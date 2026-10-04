import { createRouter, createWebHistory } from "vue-router";
import CostView from "./views/CostView.vue";
import EstimationView from "./views/EstimationView.vue";
import HomeView from "./views/HomeView.vue";
import ListView from "./views/ListView.vue";
import RfqView from "./views/RfqView.vue";
import SectionView from "./views/SectionView.vue";

export const router = createRouter({
	history: createWebHistory(`/${window.alsa_boot.route}`),
	routes: [
		{ path: "/", name: "home", component: HomeView, meta: { tabs: true } },
		{ path: "/estimations", name: "list", component: ListView, meta: { tabs: true } },
		{ path: "/estimation/:name", name: "estimation", component: EstimationView },
		{ path: "/estimation/:name/rfq", name: "rfq", component: RfqView },
		{ path: "/estimation/:name/cost", name: "cost", component: CostView },
		{ path: "/estimation/:name/:section", name: "section", component: SectionView },
		{ path: "/:pathMatch(.*)*", redirect: "/" },
	],
	scrollBehavior: () => ({ top: 0 }),
});
