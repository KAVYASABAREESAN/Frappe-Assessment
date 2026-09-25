#Query Builder
import frappe
from frappe.query_builder import DocType
from frappe.utils import today

@frappe.whitelist()
def get_overdue_returns():
    RB = DocType("Rental Booking")
    result = frappe.qb.from_(RB).select(RB.name, RB.customer_name, RB.end_date).where((RB.status == "Checked Out") & (RB.end_date < today())).orderby(RB.end_date).run(as_dict=True)
    return result

@frappe.whitelist()
def reassign_bookings(from_staff, to_staff):
    try:
        data=frappe.db.sql("""
        UPDATE `tabRental Booking`
        SET handled_by = %s
        WHERE handled_by= %s
        AND status NOT IN 
        ('Returned','Invoiced','Closed','Cancelled') 
        """,
        (to_staff,from_staff))
        frappe.db.commit()

        return {
            "success": True,
            "from_staff": from_staff,
            "to_staff": to_staff
        }

    except Exception:
        frappe.db.rollback()

        frappe.log_error(
            # frappe.get_traceback(),
            "RentFlow: Failed to reassign bookings"
        )
        raise
