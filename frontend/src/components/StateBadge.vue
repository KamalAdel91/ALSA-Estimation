<script setup>
defineProps({
	state: { type: String, default: "" },
	tone: { type: String, default: "gray" },
});
</script>

<template>
	<span class="badge" :class="`tone-${tone}`">{{ state }}</span>
</template>
