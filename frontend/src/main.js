import { createApp } from "vue";
import App from "./App.vue";
import { router } from "./router.js";
import "./install.js";
import "./style.css";

createApp(App).use(router).mount("#app");

// The service worker makes the app installable and shows its notifications; browsers allow it on HTTPS only.
if ("serviceWorker" in navigator && window.isSecureContext) {
	navigator.serviceWorker.register("/alsa-estimation-sw.js", { scope: `/${window.alsa_boot.route}` }).catch(() => {});
}
