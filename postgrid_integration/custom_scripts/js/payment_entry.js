frappe.ui.form.on('Payment Entry', {
	refresh(frm) {
        
        frm.add_custom_button("View Cheque", function(){
            frappe.msgprint("in view Cheque button")    
        });

        frm.add_custom_button("View Cheque PDF", function(){
            frappe.msgprint("in view cheque pdf button")    
        });
         
	}
})