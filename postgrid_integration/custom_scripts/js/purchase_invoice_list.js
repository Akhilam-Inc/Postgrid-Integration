const custom_erpnext_onload =
  frappe.listview_settings["Purchase Invoice"].onload;

frappe.listview_settings["Purchase Invoice"].onload = function (list_view) {
  if (custom_erpnext_onload) {
    custom_erpnext_onload(list_view);
  }
  list_view.page.add_action_item(__("Create Postgrid Cheques"), function () {
    let selected_rows = [];
    if (cur_list.view == "Report") {
      const visible_idx = cur_list.datatable.rowmanager
        .getCheckedRows()
        .map((i) => Number(i));
      if (visible_idx.length == 0) {
        frappe.throw("Please Select a row for Make Record");
      }
      let indexes = cur_list.datatable.rowmanager.getCheckedRows();

      for (const element of indexes) {
        selected_rows.push(cur_list.data[element].name);
      }
    }
    if (cur_list.view == "List") {
      let selected_rec = list_view.$checks.length;
      for (let row = 0; row < selected_rec; row++) {
        selected_rows.push(list_view.$checks[row].dataset.name);
      }
    }
    frappe.call({
      method:
        "postgrid_integration.custom_scripts.py.purchase_invoice.create_bulk_payment",
      args: {
        invoice_list: selected_rows,
      },
      freeze: true,
      freeze_message: __("Creating Postgrid Cheques..."),
      callback: function (r) {
        window.open(
          window.location.origin + "/app/bulk-payment-creation-tool",
          "_blank"
        );
      },
    });
  });
};
