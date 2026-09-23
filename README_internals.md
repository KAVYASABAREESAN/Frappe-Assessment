C3 — Booking Item & Rental Invoice
        When a doctype is updated all the other doctype linked to it also gets updated as Frappe stores the reference to the doctype and hence when Yard Staff doctype is renamed the handled_by field on Rental Bookings is also updated 

B3 — Dangerous Patterns

    def validate(self):
        self.rental_total = sum(r.line_amount for r in self.items)
        self.save()
        unit = frappe.get_doc("Equipment Unit", self.items[0].equipment_unit)
        unit.current_status = "Rented"
        unit.save()

    BUG 1 : self.save() inside validate()
        validate() is called by self.save() and hence it leads to recursion error
        validate()->self.save()->validate()->self.save() and so on

    BUG 2:  The unit current_status is being updated only for self.items[0]
        As in the code it is mentioned 
        ```unit = frappe.get_doc("Equipment Unit", self.items[0].equipment_unit)
        unit.current_status = "Rented"
        unit.save()```
        only the status of items[0] gets updated

    CORRECTED CODE:
    def validate(self):
        self.rental_total = sum(r.line_amount for r in self.items)
        for row in self.items():
            unit = frappe.get_doc("Equipment Unit", row.equipment_unit)
            unit.current_status = "Rented"
            unit.save()

B4 — Concurrency, One Question
    why would two staff members confirming the same booking at once trigger a "Document has been modified after you have opened it" error, and how does Frappe prevent the silent overwrite?

    ANSWER:When 2 staff members confirm the same booking at once, we get an error,
    it is because the frappe tracks the timestamp of the users opening a document and updating it, so if the timestamp of the document getting updated is later than the document opened timestamp it shows the error, in order to notfiy the updation and alos to prevent overriding
     