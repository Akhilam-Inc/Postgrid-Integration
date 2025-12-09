frappe.ui.form.on("Sales Invoice", {
  refresh: function (frm) {
    frappe.db
      .get_value("Postgrid Configuration", "Postgrid Configuration", "enable")
      .then((res) => {
        if (parseInt(res.message.enable)) {
          if (frm.doc.docstatus == 1) {
            frm.add_custom_button("Send PostGrid Letter", function () {
              frappe.call({
                method: "postgrid_integration.api.create_postgrid_letter",
                args: {
                  name: frm.doc.name,
                },
                freeze: true,
                freeze_message: __("Processing Letter..."),
                callback: function (r) {
                  if (r.message) {
                    frm.remove_custom_button("Send PostGrid Letter");
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
