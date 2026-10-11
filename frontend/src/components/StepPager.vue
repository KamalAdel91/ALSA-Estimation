<script setup>
import { computed } from "vue";
import { FLOW, stepRoute } from "../flow.js";

// Previous and next step of the estimation; the ends lead back to the overview.
const props = defineProps({
	estimation: { type: String, required: true },
	current: { type: String, required: true },
});

const i = computed(() => FLOW.findIndex((f) => f.key === props.current));
const overview = computed(() => ({ name: "estimation", params: { name: props.estimation } }));
const prev = computed(() =>
	i.value > 0
		? { to: stepRoute(props.estimation, FLOW[i.value - 1].key), label: FLOW[i.value - 1].label }
		: { to: overview.value, label: "Overview" },
);
const next = computed(() =>
	i.value >= 0 && i.value < FLOW.length - 1
		? { to: stepRoute(props.estimation, FLOW[i.value + 1].key), label: FLOW[i.value + 1].label }
		: { to: overview.value, label: "Overview" },
);
</script>

<template>
	<nav v-if="i >= 0" class="pager" aria-label="Estimation steps">
		<RouterLink :to="prev.to" replace class="pager-btn">
			<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
				<path d="M15 6l-6 6 6 6" />
			</svg>
			<span>
				<small>Previous</small>
				{{ prev.label }}
			</span>
		</RouterLink>
		<span class="pager-pos">{{ i + 1 }}/{{ FLOW.length }}</span>
		<RouterLink :to="next.to" replace class="pager-btn pager-next">
			<span>
				<small>Next</small>
				{{ next.label }}
			</span>
			<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
				<path d="M9 6l6 6-6 6" />
			</svg>
		</RouterLink>
	</nav>
</template>
