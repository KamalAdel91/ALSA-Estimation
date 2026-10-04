"""Workflow actions and the Contract (No Prices) upload, from the estimation screen."""

import frappe
from frappe import _
from frappe.model.workflow import apply_workflow, get_transitions

from alsa_estimation.api import DOCTYPE, _workflow_states
from alsa_estimation.editing import _editable


@frappe.whitelist(methods=["GET"])
def get_actions(name):
	"""The workflow actions this user may run now, as the desk shows them, and what each one leads to."""
	doc = frappe.get_doc(DOCTYPE, name)
	doc.check_permission("read")
	state_field, states = _workflow_states()
	if not doc.get(state_field):
		return []
	roles = set(frappe.get_roles())
	by_name = {s["name"]: s for s in states}
	actions = []
	for t in get_transitions(doc):
		state = by_name.get(t.next_state, {})
		actions.append(
			{
				"action": t.action,
				"next_state": t.next_state,
				"tone": state.get("tone", "gray"),
				"note": _note(doc.name, state, roles),
			}
		)
	return actions


@frappe.whitelist(methods=["POST"])
def apply_action(name, action, modified=None):
	"""Runs a workflow action the way the desk does: the workflow checks the role, the condition and the document."""
	current = frappe.db.get_value(DOCTYPE, name, "modified")
	if modified and str(current) != str(modified):
		frappe.throw(
			_("{0} was saved by someone else after you opened it. Reload it and try again.").format(name),
			frappe.TimestampMismatchError,
		)
	apply_workflow({"doctype": DOCTYPE, "name": name}, action)
	return {"ok": True}


@frappe.whitelist(methods=["POST"])
def attach_contract(name, file_url, modified=None):
	"""Puts the uploaded Contract (No Prices) on the estimation; the Handover to Planning needs it."""
	doc = _editable(name, modified)
	attached = frappe.db.exists(
		"File", {"file_url": file_url, "attached_to_doctype": DOCTYPE, "attached_to_name": doc.name}
	)
	if not attached:
		frappe.throw(_("Upload the file to {0} first.").format(doc.name))
	doc.contract_no_prices = file_url
	doc.save()
	return {"modified": doc.modified}


def _note(name, state, roles):
	"""What changes for the user after the action, read from the next state of the workflow."""
	if state.get("docstatus") == 1:
		return _("After this, {0} is submitted and its figures no longer change.").format(name)
	if state.get("docstatus") == 2:
		return _("This cancels {0}.").format(name)
	if state.get("allow_edit") not in roles:
		return _("After this, you cannot change {0} until it comes back to you.").format(name)
	return ""
