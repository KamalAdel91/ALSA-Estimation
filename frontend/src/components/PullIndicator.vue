<script setup>
defineProps({
	pull: { type: Number, default: 0 },
	busy: { type: Boolean, default: false },
	ready: { type: Boolean, default: false },
});
</script>

<template>
	<div
		v-show="pull > 0 || busy"
		class="pull"
		:class="{ 'is-ready': ready, 'is-busy': busy }"
		:style="{ transform: `translateY(${pull - 44}px)`, opacity: busy ? 1 : Math.min(1, pull / 40) }"
		aria-hidden="true"
	>
		<svg v-if="busy" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round">
			<path d="M21 12a9 9 0 1 1-6.2-8.6" />
		</svg>
		<svg v-else width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
			<path d="M12 5v14M6 13l6 6 6-6" />
		</svg>
	</div>
</template>
