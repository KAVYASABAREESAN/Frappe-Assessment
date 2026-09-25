// Copyright (c) 2026, Kavya and contributors
// For license information, please see license.txt

frappe.ui.form.on("Rental Booking", {

    setup(frm) {

        frm.set_query(
            "equipment_unit",
            "items",
            function(doc, cdt, cdn) {

                let current_row = locals[cdt][cdn];

                let selected_units = [];

                (doc.items || []).forEach(function(item) {

                    if (
                        item.name !== current_row.name &&
                        item.equipment_unit
                    ) {
                        selected_units.push(item.equipment_unit);
                    }

                });

                let filters = {
                    current_status: "Available"
                };

                if (current_row.equipment_unit) {

                    filters.name = [
                        "in",
                        selected_units.concat(
                            current_row.equipment_unit
                        )
                    ];
                }

                return {
                    filters: filters
                };
            }
        );
    },


    refresh(frm) {

        // Status indicator
        if (frm.doc.status === "Draft") {

            frm.dashboard.add_indicator(
                __("Draft"),
                "orange"
            );

        } else if (frm.doc.status === "Confirmed") {

            frm.dashboard.add_indicator(
                __("Confirmed"),
                "blue"
            );

        } else if (frm.doc.status === "Checked Out") {

            frm.dashboard.add_indicator(
                __("Checked Out"),
                "purple"
            );

        } else if (frm.doc.status === "Returned") {

            frm.dashboard.add_indicator(
                __("Returned"),
                "green"
            );

        } else if (frm.doc.status === "Invoiced") {

            frm.dashboard.add_indicator(
                __("Invoiced"),
                "blue"
            );

        } else if (frm.doc.status === "Closed") {

            frm.dashboard.add_indicator(
                __("Closed"),
                "green"
            );

        } else if (frm.doc.status === "Cancelled") {

            frm.dashboard.add_indicator(
                __("Cancelled"),
                "red"
            );
        }


        // H2 — Log Return
        if (
            frm.doc.status === "Checked Out" &&
            !frm.is_new()
        ) {

            frm.add_custom_button(
                __("Log Return"),
                function() {
                    show_return_dialog(frm);
                }
            );
        }


        // H2 — Transfer Handler
        if (!frm.is_new()) {

            frm.add_custom_button(
                __("Transfer Handler"),
                function() {
                    transfer_handler(frm);
                }
            );
        }
    },


    start_date(frm) {
        check_rental_period(frm);
    },


    end_date(frm) {
        check_rental_period(frm);
    }

});


// H1 — Rental period warning

function check_rental_period(frm) {

    if (
        !frm.doc.start_date ||
        !frm.doc.end_date
    ) {
        return;
    }

    let difference =
        frappe.datetime.get_diff(
            frm.doc.end_date,
            frm.doc.start_date
        );

    let days = difference + 1;

    if (days > 30) {

        frappe.show_alert({
            message: __(
                "Rental period is longer than 30 days."
            ),
            indicator: "orange"
        });
    }
}


// H1 — Booking Item calculation

frappe.ui.form.on("Booking Item", {

    equipment_unit(frm, cdt, cdn) {

        recompute_line_amount(
            frm,
            cdt,
            cdn
        );
    },

    line_days(frm, cdt, cdn) {

        recompute_line_amount(
            frm,
            cdt,
            cdn
        );
    }

});


function recompute_line_amount(
    frm,
    cdt,
    cdn
) {

    let row = locals[cdt][cdn];

    if (
        !row.daily_rate ||
        !row.line_days
    ) {

        frappe.model.set_value(
            cdt,
            cdn,
            "line_amount",
            0
        );

        return;
    }

    let amount =
        row.daily_rate *
        row.line_days;

    frappe.model.set_value(
        cdt,
        cdn,
        "line_amount",
        amount
    );
}


// H2 — Log Return Dialog

function show_return_dialog(frm) {

    let fields = [];

    (frm.doc.items || []).forEach(
        function(item, index) {

            fields.push({
                fieldname: "condition_" + index,
                label: item.equipment_unit,
                fieldtype: "Select",
                options: "New\nGood\nFair\nPoor\nDamaged",
                default: item.checkout_condition_grade,
                reqd: 1
            });

        }
    );


    fields.push({
        fieldname: "notes",
        label: "Notes",
        fieldtype: "Small Text",
        reqd: 0
    });


    let dialog = new frappe.ui.Dialog({

        title: __("Log Return"),

        fields: fields,

        primary_action_label: __("Submit"),

        primary_action(values) {

            let grade_dropped = false;


            (frm.doc.items || []).forEach(
                function(item, index) {

                    let returned_grade =
                        values["condition_" + index];

                    if (
                        get_condition_rank(
                            returned_grade
                        ) >
                        get_condition_rank(
                            item.checkout_condition_grade
                        )
                    ) {

                        grade_dropped = true;
                    }

                }
            );


            if (
                grade_dropped &&
                !values.notes
            ) {

                frappe.msgprint(
                    __(
                        "Notes are mandatory when any condition grade has dropped."
                    )
                );

                return;
            }


            (frm.doc.items || []).forEach(
                function(item, index) {

                    frappe.model.set_value(
                        item.doctype,
                        item.name,
                        "checkin_condition_grade",
                        values["condition_" + index]
                    );

                }
            );


            dialog.hide();

            frm.trigger("start_date");
        }
    });


    dialog.show();
}


// H2 — Condition grade ranking

function get_condition_rank(grade) {

    let grades = {
        "New": 1,
        "Good": 2,
        "Fair": 3,
        "Poor": 4,
        "Damaged": 5
    };

    return grades[grade] || 0;
}


// H2 — Transfer Handler

function transfer_handler(frm) {

    frappe.prompt(
        [
            {
                fieldname: "handled_by",
                label: "Transfer To",
                fieldtype: "Link",
                options: "Yard Staff",
                reqd: 1
            }
        ],

        function(values) {

            frappe.confirm(
                __("Transfer this booking to {0}?", [
                    values.handled_by
                ]),

                function() {

                    frappe.call({

                        method:
                            "rentflow.rentflow.doctype.rental_booking.rental_booking.transfer_handler",

                        args: {
                            booking: frm.doc.name,
                            handled_by: values.handled_by
                        }

                    });

                }
            );
        }
    );
}