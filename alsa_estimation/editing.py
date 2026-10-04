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


ASSET_TABLES = {"test_equipment": "Test Equipment", "transportation": "Car"}


@frappe.whitelist(methods=["GET"])
def get_options(kind):
	"""Picker options: enabled Test Equipment or Cars with their ownership, or Budget Categories."""
	frappe.has_permission(DOCTYPE, "read", throw=True)
	if kind in ASSET_TABLES:
		return frappe.get_list(
			ASSET_TABLES[kind],
			filters={"enabled": 1},
			fields=["name", "ownership"],
			order_by="name asc",
			limit_page_length=0,
		)
	if kind == "budget_category":
		return frappe.get_list("Budget Category", fields=["name"], order_by="name asc", limit_page_length=0)
	frappe.throw(_("Unknown options: {0}").format(kind))


@frappe.whitelist(methods=["POST"])
def save_accommodation(name, basis, rows, modified=None):
	"""The basis and the persons per trade; the save recalculates the monthly cost unless the basis is typed."""
	doc = _editable(name, modified)
	if basis not in (doc.meta.get_field("accommodation_basis").options or "").split("\n"):
		frappe.throw(_("Choose an accommodation basis."))
	doc.accommodation_basis = basis
	values = {r.get("designation"): r for r in frappe.parse_json(rows) or []}
	for row in doc.accommodation or []:
		value = values.get(row.designation)
		if value:
			row.persons = cint(value.get("persons"))
			row.monthly_cost_per_person = flt(value.get("monthly_cost_per_person"))
	doc.save()
	return {"modified": doc.modified}


@frappe.whitelist(methods=["POST"])
def save_assets(name, table, rows, fuel_maintenance_total=None, modified=None):
	"""Test equipment or cars, as a list of records; ownership, value and rent are fetched from each on save."""
	if table not in ASSET_TABLES:
		frappe.throw(_("Unknown table: {0}").format(table))
	doc = _editable(name, modified)
	kept = {}
	for row in doc.get(table) or []:
		kept.setdefault(row.description, []).append(row)
	doc.set(table, [])
	for description in frappe.parse_json(rows) or []:
		if not description:
			continue
		if kept.get(description):
			doc.append(table, kept[description].pop(0))
		else:
			doc.append(table, {"description": description})
	if table == "transportation" and fuel_maintenance_total is not None:
		doc.fuel_maintenance_total = flt(fuel_maintenance_total)
	doc.save()
	return {"modified": doc.modified}


@frappe.whitelist(methods=["POST"])
def save_other_costs(name, rows, modified=None):
	"""Other costs: the description, budget category and cost of each line, in the order sent."""
	doc = _editable(name, modified)
	doc.set("other_costs", [])
	for row in frappe.parse_json(rows) or []:
		description = (row.get("description") or "").strip()
		if description or flt(row.get("cost")):
			doc.append(
				"other_costs",
				{
					"description": description,
					"budget_category": row.get("budget_category") or None,
					"cost": flt(row.get("cost")),
				},
			)
	doc.save()
	return {"modified": doc.modified}


@frappe.whitelist(methods=["POST"])
def save_thresholds(name, rows, modified=None):
	"""The warning threshold of each Budget Details row; the amounts stay calculated."""
	doc = _editable(name, modified)
	values = {
		r.get("budget_category"): flt(r.get("warning_threshold_percentage"))
		for r in frappe.parse_json(rows) or []
	}
	for row in doc.details or []:
		if row.budget_category in values:
			row.warning_threshold_percentage = values[row.budget_category]
	doc.save()
	return {"modified": doc.modified}
