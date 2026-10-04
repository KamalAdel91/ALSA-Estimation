import { ref } from "vue";

// Chrome, Edge and Samsung Internet fire this once the app can be installed; keep it to show our own prompt.
export const installEvent = ref(null);

window.addEventListener("beforeinstallprompt", (e) => {
	e.preventDefault();
	installEvent.value = e;
});

window.addEventListener("appinstalled", () => {
	installEvent.value = null;
});

export const isStandalone = () =>
	window.matchMedia("(display-mode: standalone)").matches || window.navigator.standalone === true;

export const isIOS = () =>
	/iphone|ipad|ipod/i.test(navigator.userAgent) || (navigator.platform === "MacIntel" && navigator.maxTouchPoints > 1);
