import frappe
from frappe.utils import get_link_to_form, get_url_to_list
from frappe import _
from frappe.contacts.doctype.address.address import get_address_display

def validate_mandatory_fields(doc, throw=False):
	set_address(doc)

	mandatory_flag = False
	msg = "In Order to Create PostGrid Payment, <br><br>"
	if not doc.supplier_address:
		mandatory_flag = True
		msg += f'Supplier must have Address.<br>Setup Address for Supplier from here {get_link_to_form("Supplier", doc.supplier)}<br>'

	if not doc.billing_address:
		mandatory_flag = True
		msg += f'Company must have Billing Address.<br> Setup Address for Company from here {get_link_to_form("Company", doc.company)}<br>'
	
	if bank_acc_doc := frappe.db.get_value("Bank Account",{"is_company_account": 1,"company": doc.company, "disabled":0 }, ["name","postgrid_bank_account_id"], as_dict=1):
		if not bank_acc_doc.postgrid_bank_account_id:
			mandatory_flag = True
			msg += f'Company must have Postgrid Bank Account ID.<br> Setup Postgrid Bank Account ID for Bank Account from here {get_link_to_form("Bank Account", bank_acc_doc.name)}<br>'

	if not bank_acc_doc:
		mandatory_flag = True
		msg += f'Company must have Bank Account.<br>Setup Bank Account for Company from here <a href={get_url_to_list("Bank Account")}>Bank Account</a><br>'
		

	if throw and mandatory_flag:
		frappe.throw(msg)

	if mandatory_flag:
		frappe.msgprint(
				msg,
				title=_("Mandatory Details"),
				raise_exception=1,
				primary_action={
					"label": "Proceed Anyway",
					"server_action": "postgrid_integration.utils.proceed",
					"hide_on_success": True,
					"args":{
						"doctype": doc.doctype,
						"docname": doc.name
					}
				},
			)


@frappe.whitelist()
def before_submit(doc, method):
	print("ignore_postgrid_validation", doc.get("ignore_postgrid_validation"))
	if not doc.get("ignore_postgrid_validation"):
		validate_mandatory_fields(doc)



def set_address(doc):
	if not doc.supplier_address:
		if supplier_address := frappe.db.sql(f""" Select a.name from `tabAddress` as a JOIN `tabDynamic Link` as dl ON dl.parent=a.name
													WHERE dl.link_doctype='Supplier' and dl.link_name='{doc.supplier}' and a.disabled=0 """,as_dict=1):
			doc.db_set("supplier_address", supplier_address[0]["name"],update_modified=False)
			doc.db_set("address_display", get_address_display(frappe.get_doc("Address", supplier_address[0]["name"]).as_dict()),update_modified=False)

	if not doc.billing_address:
		if company_address := frappe.db.sql(f""" Select a.name from `tabAddress` as a JOIN `tabDynamic Link` as dl ON dl.parent=a.name
													WHERE dl.link_doctype='Company' and dl.link_name='{doc.company}' and a.disabled=0 and a.is_your_company_address=1 """,as_dict=1):
			doc.db_set("billing_address", company_address[0]["name"],update_modified=False)
			doc.db_set("billing_address_display", get_address_display(frappe.get_doc("Address", company_address[0]["name"]).as_dict()),update_modified=False)

	frappe.db.commit()

	return doc