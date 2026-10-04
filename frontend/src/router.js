import { createRouter, createWebHistory } from "vue-router";
import HomeView from "./views/HomeView.vue";
import ListView from "./views/ListView.vue";

export const router = createRouter({
	history: createWebHistory(`/${window.alsa_boot.route}`),
	routes: [
		{ path: "/", name: "home", component: HomeView },
		{ path: "/estimations", name: "list", component: ListView },
		{ path: "/:pathMatch(.*)*", redirect: "/" },
	],
	scrollBehavior: () => ({ top: 0 }),
});
