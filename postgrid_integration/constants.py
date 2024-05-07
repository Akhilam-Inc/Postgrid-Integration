import frappe
from frappe.utils import get_link_to_form


doc = frappe.get_doc("Postgrid Configuration", "Postgrid Configuration")

def get_url():
	print(doc.postgrid_url)
	return doc.postgrid_url

def get_headers():
	return {
				'x-api-key': doc.get_password("postgrid_api_key"),
				'Content-Type': 'application/x-www-form-urlencoded'
			}

