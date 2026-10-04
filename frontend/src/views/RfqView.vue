<script setup>
import { onMounted, ref } from "vue";
import { useRoute } from "vue-router";
import { call } from "../api.js";
import { number } from "../format.js";
import TopBar from "../components/TopBar.vue";

const route = useRoute();
const rfq = ref(null);
const error = ref("");

onMounted(async () => {
	try {
		rfq.value = await call("alsa_estimation.estimation.get_rfq", { name: route.params.name });
	} catch (e) {
		error.value = e.message;
	}
});
</script>

<template>
	<TopBar title="RFQ" :subtitle="route.params.name" :back="{ name: 'estimation', params: { name: route.params.name } }" />
	<main class="page-body">
		<p v-if="error" class="error">{{ error }}</p>
		<p v-else-if="!rfq" class="muted">Loading…</p>
		<p v-else-if="!rfq.opportunity" class="muted">This estimation has no Opportunity, so it has no RFQ.</p>
		<template v-else>
			<section class="card">
				<div>
					<span class="muted">{{ rfq.opportunity }}</span>
					<h2 class="est-title">{{ rfq.opportunity_name || rfq.opportunity }}</h2>
					<span class="muted">{{ rfq.customer }}</span>
				</div>
				<dl class="facts facts-rows">
					<div v-for="m in rfq.meta" :key="m[0]">
						<dt>{{ m[0] }}</dt>
						<dd>{{ m[1] || "Not set" }}</dd>
					</div>
				</dl>
			</section>
			<h2 class="section-title">RFQ items</h2>
			<div class="list-card">
				<div v-for="(row, i) in rfq.rows" :key="i" class="list-row">
					<div class="list-main">
						<span class="list-title">{{ row.equipment }}</span>
						<span v-if="row.description" class="muted">{{ row.description }}</span>
					</div>
					<span class="list-aside">Qty {{ number(row.quantity) }}</span>
				</div>
				<p v-if="!rfq.rows.length" class="list-empty muted">No RFQ items.</p>
			</div>
			<p class="muted">Read-only. Sales owns the RFQ on the Opportunity.</p>
		</template>
	</main>
</template>
