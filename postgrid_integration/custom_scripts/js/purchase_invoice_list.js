frappe.listview_settings["Purchase Invoice"] = {
	onload(listview){
		listview.page.add_action_item(__('Create Postgrid Cheques'), function() {
				let invoice_list = []
				let selected_rec = listview.$checks.length;
				for(let row=0;row<selected_rec;row++){
					invoice_list.push(listview.$checks[row].dataset.name)
				}
				frappe.call({
					method: 'postgrid_integration.custom_scripts.py.purchase_invoice.create_bulk_payment',
					args: {
						invoice_list: invoice_list,
					},
					freeze:true,
					freeze_message: __("Creating Postgrid Cheques..."),
					callback: function(r){
						window.open(window.location.origin+'/app/bulk-payment-creation-tool', '_blank')
					}
				});
		})
	},
}