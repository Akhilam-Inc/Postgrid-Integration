# Copyright (c) 2024, Akhilam Inc. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from datetime import datetime
from frappe.utils import today

class PostgridConfiguration(Document):
	def validate(self):
		doc = self.get_doc_before_save()
		if (not doc and self.log_deletion_interval) or (doc and doc.log_deletion_interval != self.log_deletion_interval)\
			or (self.log_deletion_interval and not self.last_deleted_on):
			
			self.last_deleted_on = today()

		if not self.log_deletion_interval:
			self.last_deleted_on = ""
