// Copyright (c) 2024, Akhilam Inc. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Bulk Letter Creation Tool', {
	refresh: function(frm) {
		if(frm.doc.invalid_invoices){
			frappe.msgprint(frm.doc.invalid_invoices)
		}
		frm.add_custom_button("Send Letter", function(){
			frappe.db.get_value("Postgrid Configuration", "Postgrid Configuration", "enable").then((res) => {
				console.log(res.message.enable)
				if(parseInt(res.message.enable)){
					if(cur_frm.fields_dict.items.grid.get_selected_children().length == 0){
						frappe.throw("Select any Invoice in Items Table to Send Letter")
					}
					if(frm.doc.items){
						frappe.call({
							method: "postgrid_integration.postgrid_integration.doctype.bulk_letter_creation_tool.bulk_letter_creation_tool.process_bulk_letter",
							args: {
									invoice_list: cur_frm.fields_dict.items.grid.get_selected_children()
							},
							freeze: true,
							freeze_message: __("Processing Letters..."),
							callback: function (r) {

							},
						})
					}
					else
						frappe.msgprint("In Order to Send Postgrid Letter Fetch the Invoices.")
				}
				else
					frappe.throw("Postgrid Integration is not enabled. Enable it in Postgrid Configuration DocType.")

			})
		});
	}
});
