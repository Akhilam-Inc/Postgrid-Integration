# Copyright (c) 2024, Akhilam Inc. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class BulkPaymentCreationTool(Document):
	@frappe.whitelist()
	def get_purchase_invoice(self):
		self.items = []
		if not self.from_date or not self.to_date:
			frappe.throw("From Date and To Date are mandatory")

		if pi_list := frappe.db.sql("""Select name as purchase_invoice,outstanding_amount as amount,status from `tabPurchase Invoice`\
									 where docstatus=1 and posting_date BETWEEN '{0}' and '{1}' """.format(self.from_date, self.to_date), as_dict=True):
				for row in pi_list:
					self.append("items", row)

		else:
			frappe.msgprint("No Invoice found for given filter")

	