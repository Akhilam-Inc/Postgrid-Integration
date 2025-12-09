// Copyright (c) 2024, Akhilam Inc. and contributors
// For license information, please see license.txt

frappe.ui.form.on("Bulk Payment Creation Tool", {
  refresh: function (frm) {
    if (frm.doc.invalid_invoices) {
      frappe.msgprint(frm.doc.invalid_invoices);
    }
    frm.add_custom_button("Generate Payment", function () {
      if (cur_frm.fields_dict.items.grid.get_selected_children().length == 0) {
        frappe.throw("Select any Invoice in Items Table to Generate Payment");
      }
      if (frm.doc.items) {
        frappe.call({
          method:
            "postgrid_integration.postgrid_integration.doctype.bulk_payment_creation_tool.bulk_payment_creation_tool.process_bulk_payment",
          args: {
            invoice_list:
              cur_frm.fields_dict.items.grid.get_selected_children(),
          },
          freeze: true,
          freeze_message: __("Processing Payment..."),
          callback: function (r) {},
        });
      } else {
        frappe.msgprint(
          "In Order to Process Postgrid Payment Fetch the Invoices."
        );
      }
    });
  },
});
