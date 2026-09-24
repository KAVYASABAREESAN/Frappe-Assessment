# Copyright (c) 2026, Kavya and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class EquipmentUnit(Document):
	pass

from frappe.model.document import Document
from frappe.model.naming import getseries

class EquipmentUnit(Document):
    def autoname(self):
    # select a project name based on customer
    	prefix = f"{self.category}"
    	series = getseries(prefix, 4)
    	self.name = f"{prefix[:3]}-{series}"
	def on_update(self):
		threshold = frappe.db.get_value("RentFlow Settings", None, "low_availability_threshold")

