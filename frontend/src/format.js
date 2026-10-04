const money = new Intl.NumberFormat("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 });

export function amount(value) {
	return money.format(Number(value) || 0);
}

// Frappe datetime ("2026-10-04 10:42:13.123456") as "Today, 10:42", "Yesterday", "Mon" or "4 Oct".
export function when(value) {
	if (!value) return "";
	const date = new Date(String(value).slice(0, 19).replace(" ", "T"));
	const now = new Date();
	const day = (d) => new Date(d.getFullYear(), d.getMonth(), d.getDate()).getTime();
	const days = Math.round((day(now) - day(date)) / 86400000);
	if (days <= 0) return `Today, ${date.toLocaleTimeString("en-GB", { hour: "2-digit", minute: "2-digit" })}`;
	if (days === 1) return "Yesterday";
	if (days < 7) return date.toLocaleDateString("en-GB", { weekday: "short" });
	return date.toLocaleDateString("en-GB", { day: "numeric", month: "short" });
}

export function number(value) {
	return (Number(value) || 0).toLocaleString("en-US", { maximumFractionDigits: 2 });
}

// A figure from the server: { value, kind: "money" | "number" | "percent" }.
export function figure(f) {
	if (f.kind === "percent") return `${number(f.value)}%`;
	if (f.kind === "number") return number(f.value);
	return amount(f.value);
}

export function date(value) {
	if (!value) return "";
	const d = new Date(`${String(value).slice(0, 10)}T00:00:00`);
	return d.toLocaleDateString("en-GB", { day: "numeric", month: "short", year: "numeric" });
}
