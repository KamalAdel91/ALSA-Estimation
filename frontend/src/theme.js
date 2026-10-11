// The appearance the user picked on this phone: "auto" follows the phone, or "light" / "dark".
const KEY = "alsa-theme";

export function getTheme() {
	try {
		return localStorage.getItem(KEY) || "auto";
	} catch (e) {
		return "auto";
	}
}

export function applyTheme(theme) {
	const root = document.documentElement;
	if (theme === "light" || theme === "dark") root.dataset.theme = theme;
	else delete root.dataset.theme;
}

export function setTheme(theme) {
	try {
		if (theme === "auto") localStorage.removeItem(KEY);
		else localStorage.setItem(KEY, theme);
	} catch (e) {
		// storage blocked: the choice lasts until the app closes
	}
	applyTheme(theme);
}

applyTheme(getTheme());
