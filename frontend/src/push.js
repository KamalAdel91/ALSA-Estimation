import { call } from "./api.js";

// Frappe Cloud's push relay, the same one Frappe HR uses; "hrms" is the project the relay knows.
const PROJECT = "hrms";
const TOKEN_KEY = "alsa_estimation_push_token";

export const pushAvailable = () =>
	Boolean(
		window.alsa_boot.push &&
			window.isSecureContext &&
			"serviceWorker" in navigator &&
			"PushManager" in window &&
			"Notification" in window,
	);

export function pushOn() {
	try {
		return Boolean(localStorage.getItem(TOKEN_KEY)) && Notification.permission === "granted";
	} catch (e) {
		return false;
	}
}

async function registration() {
	const reg = await navigator.serviceWorker.register("/alsa-estimation-sw.js", {
		scope: `/${window.alsa_boot.route}`,
	});
	if (!reg.active) {
		await new Promise((resolve) => {
			const worker = reg.installing || reg.waiting;
			if (!worker) return resolve();
			worker.addEventListener("statechange", () => worker.state === "activated" && resolve());
		});
	}
	return reg;
}

async function messaging() {
	const [{ initializeApp, getApps }, fm] = await Promise.all([import("firebase/app"), import("firebase/messaging")]);
	if (!(await fm.isSupported())) throw new Error("This browser does not support push notifications.");
	const { config, vapid } = await call("alsa_estimation.notify.get_push_config");
	const app = getApps().find((a) => a.name === "alsa-estimation") || initializeApp(config, "alsa-estimation");
	return { fm, instance: fm.getMessaging(app), vapid };
}

export async function enablePush() {
	const permission = await Notification.requestPermission();
	if (permission !== "granted") {
		throw new Error("Notifications are blocked. Allow them for this site in the browser settings.");
	}
	const reg = await registration();
	const { fm, instance, vapid } = await messaging();
	const token = await fm.getToken(instance, { vapidKey: vapid, serviceWorkerRegistration: reg });
	const result = await call(
		"frappe.push_notification.subscribe",
		{ fcm_token: token, project_name: PROJECT },
		{ write: true },
	);
	if (result && result.success === false) throw new Error(result.message || "Could not turn on notifications.");
	try {
		localStorage.setItem(TOKEN_KEY, token);
	} catch (e) {
		// private browsing: the phone still gets the alerts
	}
}

export async function disablePush() {
	let token = null;
	try {
		token = localStorage.getItem(TOKEN_KEY);
	} catch (e) {
		// private browsing
	}
	if (token) {
		try {
			await call("frappe.push_notification.unsubscribe", { fcm_token: token, project_name: PROJECT }, { write: true });
		} catch (e) {
			// the relay may have dropped the token already
		}
		try {
			const { fm, instance } = await messaging();
			await fm.deleteToken(instance);
		} catch (e) {
			// nothing left to delete
		}
	}
	try {
		localStorage.removeItem(TOKEN_KEY);
	} catch (e) {
		// private browsing
	}
}
