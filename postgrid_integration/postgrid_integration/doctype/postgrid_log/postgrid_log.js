// Copyright (c) 2024, Akhilam Inc. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Postgrid Log', {
	refresh: function(frm) {
		if(frm.doc.status == "Failure" && !frm.doc.webhook){
			if(frm.doc.type == "Cheque"){
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
			if(frm.doc.type == "Letter"){
				frm.add_custom_button("Retry", function() {
					frappe.call({
						method: "postgrid_integration.api.create_postgrid_letter",
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
	}
});
