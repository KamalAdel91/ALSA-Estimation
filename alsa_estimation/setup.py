"""One-time setup helper: the default Notification rules for estimation alerts.

Run once per site from the desk, as a System Manager, in the browser console:
    frappe.call("alsa_estimation.setup.create_default_alerts").then((r) => console.log(r.message))
Then change or switch off the rules from the Notification list; this helper never touches existing ones."""

import frappe

TEAM = [{"receiver_by_role": "Estimation Manager"}]

RULES = [
	{
		"name": "ALSA Estimation: new estimation",
		"event": "New",
		"subject": "New estimation {{ doc.name }}",
		"notification_message": "{{ doc.customer }} sent it from Opportunity {{ doc.opportunity }}.",
		"recipients": TEAM,
	},
	{
		"name": "ALSA Estimation: back from Sales",
		"event": "Value Change",
		"value_changed": "workflow_state",
		"condition": 'doc.workflow_state == "Draft"',
		"subject": "{{ doc.name }} came back from Sales",
		"notification_message": "Sales asked for a revision. Open it to see what to change.",
		"recipients": TEAM,
	},
	{
		"name": "ALSA Estimation: contract received",
		"event": "Value Change",
		"value_changed": "workflow_state",
		"condition": 'doc.workflow_state == "Contract Review"',
		"subject": "Contract received for {{ doc.name }}",
		"notification_message": "Attach the Contract (No Prices), then hand it over to Planning.",
		"recipients": TEAM,
	},
	{
		"name": "ALSA Estimation: handed over",
		"event": "Value Change",
		"value_changed": "workflow_state",
		"condition": 'doc.workflow_state == "Handed Over"',
		"subject": "{{ doc.name }} was handed over to Planning",
		"notification_message": "{{ doc.customer }}",
		"recipients": [{"receiver_by_role": "Estimation Manager"}],
	},
]


@frappe.whitelist(methods=["POST"])
def create_default_alerts():
	"""Creates the rules that are missing and leaves the existing ones as they are."""
	frappe.only_for("System Manager")
	done = []
	for rule in RULES:
		if frappe.db.exists("Notification", rule["name"]):
			done.append(f"already there: {rule['name']}")
			continue
		doc = {
			"doctype": "Notification",
			"document_type": "Project Estimation",
			"channel": "System Notification",
			"condition_type": "Python",
			"enabled": 1,
		}
		doc.update(rule)
		frappe.get_doc(doc).insert()
		done.append(f"created: {rule['name']}")
	return done
