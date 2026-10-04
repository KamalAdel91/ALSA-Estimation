<script setup>
import { onBeforeUnmount, onMounted, ref, watch } from "vue";
import { useRoute } from "vue-router";
import { call } from "../api.js";

const route = useRoute();
const unread = ref(0);

async function refresh() {
	try {
		unread.value = await call("alsa_estimation.notify.unread_count");
	} catch (e) {
		unread.value = 0;
	}
}

watch(() => route.name, refresh);
onMounted(() => {
	refresh();
	window.addEventListener("alsa-alerts-read", refresh);
});
onBeforeUnmount(() => window.removeEventListener("alsa-alerts-read", refresh));
</script>

<template>
	<nav class="tabbar" aria-label="Main">
		<RouterLink :to="{ name: 'home' }" class="tab" exact-active-class="is-active">
			<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
				<path d="M3 10.5L12 3l9 7.5V20a1 1 0 0 1-1 1h-5v-6H9v6H4a1 1 0 0 1-1-1z" />
			</svg>
			<span>Home</span>
		</RouterLink>
		<RouterLink :to="{ name: 'list' }" class="tab" active-class="is-active">
			<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
				<path d="M9 6h11M9 12h11M9 18h11M4.5 6h.01M4.5 12h.01M4.5 18h.01" />
			</svg>
			<span>Estimations</span>
		</RouterLink>
		<RouterLink
			:to="{ name: 'alerts' }"
			class="tab"
			active-class="is-active"
			:aria-label="unread ? `Alerts, ${unread} unread` : 'Alerts'"
		>
			<span class="tab-icon">
				<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
					<path d="M6 9a6 6 0 1 1 12 0c0 6.5 2.5 8 2.5 8h-17S6 15.5 6 9z" />
					<path d="M10.3 20.5a2 2 0 0 0 3.4 0" />
				</svg>
				<span v-if="unread" class="tab-badge">{{ unread > 99 ? "99+" : unread }}</span>
			</span>
			<span>Alerts</span>
		</RouterLink>
	</nav>
</template>
