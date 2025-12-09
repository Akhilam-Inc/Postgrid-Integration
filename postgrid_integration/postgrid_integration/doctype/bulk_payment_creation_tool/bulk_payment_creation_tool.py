# Copyright (c) 2024, Akhilam Inc. and contributors
# For license information, please see license.txt

import json

import frappe
from frappe.model.document import Document

from postgrid_integration.api import create_postgrid_payment


class BulkPaymentCreationTool(Document):
    def validate(self):
        doc = self.get_doc_before_save()
        if doc.invalid_invoices and self.invalid_invoices:
            self.invalid_invoices = ""

    @frappe.whitelist()
    def get_purchase_invoice(self):
        self.items = []
        total_amount = 0
        if not self.from_date or not self.to_date:
            frappe.throw("From Date and To Date are mandatory")

        if pi_list := frappe.db.sql(
            """Select name as purchase_invoice,outstanding_amount as amount,status from `tabPurchase Invoice`\
									 where docstatus=1 and is_return=0 and outstanding_amount>0 and custom_postgrid_cheque_reference is NULL and posting_date BETWEEN '{0}' and '{1}' """.format(
                self.from_date, self.to_date
            ),
            as_dict=True,
        ):
            for row in pi_list:
                total_amount += row["amount"]
                self.append("items", row)

            self.total_amount = total_amount
        else:
            frappe.msgprint("No Invoice found for given filter")

        self.total_invoices = self.success_invoices = self.failed_invoices = 0
        self.save()


@frappe.whitelist()
def process_bulk_payment(invoice_list):
    success = 0
    failed = 0
    success_msg = '<span style="color: green;font-weight: bold;">Success</span>'
    failed_msg = '<span style="color: red;font-weight: bold;">Failed</span>'
    invoice_list = json.loads(invoice_list)
    total = len(invoice_list)
    for row in invoice_list:
        try:
            create_postgrid_payment(name=row.get("purchase_invoice"), raise_throw=True)
            success += 1
            frappe.db.set_value(
                "Payment Creation Item", row.get("name"), "response", success_msg
            )
        except Exception:
            frappe.log_error("process_bulk_payment", str(frappe.get_traceback()))
            frappe.db.set_value(
                "Payment Creation Item", row.get("name"), "response", failed_msg
            )
            failed += 1

    frappe.set_value(
        "Bulk Payment Creation Tool",
        "Bulk Payment Creation Tool",
        "total_invoices",
        total,
    )
    frappe.set_value(
        "Bulk Payment Creation Tool",
        "Bulk Payment Creation Tool",
        "success_invoices",
        success,
    )
    frappe.set_value(
        "Bulk Payment Creation Tool",
        "Bulk Payment Creation Tool",
        "failed_invoices",
        failed,
    )
