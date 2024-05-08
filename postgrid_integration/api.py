import frappe
from frappe.utils import get_link_to_form, get_url_to_list
from postgrid_integration.constants import get_headers, get_url
from postgrid_integration.utils import get_payload, send_request, create_response_log
from postgrid_integration.custom_scripts.py.payment_entry import create_payment_entry
from postgrid_integration.custom_scripts.py.purchase_invoice import validate_mandatory_fields

@frappe.whitelist()
def create_postgrid_payment(name, retry=False):
	try:
		doc = frappe.get_doc("Purchase Invoice", name)
		if doc.custom_postgrid_cheque_reference:
			frappe.throw(f'Postgrid Cheque Reference is already generated for this invoice {get_link_to_form("Purchase Invoice", doc.name)}')
		validate_mandatory_fields(doc=doc,throw=True)
		if bank_acc_doc := frappe.db.get_value("Bank Account",{"is_company_account": 1,"company": doc.company, "disabled": 0}, ["name","account","postgrid_bank_account_id"], as_dict=1):
			args = frappe._dict({
						"method" : "POST",
						"url" : f"{get_url()}/print-mail/v1/cheques",
						"headers": get_headers(),
						"payload": get_payload(doc.billing_address, doc.supplier_address, doc.company, doc.outstanding_amount, doc.name, bank_acc_doc.postgrid_bank_account_id),
						"voucher_type": doc.doctype,
						"voucher_name": doc.name,
						"throw_message": "We are unable to create postgrid payment please try again sometime"
			})

			if retry:
				args.update({
								"retry": frappe.db.get_list("Postgrid Log",{"voucher_name": doc.name}, ["sum(no_of_retry) as retry"])[0]["retry"] + 1
				})
			cheque_id, status = send_request(args)
			doc.db_set("custom_postgrid_cheque_reference", cheque_id)
			args = frappe._dict({
						"company": doc.company,
						"company_bank_acc": bank_acc_doc.name,
						"doctype": doc.doctype,
						"docname": doc.name,
						"paid_from": bank_acc_doc.account,
						"paid_from_account_currency": frappe.db.get_value("Account",bank_acc_doc.account,"account_currency"),
						"paid_to": doc.credit_to,
						"paid_to_account_currency": frappe.db.get_value("Account",doc.credit_to,"account_currency"),
						"amount": doc.outstanding_amount,
						"party": doc.supplier,
						"postgrid_cheque_reference": cheque_id,
						"postgrid_cheque_status": status


			})
			create_payment_entry(args)
			frappe.msgprint("Payment Created Successfully")
	except Exception as e:
		frappe.log_error("create_postgrid_payment", str(e))



@frappe.whitelist(allow_guest=True)
def cheque_update(**args):
	try:
		data = args["data"]
		if payment_entry := frappe.get_all("Payment Entry",{"custom_postgrid_cheque_reference": data.get("id")}, pluck="name"):
			log_name = create_response_log(frappe._dict({
							"status": "Success",
							"voucher_type": "Payment Entry",
							"voucher_name": payment_entry[0],
							"response": args,
							"webhook": 1,
							"postgrid_cheque_reference": data.get("id"),
							"postgrid_cheque_status": data.get("status"),
						}))

			frappe.db.set_value("Payment Entry", payment_entry[0], "custom_postgrid_cheque_status", data.get("status"))
			if data.get("status") == "completed":
				doc = frappe.get_doc("Payment Entry", payment_entry[0])
				doc.submit()
			if data.get("status") == "cancelled":
				frappe.delete_doc("Payment Entry", payment_entry[0], ignore_permissions=True)
				if purchase_invoice := frappe.get_all("Purchase Invoice",{"custom_postgrid_cheque_reference": data.get("id")}, pluck="name"):
					frappe.db.sql(f'Update `tabPurchase Invoice` set custom_postgrid_cheque_reference="" where name="{purchase_invoice[0]}"')

			frappe.db.commit()
	
	except Exception as e:
		frappe.log_error("cheque_update", str(e))

