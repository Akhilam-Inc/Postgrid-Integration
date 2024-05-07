import frappe, json
from datetime import datetime
from frappe import _
import requests
from frappe.utils import get_link_to_form
from urllib.parse import quote


@frappe.whitelist()
def proceed(args):
	if isinstance(args, str):
		args = frappe._dict(json.loads(args))
	doc = frappe.get_doc(args.doctype, args.docname)
	doc.ignore_postgrid_validation = True
	doc.submit()
	frappe.msgprint("Submitted Successfully!")



def create_response_log(log_details):
	log = frappe.get_doc({
							"doctype": "Postgrid Log",
							"status": log_details.status,
							"payload": log_details.payload,
							"voucher_type": log_details.get("voucher_type"),
							"voucher_name": log_details.get("voucher_name"),
							"response": json.dumps(log_details.get("response"), indent=4),
							"no_of_retry": log_details.get("retry") or 0,
							"postgrid_cheque_reference": log_details.get("postgrid_cheque_reference"),
							"postgrid_cheque_status": log_details.get("postgrid_cheque_status"),

	}).insert()
	frappe.db.commit()
	return log.name

def send_request(args):
	response = requests.request(args.method, args.url, headers=args.headers, data=args.payload)
	data = frappe._dict(json.loads(response.text))
	log_name = create_response_log(frappe._dict({
							"status": "Success" if response.ok else "Failure",
							"payload": args.payload,
							"voucher_type": args.get("voucher_type") or "",
							"voucher_name": args.get("voucher_name") or "",
							"response": json.loads(response.text),
							"retry": args.get("retry") or 0,
							"postgrid_cheque_reference": data.id if response.ok else "",
							"postgrid_cheque_status": data.status if response.ok else "",
	}))
	if response.ok:
		return data.id, data.status

	else:
		frappe.throw(args.get("throw_message") or data.get("error").get("message"))



def get_payload(company_address, vendor_address, company, amount, name, postgrid_bank_account_id):
	company_address_doc = frappe.get_doc("Address", company_address)
	vendor_address_doc = frappe.get_doc("Address", vendor_address)

	memo = f'Payment for {name}'
	payload = f'from%5BcompanyName%5D={quote(company)}&\
				from%5BaddressLine1%5D={quote(company_address_doc.address_line1 or "")}&\
				from%5BaddressLine2%5D={quote(company_address_doc.address_line2 or "")}&\
				from%5Bcity%5D={quote(company_address_doc.city or "")}&\
				from%5BprovinceOrState%5D={quote(company_address_doc.state or "")}&\
				from%5BpostalOrZip%5D={quote(company_address_doc.pincode or "")}\
				&to%5BcompanyName%5D={quote(vendor_address_doc.address_title or "")}&\
				to%5BaddressLine1%5D={quote(company_address_doc.address_line1 or "")}&\
				to%5BaddressLine2%5D={quote(company_address_doc.address_line2 or "")}\
				to%5Bcity%5D={quote(company_address_doc.city or "")}&\
				to%5BprovinceOrState%5D={quote(company_address_doc.state or "")}&\
				to%5BpostalOrZip%5D={quote(company_address_doc.pincode or "")}&\
				description=Test&\
				bankAccount={quote(postgrid_bank_account_id)}&\
				amount={amount}&\
				memo={quote(memo)}'

	return payload.replace('\t', '')