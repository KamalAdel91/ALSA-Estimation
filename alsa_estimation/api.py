import frappe
from frappe.utils import get_fullname


@frappe.whitelist(methods=["GET"])
def ping():
	"""Foundation check: the session works and the user can read Project Estimation."""
	frappe.has_permission("Project Estimation", "read", throw=True)
	return {
		"full_name": get_fullname(frappe.session.user),
		"estimations": len(frappe.get_list("Project Estimation", pluck="name", limit_page_length=0)),
	}
