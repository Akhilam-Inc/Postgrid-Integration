// Copyright (c) 2024, Akhilam Inc. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Bulk Payment Creation Tool', {
	refresh: function(frm) {
		frm.add_custom_button("Generate Payment", function(){
			if(frm.doc.items){
				frappe.call({
					method: "postgrid_integration.postgrid_integration.doctype.bulk_payment_creation_tool.bulk_payment_creation_tool.process_bulk_payment",
					args: {
							invoice_list: cur_frm.fields_dict.items.grid.get_selected_children()
					},
					freeze: true,
					freeze_message: __("Processing Payment..."),
					callback: function (r) {
						if(r.message){
							frm.doc.total_invoices = r.message["total"]
							frm.success_invoices = r.message["message"]
							frm.failed_invoices = r.message["failed"]
							frm.refresh_fields()
						}
					},
				})
			}
			else{
				frappe.msgprint("In Order to Process Postgrid Payment Fetch the Invoices.")
			}
		});
	}
});
