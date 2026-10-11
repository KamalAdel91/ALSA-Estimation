<script setup>
defineProps({
	count: { type: Number, default: 3 },
	tiles: { type: Boolean, default: false },
});
</script>

<template>
	<div class="skel" aria-busy="true" aria-label="Loading">
		<div v-if="tiles" class="skel-tiles"></div>
		<div v-for="i in count" :key="i" class="skel-card">
			<div class="skel-line" style="width: 55%"></div>
			<div class="skel-line" style="width: 90%"></div>
			<div class="skel-line" style="width: 35%"></div>
		</div>
	</div>
</template>
