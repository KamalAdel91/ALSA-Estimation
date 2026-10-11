<script setup>
import { computed } from "vue";
import { FLOW, stepRoute } from "../flow.js";

// Previous and next step, docked above the tab bar; the ends lead back to the overview.
const props = defineProps({
	estimation: { type: String, required: true },
	current: { type: String, required: true },
});

const i = computed(() => FLOW.findIndex((f) => f.key === props.current));
const overview = computed(() => ({ name: "estimation", params: { name: props.estimation } }));
const prev = computed(() =>
	i.value > 0
		? { to: stepRoute(props.estimation, FLOW[i.value - 1].key), caption: `Step ${i.value}`, label: FLOW[i.value - 1].label }
		: { to: overview.value, caption: "Back to", label: "Overview" },
);
const next = computed(() =>
	i.value >= 0 && i.value < FLOW.length - 1
		? { to: stepRoute(props.estimation, FLOW[i.value + 1].key), caption: `Step ${i.value + 2}`, label: FLOW[i.value + 1].label }
		: { to: overview.value, caption: "Done, back to", label: "Overview" },
);
const progress = computed(() => `${((i.value + 1) / FLOW.length) * 100}%`);
</script>

<template>
	<template v-if="i >= 0">
		<div class="pager-space" aria-hidden="true"></div>
		<nav class="pager-dock" :aria-label="`Step ${i + 1} of ${FLOW.length}`">
			<span class="pager-progress" aria-hidden="true"><span :style="{ width: progress }"></span></span>
			<RouterLink :to="prev.to" replace class="dock-btn">
				<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
					<path d="M15 6l-6 6 6 6" />
				</svg>
				<span class="dock-text">
					<small>{{ prev.caption }}</small>
					<span>{{ prev.label }}</span>
				</span>
			</RouterLink>
			<RouterLink :to="next.to" replace class="dock-btn dock-next">
				<span class="dock-text">
					<small>{{ next.caption }}</small>
					<span>{{ next.label }}</span>
				</span>
				<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
					<path d="M9 6l6 6-6 6" />
				</svg>
			</RouterLink>
		</nav>
	</template>
</template>
