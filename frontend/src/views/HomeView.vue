<script setup>
import { computed, onMounted, ref } from "vue";
import { call } from "../api.js";
import EstimationCard from "../components/EstimationCard.vue";

const boot = window.alsa_boot;
const now = new Date();
const today = new Intl.DateTimeFormat("en-GB", { weekday: "long", day: "numeric", month: "long" }).format(now);

// Header: company logo, the employee's avatar, and a greeting by first name.
const name = boot.full_name || (boot.user || "").split("@")[0];
const firstName = name.split(/\s+/)[0];
const hour = now.getHours();
const greeting = hour < 12 ? "Good morning" : hour < 17 ? "Good afternoon" : "Good evening";
const initials = name
	.split(/[\s._-]+/)
	.filter(Boolean)
	.slice(0, 2)
	.map((w) => w[0].toUpperCase())
	.join("");
const logoOk = ref(Boolean(boot.logo));
const imageOk = ref(Boolean(boot.user_image));

const loading = ref(true);
const error = ref("");
const home = ref({ cards: [], action: [], recent: [] });
const rows = computed(() => (home.value.action.length ? home.value.action : home.value.recent));

onMounted(async () => {
	try {
		home.value = await call("alsa_estimation.api.get_home");
	} catch (e) {
		error.value = e.message;
	} finally {
		loading.value = false;
	}
});
</script>

<template>
	<header class="page-head">
		<div class="head-row">
			<img v-if="logoOk" :src="boot.logo" :alt="boot.company || boot.title" class="head-logo" @error="logoOk = false" />
			<span v-else></span>
			<img v-if="imageOk" :src="boot.user_image" :alt="name" class="head-avatar" @error="imageOk = false" />
			<span v-else class="head-avatar head-initials" :title="name">{{ initials }}</span>
		</div>
		<p class="muted">{{ today }}</p>
		<h1>{{ greeting }}, {{ firstName }}</h1>
	</header>
	<main class="page-body">
		<p v-if="loading" class="muted">Loading…</p>
		<p v-else-if="error" class="error">{{ error }}</p>
		<template v-else>
			<div v-if="home.cards.length" class="tiles">
				<RouterLink
					v-for="card in home.cards"
					:key="card.name"
					class="tile"
					:to="{ name: 'list', query: { card: card.name } }"
				>
					<span class="tile-value">{{ card.value }}</span>
					<span class="tile-label">{{ card.label }}</span>
				</RouterLink>
			</div>
			<section class="stack">
				<h2 class="section-title">{{ home.action.length ? "Needs your action" : "Recently updated" }}</h2>
				<EstimationCard v-for="row in rows" :key="row.name" :row="row" show-hint />
				<p v-if="!rows.length" class="muted">No estimations yet.</p>
			</section>
		</template>
	</main>
</template>

<style scoped>
.head-row {
	display: flex;
	align-items: center;
	justify-content: space-between;
	min-height: 40px;
	margin-bottom: 14px;
}
.head-logo {
	height: 40px;
	max-width: 160px;
	object-fit: contain;
}
.head-avatar {
	width: 40px;
	height: 40px;
	border-radius: 50%;
	object-fit: cover;
	flex-shrink: 0;
}
.head-initials {
	display: grid;
	place-items: center;
	background: var(--ink);
	color: #fff;
	font-weight: 700;
	font-size: 15px;
}
</style>
