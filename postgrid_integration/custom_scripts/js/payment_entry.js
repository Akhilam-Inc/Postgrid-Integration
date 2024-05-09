frappe.ui.form.on('Payment Entry', {
	refresh: function(frm) {
		if(frm.doc.custom_postgrid_cheque_reference){
			cur_frm.dashboard.clear_headline()
			frm.set_read_only();
			frm.set_intro(
				__("This is a postgrid payment and cannot be edited it will auto submit once completed.")
			);
			frm.add_custom_button("View Cheque", function(){
				window.open(`https://dashboard.postgrid.com/dashboard/cheques/${frm.doc.custom_postgrid_cheque_reference}`, '_blank');
			});

			frm.refresh_fields()
			$(".btn.btn-primary.btn-sm.primary-action").hide();
		}
	
	}
})