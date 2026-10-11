<script setup>
import { computed, onMounted, ref } from "vue";
import { call } from "../api.js";
import AccountSheet from "../components/AccountSheet.vue";
import EstimationCard from "../components/EstimationCard.vue";
import PullIndicator from "../components/PullIndicator.vue";
import SkeletonCards from "../components/SkeletonCards.vue";
import { usePullRefresh } from "../pull.js";

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
const account = ref(false);

const loading = ref(true);
const loaded = ref(false);
const error = ref("");
const home = ref({ cards: [], action: [], recent: [] });
const rows = computed(() => (home.value.action.length ? home.value.action : home.value.recent));

// Every card counts estimations, so the word only takes room on a phone-width tile.
function short(label) {
	const s = String(label || "")
		.replace(/\bestimations?\b/gi, "")
		.replace(/\s{2,}/g, " ")
		.trim();
	return s ? s[0].toUpperCase() + s.slice(1) : label;
}

async function load() {
	error.value = "";
	try {
		home.value = await call("alsa_estimation.api.get_home");
		loaded.value = true;
	} catch (e) {
		error.value = e.message;
	} finally {
		loading.value = false;
	}
}

const { pull, busy, ready } = usePullRefresh(load);
onMounted(load);
</script>

<template>
	<PullIndicator :pull="pull" :busy="busy" :ready="ready" />
	<header class="page-head">
		<div class="head-row">
			<img v-if="logoOk" :src="boot.logo" :alt="boot.company || boot.title" class="head-logo" @error="logoOk = false" />
			<span v-else></span>
			<button type="button" class="head-avatar-btn" aria-label="Account and appearance" @click="account = true">
				<img v-if="imageOk" :src="boot.user_image" alt="" class="head-avatar" @error="imageOk = false" />
				<span v-else class="head-avatar head-initials">{{ initials }}</span>
			</button>
		</div>
		<p class="muted">{{ today }}</p>
		<h1>{{ greeting }}, {{ firstName }}</h1>
	</header>
	<main class="page-body">
		<p v-if="error" class="error">{{ error }}</p>
		<SkeletonCards v-if="loading && !loaded" :count="3" tiles />
		<template v-else-if="loaded">
			<div v-if="home.cards.length" class="tiles">
				<RouterLink
					v-for="card in home.cards"
					:key="card.name"
					class="tile"
					:to="{ name: 'list', query: { card: card.name } }"
				>
					<span class="tile-value">{{ card.value }}</span>
					<span class="tile-label">{{ short(card.label) }}</span>
				</RouterLink>
			</div>
			<section class="stack">
				<h2 class="section-title">{{ home.action.length ? "Needs your action" : "Recently updated" }}</h2>
				<EstimationCard v-for="row in rows" :key="row.name" :row="row" show-hint />
				<p v-if="!rows.length" class="muted">No estimations yet.</p>
			</section>
		</template>
	</main>
	<AccountSheet v-if="account" :name="name" :email="boot.user" @close="account = false" />
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
	display: block;
	width: 40px;
	height: 40px;
	border-radius: 50%;
	object-fit: cover;
}
.head-initials {
	display: grid;
	place-items: center;
	background: var(--btn);
	color: var(--btn-text);
	font-weight: 700;
	font-size: 15px;
}
</style>
