"""Supply lines from the app, with the desk form's rules. Sending and the line actions stay in
nexlify_budget_control.supply_chain, which the app calls directly."""

import frappe
from frappe import _
from frappe.utils import flt
from nexlify_budget_control.nexlify_budget_control.supply_chain import (
	MANUAL,
	SUPPLY_CHAIN,
	first_state,
	in_first_state,
	pending_requests,
)

from alsa_estimation.api import DOCTYPE


@frappe.whitelist(methods=["GET"])
def get_supply(name):
	"""The Supply lines, where each one stands, and what this user can do on it."""
	est = frappe.get_doc(DOCTYPE, name)
	est.check_permission("read")
	can_write = est.has_permission("write")
	est.apply_fieldlevel_read_permissions()
	editable = bool(can_write and in_first_state(est))
	pending = pending_requests(est.name)
	waiting_requests = set(pending)

	lines, counts = [], {}
	for r in est.supply or []:
		status = _status(r)
		counts[status] = counts.get(status, 0) + 1
		waiting = bool(r.supply_request in waiting_requests and not r.supplier_quotation)
		live = editable and not r.is_cancelled
		lines.append(
			{
				"name": r.name,
				"item_code": r.item_code,
				"description": r.description,
				"qty": flt(r.qty),
				"uom": r.uom,
				"rate": flt(r.rate),
				"cost": flt(r.cost),
				"price_source": r.price_source,
				"status": status,
				"supplier": r.supplier,
				"supplier_quotation": r.supplier_quotation,
				"supply_request": r.supply_request,
				"qty_editable": live and not waiting,
				"description_editable": live,
				"rate_editable": live and r.price_source == MANUAL,
				"actions": _actions(r, status, editable),
			}
		)

	to_send = [
		r
		for r in est.supply or []
		if not r.is_cancelled
		and r.price_source != MANUAL
		and not r.supplier_quotation
		and r.supply_request not in waiting_requests
	]
	locked = ""
	if can_write and not editable:
		locked = _("The Supply can change only while the Estimation is in {0}.").format(_(first_state()))
	return {
		"name": est.name,
		"modified": est.modified,
		"currency": est.currency,
		"editable": editable,
		"locked_reason": locked,
		"lines": lines,
		"counts": counts,
		"to_send": len(to_send),
		"pending": pending,
		"supply_total": flt(est.get("supply_total")),
		"sources": [SUPPLY_CHAIN, MANUAL],
	}


@frappe.whitelist(methods=["GET"])
def search_items(txt=""):
	txt = (txt or "").strip()
	or_filters = None
	if txt:
		or_filters = [["Item", "name", "like", f"%{txt}%"], ["Item", "item_name", "like", f"%{txt}%"]]
	return frappe.get_list(
		"Item",
		filters={"disabled": 0},
		or_filters=or_filters,
		fields=["name", "item_name", "stock_uom"],
		order_by="modified desc",
		page_length=20,
	)


@frappe.whitelist(methods=["POST"])
def add_supply_line(name, item_code, qty, price_source, rate=0, description=None, modified=None):
	est = _editable(name, modified)
	if price_source not in (SUPPLY_CHAIN, MANUAL):
		frappe.throw(_("Pick where the price comes from."))
	if flt(qty) <= 0:
		frappe.throw(_("Enter a quantity above 0."))
	item = frappe.db.get_value("Item", item_code, ["item_name", "stock_uom"], as_dict=True)
	if not item:
		frappe.throw(_("Item {0} was not found.").format(item_code))
	est.append(
		"supply",
		{
			"item_code": item_code,
			"description": (description or "").strip()[:140] or item.item_name,
			"qty": flt(qty),
			"uom": item.stock_uom,
			"price_source": price_source,
			"rate": flt(rate) if price_source == MANUAL else 0,
		},
	)
	est.save()
	return {"modified": est.modified}


@frappe.whitelist(methods=["POST"])
def update_supply_line(name, row, qty=None, rate=None, description=None, modified=None):
	"""A new quantity on a Supply Chain line clears its price on save, as on the desk."""
	est = _editable(name, modified)
	line = _line(est, row)
	if line.is_cancelled:
		frappe.throw(_("Restore the line first."))
	if qty is not None:
		if flt(qty) <= 0:
			frappe.throw(_("Enter a quantity above 0."))
		line.qty = flt(qty)
	if rate is not None:
		if line.price_source != MANUAL:
			frappe.throw(_("Supply Chain sets the rate of this line."))
		line.rate = flt(rate)
	if description is not None:
		line.description = description.strip()[:140] or line.item_code
	est.save()
	return {"modified": est.modified}


@frappe.whitelist(methods=["POST"])
def remove_supply_line(name, row, modified=None):
	est = _editable(name, modified)
	line = _line(est, row)
	if line.supply_request or line.supplier_quotation:
		frappe.throw(_("This line went to the Supply Chain, so it can only be cancelled."))
	est.remove(line)
	est.save()
	return {"modified": est.modified}


def _editable(name, modified):
	est = frappe.get_doc(DOCTYPE, name)
	est.check_permission("write")
	if not in_first_state(est):
		frappe.throw(_("The Supply can change only while the Estimation is in {0}.").format(_(first_state())))
	if modified and str(est.modified) != str(modified):
		frappe.throw(_("Someone changed this estimation. Reload it and try again."))
	return est


def _line(est, row):
	line = next((r for r in est.supply or [] if r.name == row), None)
	if not line:
		frappe.throw(_("This Supply line is not in {0} any more. Reload the estimation.").format(est.name))
	return line


def _status(r):
	if r.is_cancelled:
		return "Cancelled"
	if r.price_source == MANUAL:
		return "Manual"
	return r.supply_status or "Not Sent"


def _actions(r, status, editable):
	"""The same menu as the desk's Actions button on a Supply line."""
	if not editable:
		return []
	live, manual = not r.is_cancelled, r.price_source == MANUAL
	options = (
		("restore", _("Restore line"), bool(r.is_cancelled)),
		("send_line", _("Send this line to Supply Chain"), live and not manual and status == "Not Sent"),
		("quote_again", _("Quote again"), live and status == "Priced"),
		("to_manual", _("Switch to Manual"), live and not manual and status != "Waiting"),
		("to_supply_chain", _("Switch to Supply Chain"), live and manual),
		("remove", _("Remove line"), not r.supply_request and not r.supplier_quotation),
		("cancel", _("Cancel line"), live),
	)
	return [{"action": a, "label": label} for a, label, ok in options if ok]
