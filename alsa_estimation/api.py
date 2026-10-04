import frappe
from frappe import _
from frappe.desk.doctype.number_card.number_card import get_result
from frappe.model.workflow import get_workflow
from frappe.utils import cint

DOCTYPE = "Project Estimation"

# Number Cards of the Estimation workspace: the app shows their counts and filters with their own definitions.
HOME_CARDS = ("Draft Estimations", "Estimations Missing Contract", "Estimations Submitted This Month")

# Workflow State style -> badge tone in the app.
TONES = {"Primary": "blue", "Info": "blue", "Warning": "amber", "Success": "green", "Danger": "red"}

PAGE_LENGTH = 20
LIST_FIELDS = [
	"name",
	"customer",
	"opportunity",
	"docstatus",
	"total_cost",
	"total_work_days",
	"signed_contract",
	"contract_no_prices",
	"modified",
]


@frappe.whitelist(methods=["GET"])
def get_home():
	"""The workspace card counts and the estimations waiting for this user (or the latest ones)."""
	frappe.has_permission(DOCTYPE, "read", throw=True)
	state_field, states = _workflow_states()
	cards = []
	for name in HOME_CARDS:
		if frappe.db.exists("Number Card", name):
			card = frappe.get_cached_doc("Number Card", name)
			value = get_result(card.as_dict(), card.filters_json)
			cards.append({"name": name, "label": _(card.label), "value": cint(value)})

	roles = set(frappe.get_roles())
	mine = [s["name"] for s in states if s["docstatus"] == 0 and s["allow_edit"] in roles]
	action = _rows({state_field: ["in", mine]}, state_field, states, limit=10) if mine else []
	recent = [] if action else _rows({}, state_field, states, limit=5)
	return {"cards": cards, "action": action, "recent": recent}


@frappe.whitelist(methods=["GET"])
def get_estimations(state=None, card=None, search=None, start=0):
	"""One page of estimations, newest first: by workflow state, by a workspace card's filters, or by search."""
	frappe.has_permission(DOCTYPE, "read", throw=True)
	state_field, states = _workflow_states()
	filters = []
	if card in HOME_CARDS:
		filters = frappe.parse_json(frappe.get_cached_doc("Number Card", card).filters_json or "[]")
	elif state:
		filters = {state_field: state}
	search = (search or "").strip()
	rows = _rows(filters, state_field, states, limit=PAGE_LENGTH + 1, start=cint(start), search=search)
	return {
		"rows": rows[:PAGE_LENGTH],
		"more": len(rows) > PAGE_LENGTH,
		"states": [{"name": s["name"], "tone": s["tone"]} for s in states],
	}


def _workflow_states():
	"""The active Project Estimation workflow: its state field, and its states in order with a badge tone each."""
	workflow = get_workflow(DOCTYPE)
	styles = dict(frappe.get_all("Workflow State", fields=["name", "style"], as_list=True))
	states = [
		{
			"name": s.state,
			"tone": TONES.get(styles.get(s.state) or "", "gray"),
			"docstatus": cint(s.doc_status),
			"allow_edit": s.allow_edit,
		}
		for s in workflow.states
	]
	return workflow.workflow_state_field, states


def _rows(filters, state_field, states, limit, start=0, search=None):
	"""List rows with the customer's name, the Opportunity's name and type, and what each one waits for."""
	or_filters = None
	if search:
		or_filters = [
			[DOCTYPE, field, "like", f"%{search}%"] for field in ("name", "customer", "opportunity")
		]
	rows = frappe.get_list(
		DOCTYPE,
		filters=filters,
		or_filters=or_filters,
		fields=[*LIST_FIELDS, state_field],
		order_by="modified desc",
		start=start,
		page_length=limit,
	)
	if not rows:
		return []

	opportunities = {}
	opportunity_names = list({r.opportunity for r in rows if r.opportunity})
	if opportunity_names:
		for o in frappe.get_all(
			"Opportunity",
			filters={"name": ["in", opportunity_names]},
			fields=["name", "custom_opportunity_name", "custom_project_type"],
		):
			opportunities[o.name] = o

	customer_names = {}
	customers = list({r.customer for r in rows if r.customer})
	if customers:
		customer_names = dict(
			frappe.get_all(
				"Customer",
				filters={"name": ["in", customers]},
				fields=["name", "customer_name"],
				as_list=True,
			)
		)

	last_move = {}
	for c in frappe.get_all(
		"Comment",
		filters={
			"reference_doctype": DOCTYPE,
			"reference_name": ["in", [r.name for r in rows]],
			"comment_type": "Workflow",
		},
		fields=["reference_name", "content"],
		order_by="creation desc",
	):
		last_move.setdefault(c.reference_name, c.content)

	tones = {s["name"]: s["tone"] for s in states}
	first_state = states[0]["name"] if states else None
	out = []
	for r in rows:
		state = r.get(state_field)
		opportunity = opportunities.get(r.opportunity) or {}
		hint, hint_tone = _hint(r, state, first_state, last_move.get(r.name))
		out.append(
			{
				"name": r.name,
				"customer": customer_names.get(r.customer) or r.customer or "",
				"title": opportunity.get("custom_opportunity_name") or "",
				"project_type": opportunity.get("custom_project_type") or "",
				"state": state,
				"tone": tones.get(state, "gray"),
				"total_cost": r.total_cost,
				"modified": r.modified,
				"hint": hint,
				"hint_tone": hint_tone,
			}
		)
	return out


def _hint(row, state, first_state, last_move):
	"""What an open estimation waits for, read from its fields and its last workflow move (no state names)."""
	if row.docstatus != 0:
		return "", ""
	if row.signed_contract:
		if row.contract_no_prices:
			return _("Ready to hand over to Planning"), ""
		return _("Attach the Contract (No Prices) to hand over"), ""
	if state != first_state:
		return "", ""
	if last_move in (state, _(state)):
		return _("Sent back for a revision"), "warn"
	if not row.total_work_days:
		return _("Set days and crew"), ""
	return "", ""
