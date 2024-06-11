import frappe, json
from datetime import datetime
from frappe import _
import requests
from frappe.utils import get_link_to_form
from urllib.parse import quote


@frappe.whitelist()
def check_print_format_mapped(doctype):
	mapped = False
	print_format_details = []
	if letter_format := frappe.get_all("Postgrid Letter Format", {"doctype_name": doctype, "parent": "Postgrid Configuration"}, ["format", "letterhead"]):
		mapped = True
		print_format_details.append(letter_format[0]["format"])
		print_format_details.append(letter_format[0]["letterhead"])

	return mapped, print_format_details

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
							"type": log_details.type,
							"payload": log_details.get("payload") or "",
							"voucher_type": log_details.get("voucher_type"),
							"voucher_name": log_details.get("voucher_name"),
							"response": json.dumps(log_details.get("response"), indent=4),
							"no_of_retry": log_details.get("retry") or 0,
							"postgrid_cheque_reference": log_details.get("postgrid_cheque_reference"),
							"postgrid_cheque_status": log_details.get("postgrid_cheque_status"),
							"postgrid_letter_reference": log_details.get("postgrid_letter_reference"),
							"postgrid_letter_status": log_details.get("postgrid_letter_status"),
							"webhook": log_details.get("webhook") or 0,

	}).insert(ignore_permissions=True)
	frappe.db.commit()
	return log.name

def send_request(args, webhook=False, raise_throw=False):
	response = requests.request(args.method, args.url, headers=args.headers, data=args.payload)
	data = frappe._dict(json.loads(response.text))
	log_name = create_response_log(frappe._dict({
							"status": "Success" if response.ok else "Failure",
							"type": args.type,
							"payload": args.payload,
							"voucher_type": args.get("voucher_type") or "",
							"voucher_name": args.get("voucher_name") or "",
							"response": json.loads(response.text),
							"retry": args.get("retry") or 0,
							"postgrid_cheque_reference" if "cheque" in args.url else "postgrid_letter_reference": data.id if response.ok and not webhook else "",
							"postgrid_cheque_status" if "cheque" in args.url else "postgrid_letter_status": data.status if response.ok and not webhook else "",
							"webhook": args.get("webhook") or 0,

	}))

	if webhook and response.ok:
		return data

	if response.ok and not webhook:
		return data.get("id"), data.get("status")

	else:
		if raise_throw:
			raise Exception(args.get("throw_message"))
		if not webhook:
			frappe.throw(args.get("throw_message") or data.get("error").get("message"))
		frappe.msgprint(args.get("throw_message"))



def get_payload(company_address=None, vendor_address=None, company=None, amount=None, name=None, bill_no=None,postgrid_bank_account_id=None, create_webhook=False, url=None):
	try:
		if create_webhook:
			return f'enabled=true&\
					url={quote(url)}&\
					enabledEvents%5B%5D=cheque.updated\
					&description=Cheque%20Updated\
					&payloadFormat=json'.replace('\t', '')

		company_address_doc = frappe.get_doc("Address", company_address)
		vendor_address_doc = frappe.get_doc("Address", vendor_address)
		company_doc = frappe.get_doc("Company", company)

		
		# memo = f'Payment for {name}'
		memo = f'Payment for {bill_no}'
		description = f'{name}'


		logo = url+company_doc.company_logo if company_doc.company_logo else ""
		payload = f'from%5BcompanyName%5D={quote(company)}&\
					from%5BaddressLine1%5D={quote(company_address_doc.address_line1 or "")}&\
					from%5BaddressLine2%5D={quote(company_address_doc.address_line2 or "")}&\
					from%5Bcity%5D={quote(company_address_doc.city or "")}&\
					from%5BprovinceOrState%5D={quote(company_address_doc.state or "")}&\
					from%5BcountryCode%5D={quote(frappe.get_value("Country",company_address_doc.country, "code") or "")}&\
					from%5BpostalOrZip%5D={quote(company_address_doc.pincode or "")}&\
					to%5BcompanyName%5D={quote(vendor_address_doc.address_title or "")}&\
					to%5BaddressLine1%5D={quote(vendor_address_doc.address_line1 or "")}&\
					to%5BaddressLine2%5D={quote(vendor_address_doc.address_line2 or "")}&\
					to%5Bcity%5D={quote(vendor_address_doc.city or "")}&\
					to%5BprovinceOrState%5D={quote(vendor_address_doc.state or "")}&\
					to%5BcountryCode%5D={quote(frappe.get_value("Country",vendor_address_doc.country, "code") or "")}&\
					to%5BpostalOrZip%5D={quote(vendor_address_doc.pincode or "")}&\
					description={quote(description)}&\
					bankAccount={quote(postgrid_bank_account_id)}&\
					amount={amount*100}&\
					memo={quote(memo)}&\
					logo={quote(logo)}'

		return payload.replace('\t', '')
	
	except Exception as e:
		frappe.log_error("Payload"+postgrid_bank_account_id, frappe.get_traceback())

def get_payload_for_letter(company_address=None, vendor_address=None, company=None, name=None, pdf_link=None, create_webhook=False, url=None):
	try:
		if create_webhook:
			return f'enabled=true&\
					url={quote(url)}&\
					enabledEvents%5B%5D=letter.updated\
					&description=Letter%20Updated\
					&payloadFormat=json'.replace('\t', '')

		company_address_doc = frappe.get_doc("Address", company_address)
		vendor_address_doc = frappe.get_doc("Address", vendor_address)




		payload = f'from%5BcompanyName%5D={quote(company)}&\
					from%5BaddressLine1%5D={quote(company_address_doc.address_line1 or "")}&\
					from%5BaddressLine2%5D={quote(company_address_doc.address_line2 or "")}&\
					from%5Bcity%5D={quote(company_address_doc.city or "")}&\
					from%5BprovinceOrState%5D={quote(company_address_doc.state or "")}&\
					from%5BcountryCode%5D={quote(frappe.get_value("Country",company_address_doc.country, "code") or "")}&\
					from%5BpostalOrZip%5D={quote(company_address_doc.pincode or "")}&\
					to%5BcompanyName%5D={quote(vendor_address_doc.address_title or "")}&\
					to%5BaddressLine1%5D={quote(vendor_address_doc.address_line1 or "")}&\
					to%5BaddressLine2%5D={quote(vendor_address_doc.address_line2 or "")}&\
					to%5Bcity%5D={quote(vendor_address_doc.city or "")}&\
					to%5BprovinceOrState%5D={quote(vendor_address_doc.state or "")}&\
					to%5BcountryCode%5D={quote(frappe.get_value("Country",vendor_address_doc.country, "code") or "")}&\
					to%5BpostalOrZip%5D={quote(vendor_address_doc.pincode or "")}&\
					pdf={quote(pdf_link, safe="")}&\
					addressPlacement=insert_blank_page&\
					color=true&\
					size=us_letter'

		return payload.replace('\t', '')
	
	except Exception as e:
		frappe.log_error(f"Letter Payload {name}", frappe.get_traceback())

@frappe.whitelist()
def upload_file(doctype, name, print_format, letterhead=None, fieldname=None):
	doc = frappe.get_doc(doctype, name)
	from frappe.translate import print_language
	with print_language("en"):
		pdf_file = frappe.get_print(
			doctype, name, print_format, doc=doc, as_pdf=True, letterhead=letterhead, no_letterhead= 0 if letterhead else 1
		)
	file_doc = frappe.get_doc(
			{
				"doctype": "File",
				"attached_to_doctype": doctype,
				"attached_to_name": name,
				"file_name": name,
				"is_private": 0,
				"content": pdf_file,
			}
	).save(ignore_permissions=True)

	if fieldname:
		doc.db_set(fieldname, file_doc.name)

	return file_doc


def get_pdf_link(doc, fieldname, url):
	print_format_details = frappe.get_all("Postgrid Letter Format", {"doctype_name": doc.doctype, "parent": "Postgrid Configuration"}, ["format", "letterhead"])

	if not doc.get(fieldname):
		file_doc = upload_file(doctype=doc.doctype, name=doc.name, print_format=print_format_details[0]["format"], letterhead=print_format_details[0]["letterhead"], fieldname=fieldname)

	elif not frappe.db.exists("File", doc.get(fieldname)):
		file_doc = upload_file(doctype=doc.doctype, name=doc.name, print_format=print_format_details[0]["format"], letterhead=print_format_details[0]["letterhead"], fieldname=fieldname)

	else:
		file_doc = frappe.get_doc("File", doc.get(fieldname))

	pdf_link = url + file_doc.file_url

	return pdf_link