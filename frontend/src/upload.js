import { serverMessage } from "./api.js";

const MAX_SIDE = 2000;
const SHRINK_FROM = 1.5 * 1024 * 1024;

// Photos from the phone camera are large; a contract page stays readable at 2000 px.
async function shrink(file) {
	if (!file.type.startsWith("image/") || file.size < SHRINK_FROM || !window.createImageBitmap) return file;
	const bitmap = await createImageBitmap(file).catch(() => null);
	if (!bitmap) return file;
	const scale = Math.min(1, MAX_SIDE / Math.max(bitmap.width, bitmap.height));
	const canvas = document.createElement("canvas");
	canvas.width = Math.round(bitmap.width * scale);
	canvas.height = Math.round(bitmap.height * scale);
	canvas.getContext("2d").drawImage(bitmap, 0, 0, canvas.width, canvas.height);
	const blob = await new Promise((resolve) => canvas.toBlob(resolve, "image/jpeg", 0.85));
	if (!blob) return file;
	return new File([blob], `${file.name.replace(/\.[^.]+$/, "")}.jpg`, { type: "image/jpeg" });
}

// Uploads a private file attached to a document field, the way the desk attach control does.
export async function uploadFile(file, { doctype, docname, fieldname }) {
	const ready = await shrink(file);
	const body = new FormData();
	body.append("file", ready, ready.name);
	body.append("is_private", "1");
	body.append("doctype", doctype);
	body.append("docname", docname);
	body.append("fieldname", fieldname);
	const res = await fetch("/api/method/upload_file", {
		method: "POST",
		headers: { Accept: "application/json", "X-Frappe-CSRF-Token": window.csrf_token },
		body,
	});
	const data = await res.json().catch(() => ({}));
	if (!res.ok) throw new Error(serverMessage(data) || res.statusText);
	return data.message;
}
