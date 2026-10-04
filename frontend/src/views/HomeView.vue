<script setup>
import { onMounted, ref } from "vue";
import { call } from "../api.js";

const boot = window.alsa_boot;
const today = new Intl.DateTimeFormat("en-GB", { weekday: "long", day: "numeric", month: "long" }).format(new Date());
const loading = ref(true);
const error = ref("");
const info = ref(null);

onMounted(async () => {
	try {
		info.value = await call("alsa_estimation.api.ping");
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
		<section class="card">
			<p v-if="loading" class="muted">Connecting…</p>
			<p v-else-if="error" class="error">{{ error }}</p>
			<template v-else>
				<span class="label">Signed in as</span>
				<strong>{{ info.full_name }}</strong>
				<span class="label">Estimations you can open</span>
				<strong class="big">{{ info.estimations }}</strong>
			</template>
		</section>
	</main>
</template>
