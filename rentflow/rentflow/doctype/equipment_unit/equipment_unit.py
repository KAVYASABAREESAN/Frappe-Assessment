# Copyright (c) 2026, Kavya and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


import frappe
from frappe.model.document import Document
from frappe.model.naming import getseries


class EquipmentUnit(Document):

    def autoname(self):
        prefix = f"{self.category}"
        series = getseries(prefix, 5)
        self.name = f"{prefix[:3].upper()}-{series}"

    def on_update(self):
        threshold = frappe.db.get_value(
            "RentFlow Settings",
            None,
            "low_availability_threshold"
        )