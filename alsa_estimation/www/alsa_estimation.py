import os
from urllib.parse import quote, unquote

import frappe
from frappe import _
from frappe.utils import cint, get_fullname

from alsa_estimation import APP_ROUTE, APP_TITLE
from alsa_estimation.branding import app_logo, company_logo

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
		"full_name": _employee_name() or get_fullname(frappe.session.user),
		"user_image": _url(frappe.db.get_value("User", frappe.session.user, "user_image")),
		"company": _company(),
		"logo": _url(_logo()),
		"push": bool(frappe.conf.get("push_relay_server_url"))
		and bool(
			cint(frappe.db.get_single_value("Push Notification Settings", "enable_push_notification_relay"))
		),
	}
	context.boot = frappe.as_json(boot, indent=None).replace("</", "<\\/")
	context.title = APP_TITLE
	return context


def _employee_name():
	"""The name on the user's Employee record, when the user is linked to one."""
	if not frappe.db.exists("DocType", "Employee"):
		return None
	return frappe.db.get_value("Employee", {"user_id": frappe.session.user, "status": "Active"}, "employee_name")


def _company():
	return frappe.defaults.get_user_default("Company") or frappe.db.get_single_value(
		"Global Defaults", "default_company"
	)


def _url(path):
	"""File paths can hold spaces; encode them so the browser can load the image."""
	return quote(path, safe="/:?=&%#") if path else None


def _logo():
	"""The first logo whose file is on this site; a restored database can point to files that were not copied."""
	for url in (
		frappe.db.get_single_value("Navbar Settings", "app_logo"),
		company_logo(),
		app_logo(),
		frappe.db.get_value("Company", {"company_logo": ["is", "set"]}, "company_logo"),
	):
		if url and _file_exists(url):
			return url
	return None


def _file_exists(url):
	if url.startswith(("http://", "https://")):
		return True
	path = unquote(url.split("?")[0])
	for prefix, folder in (("/private/files/", "private"), ("/files/", "public")):
		if path.startswith(prefix):
			return os.path.exists(frappe.get_site_path(folder, "files", path[len(prefix):]))
	return True
