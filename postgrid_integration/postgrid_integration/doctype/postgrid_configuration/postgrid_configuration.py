# Copyright (c) 2024, Akhilam Inc. and contributors
# For license information, please see license.txt

from datetime import datetime

import frappe
from frappe.model.document import Document
from frappe.utils import today

from postgrid_integration.constants import get_headers, get_webhook_headers
from postgrid_integration.utils import get_payload, get_payload_for_letter, send_request


class PostgridConfiguration(Document):
    def validate(self):
        doc = self.get_doc_before_save()
        if (
            (not doc and self.log_deletion_interval)
            or (doc and doc.log_deletion_interval != self.log_deletion_interval)
            or (self.log_deletion_interval and not self.last_deleted_on)
        ):
            self.last_deleted_on = today()

        if not self.log_deletion_interval:
            self.last_deleted_on = ""

        if (not doc and self.enable) or (not doc.enable and self.enable):
            webhook_list = send_request(
                frappe._dict(
                    {
                        "method": "GET",
                        "url": f"{self.postgrid_url}/print-mail/v1/webhooks",
                        "headers": get_webhook_headers(
                            postgrid_api_key=self.get_password("postgrid_api_key")
                        ),
                        "webhook": True,
                        "throw_message": "We are unable to fetch webhook list",
                    }
                ),
                webhook=True,
            )

            if webhook_list and webhook_list.get("data"):
                cheque_webhook_created = False
                letter_webhook_created = False
                for row in webhook_list.get("data"):
                    if (
                        row.get("enabled")
                        and "cheque.updated" in row.get("enabledEvents")
                        and frappe.request.origin
                        + "/api/method/postgrid_integration.api.cheque_update"
                        == row.get("url")
                    ):
                        cheque_webhook_created = True

                    if (
                        row.get("enabled")
                        and "letter.updated" in row.get("enabledEvents")
                        and frappe.request.origin
                        + "/api/method/postgrid_integration.api.letter_update"
                        == row.get("url")
                    ):
                        letter_webhook_created = True

                if not cheque_webhook_created:
                    args = frappe._dict(
                        {
                            "method": "POST",
                            "type": "Cheque",
                            "url": f"{self.postgrid_url}/print-mail/v1/webhooks",
                            "headers": get_headers(
                                postgrid_api_key=self.get_password("postgrid_api_key")
                            ),
                            "webhook": True,
                            "payload": get_payload(
                                create_webhook=True,
                                url=frappe.request.origin
                                + "/api/method/postgrid_integration.api.cheque_update",
                            ),
                            "throw_message": "We are unable to create webhook",
                        }
                    )
                    send_request(args, webhook=True)

                if not letter_webhook_created:
                    args = frappe._dict(
                        {
                            "method": "POST",
                            "type": "Letter",
                            "url": f"{self.postgrid_url}/print-mail/v1/webhooks",
                            "headers": get_headers(
                                postgrid_api_key=self.get_password("postgrid_api_key")
                            ),
                            "webhook": True,
                            "payload": get_payload_for_letter(
                                create_webhook=True,
                                url=frappe.request.origin
                                + "/api/method/postgrid_integration.api.letter_update",
                            ),
                            "throw_message": "We are unable to create webhook",
                        }
                    )
                    send_request(args, webhook=True)
