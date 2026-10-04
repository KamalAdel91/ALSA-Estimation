"""Changes from the app. Each one ends with the same save as the desk, so every stored total is recalculated."""

import frappe
from frappe import _
from frappe.utils import cint, flt
from nexlify_budget_control.nexlify_budget_control.budget_enforcement import update_project_equipment_scope

from alsa_estimation.api import DOCTYPE, _can_edit, _workflow_states
from alsa_estimation.estimation import _trade_colors


@frappe.whitelist(methods=["GET"])
def get_trades():
	"""Enabled Manpower Categories in their sort order, with the color each one has on the desk."""
	frappe.has_permission(DOCTYPE, "read", throw=True)
	enabled = set(frappe.get_all("Manpower Category", filters={"enabled": 1}, pluck="name"))
	return [{"name": trade, "dot": dot} for trade, dot in _trade_colors().items() if trade in enabled]


@frappe.whitelist(methods=["POST"])
def save_scope(name, scope, days_per_equipment, roles, modified=None):
	"""The days and crew of one equipment; then the estimation is saved so its totals follow."""
	doc = _editable(name, modified)
	row = frappe.get_doc("Project Equipment Scope", scope)
	if row.cost_budget != doc.name:
		frappe.throw(_("This equipment belongs to another estimation."))
	crew = [
		{"trade": r.get("trade"), "count": cint(r.get("count"))}
		for r in frappe.parse_json(roles) or []
		if r.get("trade") and cint(r.get("count")) > 0
	]
	update_project_equipment_scope(
		scope,
		{
			"equipment": row.equipment,
			"quantity": row.quantity,
			"days_per_equipment": flt(days_per_equipment),
			"roles": crew,
		},
	)
	doc.reload()
	doc.save()
	return {"modified": doc.modified}


@frappe.whitelist(methods=["POST"])
def save_rates(name, working_days_per_month, rows, modified=None):
	"""Working days per month, and the basic salary and factor of each trade in Team Daily Rates."""
	doc = _editable(name, modified)
	values = {r.get("designation"): r for r in frappe.parse_json(rows) or []}
	if cint(working_days_per_month) > 0:
		doc.working_days_per_month = cint(working_days_per_month)
	for r in doc.team_rates or []:
		if r.designation in values:
			r.basic_salary = flt(values[r.designation].get("basic_salary"))
			r.factor = flt(values[r.designation].get("factor"))
	doc.save()
	return {"modified": doc.modified}


@frappe.whitelist(methods=["POST"])
def save_margin(name, margin_percentage, modified=None):
	"""The margin is a permlevel 1 field: only users who may write prices can change it."""
	doc = _editable(name, modified)
	if 1 not in frappe.get_meta(DOCTYPE).get_permlevel_access("write"):
		frappe.throw(_("You are not permitted to change the margin."), frappe.PermissionError)
	doc.margin_percentage = flt(margin_percentage)
	doc.save()
	return {"modified": doc.modified}


def _editable(name, modified=None):
	"""The estimation for a change: write permission, a state the user may edit, and nobody saved it meanwhile."""
	doc = frappe.get_doc(DOCTYPE, name)
	doc.check_permission("write")
	state_field, states = _workflow_states()
	if not _can_edit(doc, state_field, states):
		frappe.throw(
			_("{0} cannot be changed in its current state.").format(doc.name), frappe.PermissionError
		)
	if modified and str(doc.modified) != str(modified):
		frappe.throw(
			_("{0} was saved by someone else after you opened it. Reload it and try again.").format(doc.name),
			frappe.TimestampMismatchError,
		)
	return doc
