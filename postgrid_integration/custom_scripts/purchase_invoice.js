frappe.ui.form.on('Purchase Invoice', {
	refresh(frm) {
        if(!frm.doc.custom_postgrid_cheque_reference){
            frm.add_custom_button("Create PostGrid Payment", function(){
                frappe.msgprint("in Button")    
            });
        }    
	}
})