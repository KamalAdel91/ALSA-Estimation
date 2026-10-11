<script setup>
import { useRoute } from "vue-router";
import BrandBar from "./components/BrandBar.vue";
import InstallPrompt from "./components/InstallPrompt.vue";
import TabBar from "./components/TabBar.vue";

const route = useRoute();
</script>

<template>
	<div class="shell" :class="{ 'has-tabs': route.meta.tabs }">
		<BrandBar v-if="route.meta.tabs" />
		<RouterView :key="route.path" />
	</div>
	<InstallPrompt v-if="route.meta.tabs" />
	<TabBar v-if="route.meta.tabs" />
</template>
