import frappe


import frappe


def after_install():
    categories = [
        {
            "category_name": "Power Drill",
            "description": "Electric power drill",
            "daily_rate": 500,
            "deposit_amount": 2000
        },
        {
            "category_name": "Generator",
            "description": "Portable generator",
            "daily_rate": 1500,
            "deposit_amount": 5000
        },
        {
            "category_name": "Scaffold Tower Set",
            "description": "Scaffold tower equipment set",
            "daily_rate": 1000,
            "deposit_amount": 4000
        }
    ]

    for category in categories:
        if not frappe.db.exists(
            "Equipment Category",
            category["category_name"]
        ):
            frappe.get_doc({
                "doctype": "Equipment Category",
                **category
            }).insert(ignore_permissions=True)

    settings = frappe.get_single("RentFlow Settings")

    settings.shop_name = "RentFlow"
    settings.manager_email = frappe.session.user
    settings.default_deposit_percent = 20
    settings.damage_fee_per_grade_drop = 500
    settings.late_fee_per_day = 100
    settings.low_availability_alert_enabled = 1

    settings.save(ignore_permissions=True)

    frappe.db.commit()

    frappe.msgprint("RentFlow installation completed")