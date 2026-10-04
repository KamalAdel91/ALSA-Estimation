"""Alerts: the Notification Logs about estimations, which also show in the desk bell, and a push to the phone
through Frappe Cloud's push relay when Push Notification Settings > Enable Push Notification Relay is on.
Who is told what, and when, is set on the desk: Notification rules on Project Estimation (System Notification)."""

from html import unescape

import frappe
import requests
from frappe import _
from frappe.utils import cint, get_url, strip_html

from alsa_estimation import APP_ROUTE, APP_TITLE
from alsa_estimation.api import DOCTYPE

# The project Frappe HR uses on the relay; the relay rejects project names it does not know.
PUSH_PROJECT = "hrms"
PAGE_LENGTH = 30


@frappe.whitelist(methods=["GET"])
def get_alerts(start=0):
	"""This user's notifications about estimations, newest first."""
	rows = frappe.get_all(
		"Notification Log",
		filters={"for_user": frappe.session.user, "document_type": DOCTYPE},
		fields=[
			"name",
			"title",
			"subject",
			"description",
			"email_content",
			"document_name",
			"read",
			"creation",
		],
		order_by="creation desc",
		start=cint(start),
		page_length=PAGE_LENGTH + 1,
	)
	alerts = [
		{
			"name": r.name,
			"title": _text(r.title or r.subject),
			"body": _text(r.description or r.email_content)[:300],
			"estimation": r.document_name,
			"read": cint(r.read),
			"when": r.creation,
		}
		for r in rows[:PAGE_LENGTH]
	]
	return {"rows": alerts, "more": len(rows) > PAGE_LENGTH}


@frappe.whitelist(methods=["GET"])
def unread_count():
	return frappe.db.count(
		"Notification Log", {"for_user": frappe.session.user, "document_type": DOCTYPE, "read": 0}
	)


@frappe.whitelist(methods=["POST"])
def mark_read(name=None):
	"""Marks one alert, or all of this user's alerts about estimations, as read."""
	filters = {"for_user": frappe.session.user, "document_type": DOCTYPE, "read": 0}
	if name:
		filters["name"] = name
	for log in frappe.get_all("Notification Log", filters=filters, pluck="name"):
		frappe.db.set_value("Notification Log", log, "read", 1, update_modified=False)
	return {"ok": True}


@frappe.whitelist(methods=["GET"])
def get_push_config():
	"""The relay's Firebase web config and VAPID key, read by the server so the browser needs no access to the relay."""
	config = frappe.cache.get_value("alsa_estimation_push_config")
	if config:
		return config
	relay = (frappe.conf.get("push_relay_server_url") or "").rstrip("/")
	if not relay:
		frappe.throw(_("The push relay is not set up on this site."))
	try:
		response = requests.get(
			f"{relay}/api/method/notification_relay.api.get_config",
			params={"project_name": PUSH_PROJECT},
			timeout=15,
		)
		response.raise_for_status()
	except requests.RequestException as e:
		frappe.throw(_("The push relay did not answer: {0}").format(e))
	payload = response.json()
	body = payload.get("message") or payload
	web = body.get("config") or {}
	config = {"config": web, "vapid": body.get("vapid_public_key") or web.get("vapid_public_key")}
	if not config["vapid"]:
		frappe.throw(_("The push relay did not return a VAPID key."))
	frappe.cache.set_value("alsa_estimation_push_config", config, expires_in_sec=86400)
	return config


def push_alert(doc, method=None):
	"""Notification Log after_insert: an alert about an estimation also goes to the user's phone."""
	if doc.document_type != DOCTYPE or not doc.for_user:
		return
	frappe.enqueue(
		"alsa_estimation.notify.send_push",
		user=doc.for_user,
		title=_text(doc.title or doc.subject) or APP_TITLE,
		body=_text(doc.description or doc.email_content),
		estimation=doc.document_name,
		enqueue_after_commit=True,
	)


def send_push(user, title, body, estimation=None):
	from frappe.push_notification import PushNotification

	push = PushNotification(PUSH_PROJECT)
	if not push.is_enabled():
		return
	route = f"/{APP_ROUTE}/estimation/{estimation}" if estimation else f"/{APP_ROUTE}"
	try:
		push.send_notification_to_user(
			user,
			title,
			body or title,
			link=get_url(route),
			data={"title": title, "body": body or title, "tag": estimation or ""},
		)
	except Exception:
		frappe.log_error(title="ALSA Estimation: push notification failed")


def _text(value):
	return unescape(strip_html(value or "")).strip()
