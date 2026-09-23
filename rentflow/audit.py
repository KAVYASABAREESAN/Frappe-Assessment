import frappe


def log_change(doc, method=None):

    if doc.doctype == "Audit Log":
        return

    audit_log = frappe.get_doc({
        "doctype": "Audit Log",
        "doctype_name": doc.doctype,
        "document_name": doc.name,
        "action": method or "unknown",
        "user": frappe.session.user,
        "timestamp": frappe.utils.now_datetime()
    })

    audit_log.insert(ignore_permissions=True)