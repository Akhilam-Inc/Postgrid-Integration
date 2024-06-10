frappe.listview_settings["Sales Invoice"] = {
	onload(listview){
		listview.page.add_action_item(__('Create Postgrid Letters'), function() {
				let invoice_list = []
				let selected_rec = listview.$checks.length;
				for(let row=0;row<selected_rec;row++){
					invoice_list.push(listview.$checks[row].dataset.name)
				}
				frappe.call({
					method: 'postgrid_integration.custom_scripts.py.sales_invoice.create_bulk_letter',
					args: {
						invoice_list: invoice_list,
					},
					freeze:true,
					freeze_message: __("Creating Postgrid Letters..."),
					callback: function(r){
						window.open(window.location.origin+'/app/bulk-letter-creation-tool', '_blank')
					}
				});
		})
	},
}