// Calls whitelisted methods with the user's desk session. Reads go as GET; writes as POST with the CSRF token.
export class ApiError extends Error {
	constructor(message, status) {
		super(message);
		this.status = status;
	}
}

function serverMessage(data) {
	try {
		if (data._server_messages) {
			return JSON.parse(data._server_messages)
				.map((m) => JSON.parse(m).message)
				.join("\n")
				.replace(/<[^>]+>/g, "");
		}
	} catch (e) {
		// fall back to the exception text below
	}
	return data.exception || "";
}

function isGuest() {
	return /(?:^|;\s*)user_id=Guest(?:;|$)/.test(document.cookie);
}

export async function call(method, args = {}, { write = false } = {}) {
	let url = `/api/method/${method}`;
	const options = { headers: { Accept: "application/json" } };
	if (write) {
		options.method = "POST";
		options.headers["Content-Type"] = "application/json";
		options.headers["X-Frappe-CSRF-Token"] = window.csrf_token;
		options.body = JSON.stringify(args);
	} else {
		const query = new URLSearchParams();
		for (const [key, value] of Object.entries(args)) {
			if (value !== undefined && value !== null) {
				query.set(key, typeof value === "object" ? JSON.stringify(value) : value);
			}
		}
		const qs = query.toString();
		if (qs) url += `?${qs}`;
	}

	const res = await fetch(url, options);
	const data = await res.json().catch(() => ({}));
	if (res.status === 401 || (res.status === 403 && isGuest())) {
		window.location.href = `/login?redirect-to=${encodeURIComponent(window.location.pathname)}`;
		throw new ApiError("Your session ended. Please sign in again.", res.status);
	}
	if (!res.ok) {
		throw new ApiError(serverMessage(data) || res.statusText, res.status);
	}
	return data.message;
}
