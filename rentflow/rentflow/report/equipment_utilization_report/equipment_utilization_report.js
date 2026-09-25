// // Copyright (c) 2026, Kavya and contributors
// // For license information, please see license.txt

// frappe.query_reports["Equipment Utilization Report"] = {
// 	filters: [
// 		// {
// 		// 	"fieldname": "my_filter",
// 		// 	"label": __("My Filter"),
// 		// 	"fieldtype": "Data",
// 		// 	"reqd": 1,
// 		// },
// 	],
// };
frappe.query_reports["Equipment Utilization Report"] = {

    filters: [
        {
            fieldname: "from_date",
            label: "From Date",
            fieldtype: "Date",
            default: frappe.datetime.add_months(
                frappe.datetime.get_today(),
                -1
            ),
            reqd: 1
        },
        {
            fieldname: "to_date",
            label: "To Date",
            fieldtype: "Date",
            default: frappe.datetime.get_today(),
            reqd: 1
        },
        {
            fieldname: "category",
            label: "Category",
            fieldtype: "Link",
            options: "Equipment Category"
        }
    ],

    formatter: function(
        value,
        row,
        column,
        data,
        default_formatter
    ) {

        value = default_formatter(
            value,
            row,
            column,
            data
        );

        if (
            column.fieldname === "utilization" &&
            data &&
            data.utilization != null
        ) {

            if (data.utilization < 30) {
                value = `<span style="color:red">${value}</span>`;
            }

            else if (data.utilization >= 70) {
                value = `<span style="color:green">${value}</span>`;
            }
        }

        return value;
    }
};