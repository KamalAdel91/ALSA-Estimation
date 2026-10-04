app_name = "alsa_estimation"
app_title = "ALSA Estimation"
app_publisher = "Kamal Adel"
app_description = "Mobile web app for Project Estimation"
app_email = "Kmaal.adel@outlook.com"
app_license = "mit"

# Apps
# ------------------

# required_apps = []

# Each item in the list will be shown as an app in the apps page
# add_to_apps_screen = [
# 	{
# 		"name": "alsa_estimation",
# 		"logo": "/assets/alsa_estimation/logo.png",
# 		"title": "ALSA Estimation",
# 		"route": "/alsa_estimation",
# 		"has_permission": "alsa_estimation.api.permission.has_app_permission"
# 	}
# ]

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/alsa_estimation/css/alsa_estimation.css"
# app_include_js = "/assets/alsa_estimation/js/alsa_estimation.js"

# include js, css files in header of web template
# web_include_css = "/assets/alsa_estimation/css/alsa_estimation.css"
# web_include_js = "/assets/alsa_estimation/js/alsa_estimation.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "alsa_estimation/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Svg Icons
# ------------------
# include app icons in desk
# app_include_icons = "alsa_estimation/public/icons.svg"

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
# 	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# automatically load and sync documents of this doctype from downstream apps
# importable_doctypes = [doctype_1]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
# 	"methods": "alsa_estimation.utils.jinja_methods",
# 	"filters": "alsa_estimation.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "alsa_estimation.install.before_install"
# after_install = "alsa_estimation.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "alsa_estimation.uninstall.before_uninstall"
# after_uninstall = "alsa_estimation.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "alsa_estimation.utils.before_app_install"
# after_app_install = "alsa_estimation.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "alsa_estimation.utils.before_app_uninstall"
# after_app_uninstall = "alsa_estimation.utils.after_app_uninstall"

# Build
# ------------------
# To hook into the build process

# after_build = "alsa_estimation.build.after_build"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "alsa_estimation.notifications.get_notification_config"

# Awesome Bar
# -----------
# Extra search results: list of dicts with label, description, route, index.
# route: ["List", "ToDo"], "/desk/docs/some/page", or "https://example.com"
# awesomebar_search = ["alsa_estimation.search.awesomebar_results"]

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# Document Events
# ---------------
# Hook on document methods and events

# doc_events = {
# 	"*": {
# 		"on_update": "method",
# 		"on_cancel": "method",
# 		"on_trash": "method"
# 	}
# }

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"alsa_estimation.tasks.all"
# 	],
# 	"daily": [
# 		"alsa_estimation.tasks.daily"
# 	],
# 	"hourly": [
# 		"alsa_estimation.tasks.hourly"
# 	],
# 	"weekly": [
# 		"alsa_estimation.tasks.weekly"
# 	],
# 	"monthly": [
# 		"alsa_estimation.tasks.monthly"
# 	],
# }

# Testing
# -------

# before_tests = "alsa_estimation.install.before_tests"

# Extend DocType Class
# ------------------------------
#
# Specify custom mixins to extend the standard doctype controller.
# extend_doctype_class = {
# 	"Task": "alsa_estimation.custom.task.CustomTaskMixin"
# }

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "alsa_estimation.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "alsa_estimation.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["alsa_estimation.utils.before_request"]
# after_request = ["alsa_estimation.utils.after_request"]

# Job Events
# ----------
# before_job = ["alsa_estimation.utils.before_job"]
# after_job = ["alsa_estimation.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
# 	{
# 		"doctype": "{doctype_1}",
# 		"filter_by": "{filter_by}",
# 		"redact_fields": ["{field_1}", "{field_2}"],
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_2}",
# 		"filter_by": "{filter_by}",
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_3}",
# 		"strict": False,
# 	},
# 	{
# 		"doctype": "{doctype_4}"
# 	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"alsa_estimation.auth.validate"
# ]

# Automatically update python controller files with type annotations for this app.
# export_python_type_annotations = True

# default_log_clearing_doctypes = {
# 	"Logging DocType Name": 30  # days to retain logs
# }

# Translation
# ------------
# List of apps whose translatable strings should be excluded from this app's translations.
# ignore_translatable_strings_from = []

# ALSA Estimation: reads Project Estimation from nexlify_budget_control, served at /ALSA.Estimation
from alsa_estimation import APP_ROUTE

required_apps = ["nexlify_budget_control"]

website_route_rules = [
	{"from_route": f"/{APP_ROUTE}", "to_route": "alsa_estimation"},
	{"from_route": f"/{APP_ROUTE}/<path:app_path>", "to_route": "alsa_estimation"},
]
