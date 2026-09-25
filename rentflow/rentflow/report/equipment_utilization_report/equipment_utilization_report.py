# # Copyright (c) 2026, Kavya and contributors
# # For license information, please see license.txt

# # import frappe
# from frappe import _


# def execute(filters: dict | None = None):
# 	"""Return columns and data for the report.

# 	This is the main entry point for the report. It accepts the filters as a
# 	dictionary and should return columns and data. It is called by the framework
# 	every time the report is refreshed or a filter is updated.
# 	"""
# 	columns = get_columns()
# 	data = get_data()

# 	return columns, data

# def execute_snapshot_report(filters: dict | None = None):
# 	"""Return columns and data for the report.

# 	This is the main entry point for snapshot report. When 'Synced
# 	Report' is enabled in report, framework will call this method
# 	every time the report is refreshed or a filter is updated. It
# 	accepts the same filters as normal execute. But a utility method -
# 	get_latest_sync, is also imported.

# 	"""
# 	from frappe.database.duckdb.database import get_latest_sync

# 	columns = get_columns()
# 	data = get_data()

# 	return columns, data

# def get_columns() -> list[dict]:
# 	"""Return columns for the report.

# 	One field definition per column, just like a DocType field definition.
# 	"""
# 	return [
# 		{
# 			"label": _("Column 1"),
# 			"fieldname": "column_1",
# 			"fieldtype": "Data",
# 		},
# 		{
# 			"label": _("Column 2"),
# 			"fieldname": "column_2",
# 			"fieldtype": "Int",
# 		},
# 	]


# def get_data() -> list[list]:
# 	"""Return data for the report.

# 	The report data is a list of rows, with each row being a list of cell values.
# 	"""
# 	return [
# 		["Row 1", 1],
# 		["Row 2", 2],
# 	]
import frappe
from frappe.utils import getdate, date_diff


def execute(filters=None):
    filters = filters or {}

    columns = get_columns()
    data = get_data(filters)
    report_summary = get_report_summary(data)

    return columns, data, None, None, report_summary


def get_columns():
    return [
        {
            "label": "Category",
            "fieldname": "category",
            "fieldtype": "Link",
            "options": "Equipment Category",
            "width": 180
        },
        {
            "label": "Total Units",
            "fieldname": "total_units",
            "fieldtype": "Int",
            "width": 120
        },
        {
            "label": "Days Rented",
            "fieldname": "days_rented",
            "fieldtype": "Int",
            "width": 120
        },
        {
            "label": "Utilization %",
            "fieldname": "utilization",
            "fieldtype": "Percent",
            "width": 120
        },
        {
            "label": "Revenue",
            "fieldname": "revenue",
            "fieldtype": "Currency",
            "width": 120
        },
        {
            "label": "Damage Incidents",
            "fieldname": "damage_incidents",
            "fieldtype": "Int",
            "width": 130
        }
    ]


def get_data(filters):
    from_date = getdate(filters.get("from_date"))
    to_date = getdate(filters.get("to_date"))
    category = filters.get("category")

    equipment_filters = {
        "is_active": 1
    }

    if category:
        equipment_filters["category"] = category

    equipment_units = frappe.get_list(
        "Equipment Unit",
        filters=equipment_filters,
        fields=["name", "category"]
    )

    categories = {}

    for unit in equipment_units:
        if unit.category not in categories:
            categories[unit.category] = {
                "total_units": 0,
                "days_rented": 0,
                "revenue": 0,
                "damage_incidents": 0
            }

        categories[unit.category]["total_units"] += 1

    bookings = frappe.get_list(
        "Rental Booking",
        filters={
            "docstatus": 1
        },
        fields=[
            "name",
            "start_date",
            "end_date"
        ]
    )

    for booking in bookings:

        if not booking.start_date or not booking.end_date:
            continue

        booking_start = getdate(booking.start_date)
        booking_end = getdate(booking.end_date)

        # Skip bookings outside selected date range
        if booking_end < from_date or booking_start > to_date:
            continue

        overlap_start = max(booking_start, from_date)
        overlap_end = min(booking_end, to_date)

        rented_days = date_diff(
            overlap_end,
            overlap_start
        ) + 1

        items = frappe.get_list(
            "Booking Item",
            filters={
                "parent": booking.name
            },
            fields=[
                "equipment_unit",
                "category",
                "line_amount",
                "damage_fee"
            ]
        )

        for item in items:

            item_category = item.category

            if category and item_category != category:
                continue

            if item_category not in categories:
                continue

            categories[item_category]["days_rented"] += rented_days

            categories[item_category]["revenue"] += (
                item.line_amount or 0
            )

            if (item.damage_fee or 0) > 0:
                categories[item_category]["damage_incidents"] += 1

    data = []

    total_period_days = date_diff(
        to_date,
        from_date
    ) + 1

    for category_name, values in categories.items():

        total_units = values["total_units"]

        total_available_days = (
            total_units * total_period_days
        )

        utilization = 0

        if total_available_days > 0:
            utilization = (
                values["days_rented"]
                / total_available_days
            ) * 100

        data.append({
            "category": category_name,
            "total_units": total_units,
            "days_rented": values["days_rented"],
            "utilization": utilization,
            "revenue": values["revenue"],
            "damage_incidents": values["damage_incidents"]
        })

    return data


def get_report_summary(data):

    total_revenue = sum(
        row["revenue"]
        for row in data
    )

    total_damage_incidents = sum(
        row["damage_incidents"]
        for row in data
    )

    most_utilized = None

    if data:
        most_utilized = max(
            data,
            key=lambda row: row["utilization"]
        )["category"]

    return [
        {
            "value": total_revenue,
            "indicator": "Green",
            "label": "Total Revenue",
            "datatype": "Currency"
        },
        {
            "value": total_damage_incidents,
            "indicator": "Orange",
            "label": "Total Damage Incidents",
            "datatype": "Int"
        },
        {
            "value": most_utilized or "None",
            "indicator": "Blue",
            "label": "Most Utilized Category",
            "datatype": "Data"
        }
    ]