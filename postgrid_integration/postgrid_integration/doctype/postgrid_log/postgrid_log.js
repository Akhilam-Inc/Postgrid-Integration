// Copyright (c) 2024, Akhilam Inc. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Postgrid Log', {
	refresh: function(frm) {
		if(frm.doc.status == "Failure"){
			frm.add_custom_button("Retry", function() {
				frappe.call({
					method: "postgrid_integration.api.create_postgrid_payment",
					args: {
						name: frm.doc.voucher_name,
						retry: true,
					},
					callback: function (r) {
					
					},
				})
			})
		}
	}
});
