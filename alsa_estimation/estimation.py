"""The estimation screen and its sections, read only. Shares the workflow helpers of api.py."""

from html import unescape

import frappe
from frappe import _
from frappe.utils import cint, flt, fmt_money, strip_html
from nexlify_budget_control.nexlify_budget_control.manpower import trade_order
from nexlify_budget_control.nexlify_budget_control.opportunity_rfq import get_rfq_for_estimation

from alsa_estimation.api import DOCTYPE, _can_edit, _hint, _workflow_states

# Same palette and order rule as manpower_order.js on the desk.
TRADE_COLORS = ["#2490EF", "#20A39E", "#F59E0B", "#8B5CF6", "#EC4899", "#64748B"]


@frappe.whitelist(methods=["GET"])
def get_estimation(name):
	"""One estimation: header, stored totals, what each section holds, and the attachments."""
	doc = _read(name)
	can_see_price = _can_see_price()
	state_field, states = _workflow_states()
	state = doc.get(state_field)
	first_state = states[0]["name"] if states else None
	last_move = frappe.db.get_value(
		"Comment",
		{"reference_doctype": DOCTYPE, "reference_name": doc.name, "comment_type": "Workflow"},
		"content",
		order_by="creation desc",
	)
	hint, hint_tone = _hint(doc, state, first_state, last_move)

	opportunity = frappe._dict()
	if doc.opportunity:
		opportunity = (
			frappe.db.get_value(
				"Opportunity",
				doc.opportunity,
				["custom_opportunity_name", "custom_project_type"],
				as_dict=True,
			)
			or frappe._dict()
		)

	revision = None
	if hint_tone == "warn":
		note = frappe.db.get_value(
			"Comment",
			{
				"reference_doctype": DOCTYPE,
				"reference_name": doc.name,
				"comment_type": "Comment",
				"content": ["like", "%Revision requested by%"],
			},
			["content", "creation"],
			as_dict=True,
			order_by="creation desc",
		)
		if note:
			revision = {"text": unescape(strip_html(note.content)), "when": note.creation}

	total_cost = flt(doc.total_cost)
	days = flt(doc.total_work_days)
	price = None
	if can_see_price:
		total_price = flt(doc.get("total_price"))
		price = {
			"total_price": total_price,
			"price_per_day": doc.get("price_per_day"),
			"margin_amount": doc.get("margin_amount"),
			"margin_percentage": doc.get("margin_percentage"),
			"cost_share": flt(total_cost / total_price * 100, 1) if total_price else 0,
		}

	by_category = {}
	for row in doc.other_costs or []:
		key = row.budget_category or _("Uncategorized")
		by_category[key] = by_category.get(key, 0) + flt(row.cost)
	breakdown = [
		{"label": _("Accommodation"), "amount": doc.accommodation_total},
		{"label": _("Test Equipment"), "amount": doc.test_equipment_total},
		{"label": _("Car & Fuels"), "amount": doc.transportation_total},
		*({"label": k, "amount": v} for k, v in by_category.items()),
	]

	rfq_items = 0
	if doc.opportunity:
		rfq_items = frappe.db.count(
			"Opportunity RFQ Item", {"parent": doc.opportunity, "parenttype": "Opportunity"}
		)
	scope_items = frappe.db.count("Project Equipment Scope", {"cost_budget": doc.name, "docstatus": ["<", 2]})
	margin = _("Margin {0}%").format(_num(price["margin_percentage"])) if price else None
	sections = [
		{"key": "rfq", "label": _("RFQ"), "text": _plural(rfq_items, _("{0} item"), _("{0} items"))}
		if doc.opportunity
		else None,
		{
			"key": "scope",
			"label": _("Equipment scope"),
			"text": _("{0} equipment, {1}").format(scope_items, _plural(days, _("{0} team day"), _("{0} team days"))),
		},
		{"key": "rates", "label": _("Team daily rates"), "amount": doc.manpower_cost},
		{"key": "accommodation", "label": _("Accommodation"), "amount": doc.accommodation_total},
		{"key": "test_equipment", "label": _("Test equipment"), "amount": doc.test_equipment_total},
		{"key": "transportation", "label": _("Car & fuels"), "amount": doc.transportation_total},
		{"key": "other_costs", "label": _("Other costs"), "amount": doc.other_costs_table_total},
		{"key": "cost", "label": _("Cost & price"), "text": margin, "amount": None if margin else total_cost},
		{
			"key": "budget",
			"label": _("Budget details"),
			"text": _("Difference {0}").format(fmt_money(doc.budget_difference, 2)),
		},
	]

	return {
		"name": doc.name,
		"modified": doc.modified,
		"can_edit": _can_edit(doc, state_field, states),
		"can_edit_price": can_see_price and 1 in frappe.get_meta(DOCTYPE).get_permlevel_access("write"),
		"customer": frappe.db.get_value("Customer", doc.customer, "customer_name") or doc.customer,
		"title": opportunity.custom_opportunity_name or "",
		"project_type": opportunity.custom_project_type or "",
		"opportunity": doc.opportunity,
		"currency": doc.currency,
		"conversion_rate": doc.conversion_rate,
		"estimation_date": doc.estimation_date,
		"state": state,
		"tone": {s["name"]: s["tone"] for s in states}.get(state, "gray"),
		"hint": hint,
		"hint_tone": hint_tone,
		"revision": revision,
		"totals": {
			"total_cost": total_cost,
			"manpower_cost": doc.manpower_cost,
			"other_cost_total": doc.other_cost_total,
			"total_work_days": days,
			"duration_months": doc.duration_months,
			"cost_per_day": flt(total_cost / days, 2) if days else 0,
		},
		"price": price,
		"breakdown": [b for b in breakdown if flt(b["amount"])],
		"sections": [s for s in sections if s],
		"attachments": {"signed_contract": doc.signed_contract, "contract_no_prices": doc.contract_no_prices},
	}


@frappe.whitelist(methods=["GET"])
def get_rfq(name):
	"""The RFQ of the estimation's Opportunity, read through nexlify_budget_control (it checks the permission)."""
	return get_rfq_for_estimation(name)


@frappe.whitelist(methods=["GET"])
def get_section(name, section):
	"""One Execution Estimation section as cards: each row with its figures, then the section totals."""
	builder = SECTIONS.get(section)
	if not builder:
		frappe.throw(_("Unknown section: {0}").format(section))
	doc = _read(name)
	state_field, states = _workflow_states()
	return {
		"name": doc.name,
		"modified": doc.modified,
		"can_edit": _can_edit(doc, state_field, states),
		**builder(doc, _trade_colors(), _can_see_price()),
	}


def _section_scope(doc, colors, can_see_price):
	scope = frappe.get_all(
		"Project Equipment Scope",
		filters={"cost_budget": doc.name, "docstatus": ["<", 2]},
		fields=[
			"name",
			"equipment",
			"quantity",
			"days_per_equipment",
			"total_days",
			"crew_day_cost",
			"manpower_cost",
			"total_price",
		],
		order_by="creation asc",
	)
	roles = {}
	if scope:
		for r in frappe.get_all(
			"Project Equipment Scope Role",
			filters={"parenttype": "Project Equipment Scope", "parent": ["in", [s.name for s in scope]]},
			fields=["parent", "trade", "count"],
			order_by="idx asc",
		):
			roles.setdefault(r.parent, []).append(r)
	rows = []
	for s in scope:
		figures = [_fig(_("Crew day cost"), s.crew_day_cost), _fig(_("Cost"), s.manpower_cost, tone="cost")]
		if can_see_price:
			figures.append(_fig(_("Price"), s.total_price, tone="price"))
		crew = sorted(roles.get(s.name, []), key=lambda r: _trade_rank(colors, r.trade))
		rows.append(
			{
				"key": s.name,
				"title": s.equipment,
				"subtitle": _("Qty {0}, {1} each").format(
					_num(s.quantity), _plural(s.days_per_equipment, _("{0} day"), _("{0} days"))
				),
				"aside": _plural(s.total_days, _("{0} day"), _("{0} days")),
				"chips": [
					{"text": r.trade, "count": cint(r.count), "dot": _color(colors, r.trade)} for r in crew
				],
				"figures": figures,
				"edit": {
					"quantity": flt(s.quantity),
					"days_per_equipment": flt(s.days_per_equipment),
					"roles": [{"trade": r.trade, "count": cint(r.count)} for r in crew],
				},
			}
		)
	return {
		"title": _("Equipment scope"),
		"facts": [
			{"label": _("Equipment"), "value": str(len(scope))},
			{"label": _("Team days"), "value": _num(doc.total_work_days)},
		],
		"rows": rows,
		"totals": [_fig(_("Manpower cost"), doc.manpower_cost, tone="cost")],
		"empty": _("No equipment yet."),
	}


def _section_rates(doc, colors, can_see_price):
	rows = [
		{
			"title": r.designation,
			"dot": _color(colors, r.designation),
			"figures": [
				_fig(_("Basic salary"), r.basic_salary),
				_fig(_("Factor"), r.factor, kind="number"),
				_fig(_("Complete salary"), r.complete_salary),
				_fig(_("Day rate"), r.day_rate),
			],
		}
		for r in sorted(doc.team_rates or [], key=lambda r: _trade_rank(colors, r.designation))
	]
	return {
		"title": _("Team daily rates"),
		"facts": [{"label": _("Working days per month"), "value": _num(doc.working_days_per_month)}],
		"edit": {
			"working_days_per_month": cint(doc.working_days_per_month),
			"rows": [
				{"designation": r.designation, "basic_salary": flt(r.basic_salary), "factor": flt(r.factor)}
				for r in sorted(doc.team_rates or [], key=lambda r: _trade_rank(colors, r.designation))
			],
		},
		"rows": rows,
		"totals": [_fig(_("Manpower cost"), doc.manpower_cost, tone="cost")],
		"empty": _("The rows follow the trades in Equipment scope."),
	}


def _section_accommodation(doc, colors, can_see_price):
	rows = [
		{
			"title": r.designation,
			"dot": _color(colors, r.designation),
			"figures": [
				_fig(_("Persons"), r.persons, kind="number"),
				_fig(_("Monthly per person"), r.monthly_cost_per_person),
				_fig(_("Cost"), r.cost, tone="cost"),
			],
		}
		for r in sorted(doc.accommodation or [], key=lambda r: _trade_rank(colors, r.designation))
	]
	return {
		"title": _("Accommodation"),
		"facts": [
			{"label": _("Basis"), "value": _(doc.accommodation_basis) if doc.accommodation_basis else ""},
			{"label": _("Duration"), "value": _plural(doc.duration_months, _("{0} month"), _("{0} months"))},
		],
		"rows": rows,
		"totals": [_fig(_("Accommodation total"), doc.accommodation_total, tone="cost")],
		"empty": _("The rows follow the trades in Equipment scope."),
	}


def _section_test_equipment(doc, colors, can_see_price):
	return {
		"title": _("Test equipment"),
		"facts": [{"label": _("Duration"), "value": _plural(doc.duration_months, _("{0} month"), _("{0} months"))}],
		"rows": _asset_rows(doc.test_equipment, doc.duration_months),
		"totals": [_fig(_("Test equipment total"), doc.test_equipment_total, tone="cost")],
		"empty": _("No test equipment yet."),
	}


def _section_transportation(doc, colors, can_see_price):
	return {
		"title": _("Car & fuels"),
		"facts": [{"label": _("Duration"), "value": _plural(doc.duration_months, _("{0} month"), _("{0} months"))}],
		"rows": _asset_rows(doc.transportation, doc.duration_months),
		"totals": [
			_fig(_("Fuel & maintenance"), doc.fuel_maintenance_total),
			_fig(_("Car & fuels total"), doc.transportation_total, tone="cost"),
		],
		"empty": _("No cars yet."),
	}


def _section_other_costs(doc, colors, can_see_price):
	rows = [
		{
			"title": r.description,
			"subtitle": r.budget_category or _("Uncategorized"),
			"figures": [_fig(_("Cost"), r.cost, tone="cost")],
		}
		for r in doc.other_costs or []
	]
	return {
		"title": _("Other costs"),
		"facts": [],
		"rows": rows,
		"totals": [_fig(_("Other costs total"), doc.other_costs_table_total, tone="cost")],
		"empty": _("No other costs yet."),
	}


def _section_budget(doc, colors, can_see_price):
	rows = [
		{
			"title": r.budget_category,
			"badge": {"text": _("Auto"), "tone": "gray"} if r.is_auto else None,
			"figures": [
				_fig(_("Estimated"), r.estimated_amount),
				_fig(_("Warn at"), r.warning_threshold_percentage, kind="percent"),
			],
		}
		for r in doc.details or []
	]
	return {
		"title": _("Budget details"),
		"facts": [],
		"rows": rows,
		"totals": [
			_fig(_("Budget details total"), doc.budget_details_total),
			_fig(_("Estimation total cost"), doc.total_cost, tone="cost"),
			_fig(
				_("Difference"),
				doc.budget_difference,
				tone="price" if not flt(doc.budget_difference) else "cost",
			),
		],
		"empty": _("No budget rows yet."),
	}


SECTIONS = {
	"scope": _section_scope,
	"rates": _section_rates,
	"accommodation": _section_accommodation,
	"test_equipment": _section_test_equipment,
	"transportation": _section_transportation,
	"other_costs": _section_other_costs,
	"budget": _section_budget,
}


def _asset_rows(rows, months):
	out = []
	for r in rows or []:
		if r.ownership == "Rented":
			subtitle = _("Rent {0} a month").format(fmt_money(r.monthly_rent, 2))
		else:
			subtitle = _("Asset {0} over {1} months").format(
				fmt_money(r.asset_value, 2), cint(r.depreciation_months)
			)
		out.append(
			{
				"title": r.description,
				"subtitle": subtitle,
				"badge": {"text": _(r.ownership), "tone": "amber" if r.ownership == "Rented" else "gray"},
				"figures": [
					_fig(_("Monthly"), r.monthly_cost),
					_fig(_("Cost for {0}").format(_plural(months, _("{0} month"), _("{0} months"))), r.cost, tone="cost"),
				],
			}
		)
	return out


def _read(name):
	"""The estimation, after the read check, with the fields this user may not read removed."""
	doc = frappe.get_doc(DOCTYPE, name)
	doc.check_permission("read")
	doc.apply_fieldlevel_read_permissions()
	return doc


def _can_see_price():
	"""Prices are the permlevel 1 fields of Project Estimation; the desk hides them the same way."""
	return 1 in frappe.get_meta(DOCTYPE).get_permlevel_access("read")


def _fig(label, value, kind="money", tone=None):
	return {"label": label, "value": flt(value), "kind": kind, "tone": tone}


def _num(value):
	"""2 -> "2", 0.5 -> "0.5", 1250 -> "1,250"."""
	return f"{flt(value):,.2f}".rstrip("0").rstrip(".")


def _trade_colors():
	return {trade: TRADE_COLORS[i % len(TRADE_COLORS)] for i, trade in enumerate(trade_order())}


def _trade_rank(colors, trade):
	return (list(colors).index(trade) if trade in colors else len(colors), trade or "")


def _color(colors, trade):
	return colors.get(trade, TRADE_COLORS[-1])


def _plural(value, one, many):
	"""_("{0} day") or _("{0} days"), by the number."""
	return (one if flt(value) == 1 else many).format(_num(value))
