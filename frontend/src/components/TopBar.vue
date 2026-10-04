<script setup>
import { useRouter } from "vue-router";

const props = defineProps({
	title: { type: String, default: "" },
	subtitle: { type: String, default: "" },
	back: { type: [String, Object], required: true },
});
const router = useRouter();

// Back to the previous screen of the app; a screen opened from a link goes to its parent instead.
function goBack() {
	if (window.history.state && window.history.state.back) router.back();
	else router.push(props.back);
}
</script>

<template>
	<header class="topbar">
		<button type="button" class="icon-btn" aria-label="Back" @click="goBack">
			<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
				<path d="M15 6l-6 6 6 6" />
			</svg>
		</button>
		<div class="topbar-title">
			<h1>{{ title }}</h1>
			<span v-if="subtitle" class="muted">{{ subtitle }}</span>
		</div>
		<slot />
	</header>
</template>
