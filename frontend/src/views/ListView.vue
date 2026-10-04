<script setup>
import { onMounted, ref, watch } from "vue";
import { useRoute, useRouter } from "vue-router";
import { call } from "../api.js";
import EstimationCard from "../components/EstimationCard.vue";

const route = useRoute();
const router = useRouter();
const rows = ref([]);
const states = ref([]);
const more = ref(false);
const loading = ref(false);
const error = ref("");
const search = ref(route.query.q || "");
let timer;

async function load(append = false) {
	loading.value = true;
	error.value = "";
	try {
		const data = await call("alsa_estimation.api.get_estimations", {
			state: route.query.state,
			card: route.query.card,
			search: route.query.q,
			start: append ? rows.value.length : 0,
		});
		rows.value = append ? [...rows.value, ...data.rows] : data.rows;
		states.value = data.states;
		more.value = data.more;
	} catch (e) {
		error.value = e.message;
	} finally {
		loading.value = false;
	}
}

function pick(state) {
	router.replace({ query: { q: route.query.q, state: state || undefined } });
}

watch(search, (value) => {
	clearTimeout(timer);
	timer = setTimeout(() => router.replace({ query: { ...route.query, q: value.trim() || undefined } }), 300);
});
watch(
	() => [route.query.state, route.query.card, route.query.q],
	() => load(),
);
onMounted(() => load());
</script>

<template>
	<header class="page-head list-head">
		<h1>Estimations</h1>
		<label class="search">
			<span class="sr-only">Search estimations</span>
			<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
				<circle cx="11" cy="11" r="7" />
				<path d="M20 20l-3.5-3.5" />
			</svg>
			<input v-model="search" type="search" placeholder="Customer, opportunity or ID" />
		</label>
	</header>
	<div class="chips">
		<button
			v-if="route.query.card"
			type="button"
			class="chip is-on"
			:aria-label="`Clear filter: ${route.query.card}`"
			@click="pick('')"
		>
			{{ route.query.card }}
			<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" aria-hidden="true">
				<path d="M6 6l12 12M18 6L6 18" />
			</svg>
		</button>
		<template v-else>
			<button
				type="button"
				class="chip"
				:class="{ 'is-on': !route.query.state }"
				:aria-pressed="String(!route.query.state)"
				@click="pick('')"
			>
				All
			</button>
			<button
				v-for="s in states"
				:key="s.name"
				type="button"
				class="chip"
				:class="{ 'is-on': route.query.state === s.name }"
				:aria-pressed="String(route.query.state === s.name)"
				@click="pick(s.name)"
			>
				{{ s.name }}
			</button>
		</template>
	</div>
	<main class="page-body">
		<p v-if="error" class="error">{{ error }}</p>
		<EstimationCard v-for="row in rows" :key="row.name" :row="row" />
		<p v-if="!loading && !error && !rows.length" class="muted">No estimations match.</p>
		<button v-if="more" type="button" class="btn-secondary" :disabled="loading" @click="load(true)">
			Load more
		</button>
		<p v-if="loading" class="muted">Loading…</p>
	</main>
</template>
