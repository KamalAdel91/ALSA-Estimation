<script setup>
import { computed, onMounted, ref } from "vue";
import { call } from "../api.js";
import EstimationCard from "../components/EstimationCard.vue";

const boot = window.alsa_boot;
const today = new Intl.DateTimeFormat("en-GB", { weekday: "long", day: "numeric", month: "long" }).format(new Date());
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
		<p class="muted">{{ today }}</p>
		<h1>{{ boot.title }}</h1>
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
