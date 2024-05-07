import frappe
from frappe.utils import get_link_to_form, get_url_to_list
from postgrid_integration.constants import get_headers, get_url
from postgrid_integration.utils import get_payload, send_request
from postgrid_integration.custom_scripts.py.payment_entry import create_payment_entry
from postgrid_integration.custom_scripts.py.purchase_invoice import validate_mandatory_fields


@frappe.whitelist()
def create_postgrid_payment(name, retry=False):
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



@frappe.whitelist(allow_guest=True)
def cheque_update(**args):
	frappe.log_error(str(args), "cheque_update")