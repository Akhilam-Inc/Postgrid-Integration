import json

import frappe
from frappe import _
from frappe.contacts.doctype.address.address import get_address_display
from frappe.utils import get_link_to_form

from postgrid_integration.constants import is_postgrid_enabled
from postgrid_integration.utils import check_print_format_mapped


def validate_mandatory_fields(doc, throw=False, raise_throw=False):
    set_address(doc)

    mandatory_flag = False
    msg = "In Order to Create PostGrid Letter, <br><br>"
    if not doc.customer_address:
        mandatory_flag = True
        msg += f'Customer must have Address.<br>Setup Address for Customer from here {get_link_to_form("Customer", doc.customer)}<br>'

    if not doc.company_address:
        mandatory_flag = True
        msg += f'Company must have Billing Address.<br> Setup Address for Company from here {get_link_to_form("Company", doc.company)}<br>'

    if print_format_details := check_print_format_mapped(doc.doctype):
        if not print_format_details[0]:
            mandatory_flag = True
            msg += f'Kindly map the respective print format for {doc.doctype}.<br> Map Pirnt Format for {doc.doctype} from here {get_link_to_form("Postgrid Configuration", "Postgrid Configuration")}<br>'

    if raise_throw and mandatory_flag:
        raise Exception(msg)

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
                "args": {"doctype": doc.doctype, "docname": doc.name},
            },
        )


@frappe.whitelist()
def before_submit(doc, method):
    if is_postgrid_enabled() and not doc.get("ignore_postgrid_validation"):
        validate_mandatory_fields(doc)


def set_address(doc):
    if not doc.customer_address:
        if customer_address := frappe.db.sql(
            f""" Select a.name from `tabAddress` as a JOIN `tabDynamic Link` as dl ON dl.parent=a.name
													WHERE dl.link_doctype='Customer' and dl.link_name='{doc.customer}' and a.disabled=0 """,
            as_dict=1,
        ):
            doc.db_set(
                "customer_address", customer_address[0]["name"], update_modified=False
            )
            doc.db_set(
                "address_display",
                get_address_display(
                    frappe.get_doc("Address", customer_address[0]["name"]).as_dict()
                ),
                update_modified=False,
            )

    if not doc.company_address:
        if company_address := frappe.db.sql(
            f""" Select a.name from `tabAddress` as a JOIN `tabDynamic Link` as dl ON dl.parent=a.name
													WHERE dl.link_doctype='Company' and dl.link_name='{doc.company}' and a.disabled=0 and a.is_your_company_address=1 """,
            as_dict=1,
        ):
            doc.db_set(
                "company_address", company_address[0]["name"], update_modified=False
            )
            doc.db_set(
                "company_address_display",
                get_address_display(
                    frappe.get_doc("Address", company_address[0]["name"]).as_dict()
                ),
                update_modified=False,
            )

    frappe.db.commit()

    return doc


@frappe.whitelist()
def create_bulk_letter(invoice_list):
    pi_path = frappe.request.origin + "/app/sales-invoice/"
    invoice_list = json.loads(invoice_list)
    bulk_payment_doc = frappe.get_doc("Bulk Letter Creation Tool")
    bulk_payment_doc.db_set("invalid_invoices", "")
    bulk_payment_doc.items = []
    bulk_payment_doc.from_date = bulk_payment_doc.to_date = ""
    total_amount = 0
    invalid_invoices = []
    for row in invoice_list:
        invoice_details = frappe.get_all(
            "Sales Invoice",
            {"name": row},
            [
                "custom_postgrid_letter_reference",
                "docstatus",
                "customer",
                "status",
                "outstanding_amount",
            ],
        )[0]
        if invoice_details.docstatus == 1:
            bulk_payment_doc.append(
                "items",
                {
                    "sales_invoice": row,
                    "status": invoice_details.status,
                    "amount": invoice_details.outstanding_amount,
                    "customer": invoice_details.customer,
                    "letter_status": "Sent"
                    if invoice_details.custom_postgrid_letter_reference
                    else "Not Sent",
                },
            )
            total_amount += invoice_details.outstanding_amount
        else:
            invalid_invoices.append(f"<br><a href='{pi_path+row}'>{row}</a>")

    bulk_payment_doc.total_amount = total_amount

    if not bulk_payment_doc.items:
        frappe.throw(
            "The chosen records didn't meet the necessary criteria to send postgrid letters."
        )

    if invalid_invoices:
        msg = "Below records didn't meet the necessary criteria tosend postgrid letters.<br>"
        msg += ", ".join(invalid_invoices)
        bulk_payment_doc.invalid_invoices = msg

    bulk_payment_doc.save(ignore_permissions=True)
