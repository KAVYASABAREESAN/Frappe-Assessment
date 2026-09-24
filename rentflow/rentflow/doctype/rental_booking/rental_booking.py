# Copyright (c) 2026, Kavya and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class RentalBooking(Document):

    def validate(self):

        # if self.age <= 18:
        #     frappe.throw("Person's age must be at least 18")

        rental_total = 0
        damage_total = 0

        if self.start_date > self.end_date:
            frappe.throw("Start date must be less than end date")

        for item in self.items:

            item.line_days = (self.end_date - self.start_date).days + 1
            item.line_amount = item.daily_rate * item.line_days

            rental_total += item.line_amount

            item.damage_fee = 0

            if item.checkin_condition_grade and item.checkout_condition_grade:

                grades = {
                    "New": 1,
                    "Good": 2,
                    "Fair": 3,
                    "Poor": 4,
                    "Damaged": 5
                }

                checkin_grade = grades[item.checkin_condition_grade]
                checkout_grade = grades[item.checkout_condition_grade]

                if checkin_grade > checkout_grade:

                    settings = frappe.get_single(
                        "RentFlow Settings"
                    )

                    item.damage_fee = (
                        settings.damage_fee_per_grade_drop
                        * (checkin_grade - checkout_grade)
                    )

            damage_total += item.damage_fee or 0

        self.rental_total = rental_total
        self.damage_total = damage_total
        self.final_amount = self.rental_total + self.damage_total

        self.validate_equipment_overlap()


    def validate_equipment_overlap(self):

        for item in self.items:

            if not item.equipment_unit:
                continue

            conflicts = frappe.db.sql(
                """
                SELECT rb.name
                FROM `tabRental Booking` rb
                INNER JOIN `tabBooking Item` bi
                    ON bi.parent = rb.name
                WHERE rb.name != %s
                  AND rb.docstatus = 1
                  AND rb.status NOT IN ('Cancelled', 'Returned')
                  AND bi.equipment_unit = %s
                  AND rb.start_date <= %s
                  AND rb.end_date >= %s
                LIMIT 1
                """,
                (
                    self.name,
                    item.equipment_unit,
                    self.end_date,
                    self.start_date,
                ),
                as_dict=True,
            )

            if conflicts:

                frappe.throw(
                    f"Equipment Unit {item.equipment_unit} "
                    f"is already booked in "
                    f"Rental Booking {conflicts[0].name}."
                )


    def before_submit(self):

        if self.status != "Confirmed":
            frappe.throw(
                "Confirm the booking before submitting"
            )

        if self.deposit_collected <= 0:
            frappe.throw(
                "Deposit collected must be greater than 0"
            )

        self.validate_equipment_overlap()


    def on_submit(self):

        for item in self.items:

            frappe.db.set_value(
                "Equipment Unit",
                item.equipment_unit,
                "current_status",
                "Reserved",
                ignore_permissions=True
            )


    def on_cancel(self):

        self.status = "Cancelled"

        for item in self.items:

            frappe.db.set_value(
                "Equipment Unit",
                item.equipment_unit,
                "current_status",
                "Available",
                ignore_permissions=True
            )


    def on_trash(self):

        if self.status not in ["Cancelled", "Draft"]:

            frappe.throw(
                "Only Draft or Cancelled bookings can be deleted."
            )