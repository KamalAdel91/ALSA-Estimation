<script setup>
import { useRoute } from "vue-router";
import TabBar from "./components/TabBar.vue";

const route = useRoute();
</script>

<template>
	<div class="shell" :class="{ 'has-tabs': route.meta.tabs }">
		<RouterView :key="route.path" />
	</div>
	<TabBar v-if="route.meta.tabs" />
</template>
