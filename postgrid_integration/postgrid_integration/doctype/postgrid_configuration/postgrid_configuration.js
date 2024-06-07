// Copyright (c) 2024, Akhilam Inc. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Postgrid Configuration', {
	refresh: function(frm) {
		frm.fields_dict['postgrid_letter_format'].grid.get_field('format').get_query = function(doc, cdt, cdn) {
			var row = locals[cdt][cdn];
			if(row.doctype_name){
				return {
					filters: [
						['Print Format', 'doc_type', 'in', [row.doctype_name]]
					]
				};
			}
		};
	}
});
