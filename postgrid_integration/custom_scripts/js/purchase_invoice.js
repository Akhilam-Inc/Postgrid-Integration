frappe.ui.form.on("Purchase Invoice", {
  refresh: function (frm) {
    frappe.db
      .get_value("Postgrid Configuration", "Postgrid Configuration", "enable")
      .then((res) => {
        if (parseInt(res.message.enable)) {
          if (
            !frm.doc.custom_postgrid_cheque_reference &&
            frm.doc.docstatus == 1 &&
            frm.doc.outstanding_amount > 0
          ) {
            frm.add_custom_button("Create PostGrid Payment", function () {
              frappe.call({
                method: "postgrid_integration.api.create_postgrid_payment",
                args: {
                  name: frm.doc.name,
                },
                freeze: true,
                freeze_message: __("Processing Payment..."),
                callback: function (r) {
                  if (r.message) {
                    frm.remove_custom_button("Create PostGrid Payment");
                    frm.reload_doc();
                  }
                },
              });
            });
          }
        }
      });
  },
});
