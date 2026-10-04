<script setup>
import { computed } from "vue";
import { amount, when } from "../format.js";
import StateBadge from "./StateBadge.vue";

const props = defineProps({
	row: { type: Object, required: true },
	showHint: { type: Boolean, default: false },
});

// Until the estimation screen is built, a card opens the estimation on the desk.
const href = computed(() => `/app/project-estimation/${encodeURIComponent(props.row.name)}`);
const subtitle = computed(() => [props.row.title, props.row.project_type].filter(Boolean).join(", "));
</script>

<template>
	<a class="est-card" :href="href">
		<div class="row-between">
			<span class="est-customer">{{ row.customer || row.name }}</span>
			<StateBadge :state="row.state" :tone="row.tone" />
		</div>
		<span v-if="subtitle" class="muted">{{ subtitle }}</span>
		<span v-if="showHint && row.hint" class="hint" :class="row.hint_tone ? `hint-${row.hint_tone}` : ''">
			{{ row.hint }}
		</span>
		<div class="row-between est-foot">
			<span class="muted">{{ row.name }}, {{ when(row.modified) }}</span>
			<span v-if="row.total_cost" class="est-amount">{{ amount(row.total_cost) }}</span>
			<span v-else class="muted">Not priced yet</span>
		</div>
	</a>
</template>
