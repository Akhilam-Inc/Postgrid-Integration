import frappe
from frappe.utils import today



def create_payment_entry(args):
	doc = frappe.get_doc({
			"payment_type":"Pay",
			"posting_date": today(),
			"company": args.company,
			"mode_of_payment":"Cheque",
			"party_type":"Supplier",
			"party": args.party,
			"bank_account": args.company_bank_acc,
			"paid_amount": args.amount,
			"received_amount": args.amount,
			"paid_from": args.paid_from,
			"paid_from_account_currency": args.paid_from_account_currency,
			"paid_to": args.paid_to,
			"paid_to_account_currency": args.paid_to_account_currency,
			"doctype":"Payment Entry",
			"references":[
				{
					"reference_doctype": args.doctype,
					"reference_name": args.docname,
					"allocated_amount": args.amount,
				}
			],
			"reference_no": args.postgrid_cheque_reference,
			"reference_date": today(),
			"custom_postgrid_cheque_status": args.postgrid_cheque_status,
			"custom_postgrid_cheque_reference": args.postgrid_cheque_reference
		})

	# doc.validate()
	doc.insert(ignore_permissions=True)