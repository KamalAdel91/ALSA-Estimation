<script setup>
import { computed } from "vue";
import { amount, when } from "../format.js";
import StateBadge from "./StateBadge.vue";

const props = defineProps({
	row: { type: Object, required: true },
	showHint: { type: Boolean, default: false },
});

const subtitle = computed(() => [props.row.title, props.row.project_type].filter(Boolean).join(", "));
</script>

<template>
	<RouterLink class="est-card" :to="{ name: 'estimation', params: { name: row.name } }">
		<div class="row-between">
			<span class="est-customer">{{ row.customer || row.name }}</span>
			<StateBadge :state="row.state" :tone="row.tone" />
		</div>
		<span v-if="subtitle" class="est-sub">{{ subtitle }}</span>
		<div class="est-meta">
			<span>{{ row.name }}, {{ when(row.modified) }}</span>
			<span v-if="row.total_cost" class="est-amount">{{ amount(row.total_cost) }}</span>
			<span v-else>Not priced yet</span>
		</div>
		<span v-if="showHint && row.hint" class="est-ticket" :data-tone="row.hint_tone || null">
			<span class="est-ticket-mark" aria-hidden="true"></span>
			<span class="est-ticket-text">{{ row.hint }}</span>
			<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
				<path d="M9 6l6 6-6 6" />
			</svg>
		</span>
	</RouterLink>
</template>
