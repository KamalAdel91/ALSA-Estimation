"""The app's service worker, served at /alsa-estimation-sw.js.

A service worker controls only pages under its own URL, and a file under /assets cannot control
/ALSA.Estimation, so it is served from the site root and registered with the app's scope.
It shows the pushes the app will send, and opens the estimation when one is tapped."""

from frappe.website.page_renderers.base_renderer import BaseRenderer
from werkzeug.wrappers import Response

from alsa_estimation import APP_ROUTE, APP_TITLE

SW_PATH = "alsa-estimation-sw.js"

SCRIPT = """
const ROUTE = "/{route}";
const TITLE = "{title}";

self.addEventListener("install", () => self.skipWaiting());
self.addEventListener("activate", (e) => e.waitUntil(self.clients.claim()));

self.addEventListener("push", (e) => {{
	let p = {{}};
	try {{
		p = e.data ? e.data.json() : {{}};
	}} catch (err) {{
		p = {{ data: {{ body: e.data && e.data.text() }} }};
	}}
	const n = p.notification || {{}};
	const d = p.data || {{}};
	const link = d.click_action || n.click_action || (p.fcmOptions && p.fcmOptions.link) || ROUTE;
	e.waitUntil(
		self.registration.showNotification(d.title || n.title || TITLE, {{
			body: d.body || n.body || "",
			icon: "/alsa-estimation-icon-192.png",
			tag: d.tag || undefined,
			data: {{ link }},
		}})
	);
}});

self.addEventListener("notificationclick", (e) => {{
	e.notification.close();
	const link = (e.notification.data && e.notification.data.link) || ROUTE;
	e.waitUntil(
		self.clients.matchAll({{ type: "window", includeUncontrolled: true }}).then((windows) => {{
			for (const w of windows) {{
				if (w.url.includes(ROUTE) && "focus" in w) {{
					w.navigate(link);
					return w.focus();
				}}
			}}
			return self.clients.openWindow(link);
		}})
	);
}});
""".format(route=APP_ROUTE, title=APP_TITLE)


class ServiceWorkerRenderer(BaseRenderer):
	def can_render(self):
		return self.path.strip("/") == SW_PATH

	def render(self):
		response = Response(SCRIPT, mimetype="application/javascript")
		response.headers["Cache-Control"] = "no-cache"
		response.headers["Service-Worker-Allowed"] = f"/{APP_ROUTE}"
		return response
