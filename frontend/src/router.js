import { createRouter, createWebHistory } from "vue-router";
import HomeView from "./views/HomeView.vue";

export const router = createRouter({
	history: createWebHistory(`/${window.alsa_boot.route}`),
	routes: [
		{ path: "/", name: "home", component: HomeView },
		{ path: "/:pathMatch(.*)*", redirect: "/" },
	],
});
