import frappe
from frappe import _
from frappe.utils import get_fullname

from alsa_estimation import APP_ROUTE, APP_TITLE

no_cache = 1


def get_context(context):
	if frappe.session.user == "Guest":
		frappe.local.flags.redirect_location = f"/login?redirect-to=/{APP_ROUTE}"
		raise frappe.Redirect

	if not frappe.has_permission("Project Estimation", "read"):
		frappe.throw(_("You are not permitted to open {0}.").format(APP_TITLE), frappe.PermissionError)

	context.csrf_token = frappe.sessions.get_csrf_token()
	# A GET request does not commit on its own; the new CSRF token must be saved with the session.
	frappe.db.commit()  # nosemgrep

	boot = {
		"route": APP_ROUTE,
		"title": APP_TITLE,
		"user": frappe.session.user,
		"full_name": get_fullname(frappe.session.user),
	}
	context.boot = frappe.as_json(boot, indent=None).replace("</", "<\\/")
	context.title = APP_TITLE
	return context
