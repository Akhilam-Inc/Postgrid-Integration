// Copyright (c) 2024, Akhilam Inc. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Bulk Payment Creation Tool', {
	refresh: function(frm) {
		frm.add_custom_button("Generate Payment", function(){
			console.log("in button event")
		});
	}
});
