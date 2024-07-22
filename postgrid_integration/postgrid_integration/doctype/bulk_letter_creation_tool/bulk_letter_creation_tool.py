# Copyright (c) 2024, Akhilam Inc. and contributors
# For license information, please see license.txt

import frappe, json
from frappe.model.document import Document
from postgrid_integration.api import create_postgrid_letter

class BulkLetterCreationTool(Document):
	def validate(self):
		doc = self.get_doc_before_save()
		if doc.invalid_invoices and self.invalid_invoices:
			self.invalid_invoices = ""


	@frappe.whitelist()
	def get_sales_invoice(self):
		self.items = []
		condition = ""
		total_amount = 0
		if self.from_date and not self.to_date or self.to_date and not self.from_date:
			frappe.throw("From Date and To Date are mandatory")

		if self.from_date and self.to_date:
			condition += "and posting_date BETWEEN '{0}' and '{1}'".format(self.from_date, self.to_date)

		if self.status:
			condition += "and status = '{0}'".format(self.status)

		if self.letter_status == 'Sent':
			condition += "and custom_postgrid_letter_reference is NOT NULL"
		
		if self.letter_status == 'Not Sent':
			condition += "and custom_postgrid_letter_reference is NULL"

		if si_list := frappe.db.sql("""Select name as sales_invoice,outstanding_amount as amount,status, customer, custom_postgrid_letter_reference from `tabSales Invoice`\
									where docstatus=1 and is_return=0 \
										{condition} """.format(condition=condition), as_dict=True):
			for row in si_list:
				total_amount += row["amount"]
				row.letter_status = "Not Sent"
				if row.custom_postgrid_letter_reference:
					row.letter_status = "Sent"
				self.append("items", row)
			self.total_amount = total_amount


		else:
			frappe.msgprint("No Invoice found for given filter")

		self.total_invoices = self.success_invoices = self.failed_invoices = 0
		self.save()

@frappe.whitelist()
def process_bulk_letter(invoice_list):
	success = 0
	failed = 0
	success_msg = '<span style="color: green;font-weight: bold;">Success</span>'
	failed_msg = '<span style="color: red;font-weight: bold;">Failed</span>'
	invoice_list = json.loads(invoice_list)
	total = len(invoice_list)
	for row in invoice_list:
		try:
			create_postgrid_letter(name=row.get("sales_invoice"), raise_throw=True)
			success += 1
			frappe.db.set_value("Letter Creation Item", row.get("name"), "response", success_msg)
		except Exception as e:
			frappe.log_error("process_bulk_letter", str(frappe.get_traceback()))
			frappe.db.set_value("Letter Creation Item", row.get("name"), "response", failed_msg)
			failed += 1


	frappe.set_value("Bulk Letter Creation Tool","Bulk Letter Creation Tool","total_invoices", total)
	frappe.set_value("Bulk Letter Creation Tool","Bulk Letter Creation Tool","success_invoices", success)
	frappe.set_value("Bulk Letter Creation Tool","Bulk Letter Creation Tool","failed_invoices", failed)

