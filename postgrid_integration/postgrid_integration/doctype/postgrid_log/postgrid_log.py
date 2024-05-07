# Copyright (c) 2024, Akhilam Inc. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import today
from datetime import datetime

class PostgridLog(Document):
	pass


def delete_postgrid_log():
	postgrid_conf = frappe.db.get_value("Postgrid Configuration", "Postgrid Configuration", ["log_deletion_interval","last_deleted_on"], as_dict=True)
	if postgrid_conf["last_deleted_on"] and postgrid_conf["log_deletion_interval"]:
		last_updated_date = datetime.strptime(postgrid_conf["last_deleted_on"], '%Y-%m-%d')
		today_date = datetime.strptime(today(), '%Y-%m-%d')
		if int((last_updated_date - today_date).days) == int(postgrid_conf["log_deletion_interval"]):
			frappe.db.sql("""Delete from `tabPostgrid Log` """)
			frappe.db.set_value("Postgrid Configuration", "Postgrid Configuration", "last_deleted_on", today())
			frappe.db.commit()
