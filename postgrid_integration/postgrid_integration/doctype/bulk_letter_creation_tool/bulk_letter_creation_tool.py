# Copyright (c) 2024, Akhilam Inc. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class BulkLetterCreationTool(Document):
	def validate(self):
		doc = self.get_doc_before_save()
		if doc.invalid_invoices and self.invalid_invoices:
			self.invalid_invoices = ""


	@frappe.whitelist()
	def get_sales_invoice(self):
		self.items = []
		if not self.from_date or not self.to_date:
			frappe.throw("From Date and To Date are mandatory")

		if si_list := frappe.db.sql("""Select name as sales_invoice,outstanding_amount as amount,status from `tabSales Invoice`\
									 where docstatus=1 and is_return=0 and custom_postgrid_letter_reference is NULL\
									and posting_date BETWEEN '{0}' and '{1}' """.format(self.from_date, self.to_date), as_dict=True):
			for row in si_list:
				self.append("items", row)


		else:
			frappe.msgprint("No Invoice found for given filter")

		self.total_invoices = self.success_invoices = self.failed_invoices = 0
		self.save()
