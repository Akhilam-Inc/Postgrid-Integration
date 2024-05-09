import frappe
from frappe.utils import get_link_to_form


def get_url():
	doc = frappe.get_doc("Postgrid Configuration", "Postgrid Configuration")
	return doc.postgrid_url

def get_headers(postgrid_api_key=None):
	doc = frappe.get_doc("Postgrid Configuration", "Postgrid Configuration")
	return {
				'x-api-key': postgrid_api_key or doc.get_password("postgrid_api_key"),
				'Content-Type': 'application/x-www-form-urlencoded'
			}

def get_webhook_headers():
	doc = frappe.get_doc("Postgrid Configuration", "Postgrid Configuration")
	return {
				'x-api-key': doc.get_password("postgrid_api_key"),
				
			}

