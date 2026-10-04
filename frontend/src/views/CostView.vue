<script setup>
import { onMounted, ref } from "vue";
import { useRoute } from "vue-router";
import { call } from "../api.js";
import { amount, number } from "../format.js";
import PriceHero from "../components/PriceHero.vue";
import TopBar from "../components/TopBar.vue";

const route = useRoute();
const est = ref(null);
const error = ref("");

function pct(value) {
	const total = est.value ? Number(est.value.totals.total_cost) : 0;
	return total ? (Number(value) / total) * 100 : 0;
}

onMounted(async () => {
	try {
		est.value = await call("alsa_estimation.estimation.get_estimation", { name: route.params.name });
	} catch (e) {
		error.value = e.message;
	}
});
</script>

<template>
	<TopBar title="Cost & price" :subtitle="route.params.name" :back="{ name: 'estimation', params: { name: route.params.name } }" />
	<main class="page-body">
		<p v-if="error" class="error">{{ error }}</p>
		<p v-else-if="!est" class="muted">Loading…</p>
		<template v-else>
			<section v-if="est.price" class="summary summary-price">
				<PriceHero :price="est.price" :currency="est.currency" />
			</section>
			<div class="kpis">
				<div class="kpi">
					<span>Total cost</span>
					<strong class="is-cost">{{ amount(est.totals.total_cost) }}</strong>
					<small v-if="est.totals.cost_per_day">{{ amount(est.totals.cost_per_day) }} a team day</small>
				</div>
				<div v-if="est.price" class="kpi">
					<span>Margin</span>
					<strong class="is-margin">{{ amount(est.price.margin_amount) }}</strong>
					<small>{{ number(est.price.margin_percentage) }}% of cost</small>
				</div>
				<div class="kpi">
					<span>Duration</span>
					<strong>{{ number(est.totals.total_work_days) }} days</strong>
					<small>{{ number(est.totals.duration_months) }} months</small>
				</div>
			</div>
			<section class="card">
				<div class="row-between">
					<h2 class="section-title">Cost breakdown</h2>
					<strong class="is-cost">{{ amount(est.totals.total_cost) }}</strong>
				</div>
				<div class="bd">
					<div class="bd-line">
						<span class="bd-label"><span class="dot dot-manpower"></span>Manpower</span>
						<span>{{ amount(est.totals.manpower_cost) }}</span>
						<span class="bd-pct">{{ number(pct(est.totals.manpower_cost)) }}%</span>
					</div>
					<div class="bar" aria-hidden="true">
						<span class="bar-fill bar-manpower" :style="{ width: `${Math.min(100, pct(est.totals.manpower_cost))}%` }"></span>
					</div>
				</div>
				<div class="bd">
					<div class="bd-line">
						<span class="bd-label"><span class="dot dot-other"></span>Other costs</span>
						<span>{{ amount(est.totals.other_cost_total) }}</span>
						<span class="bd-pct">{{ number(pct(est.totals.other_cost_total)) }}%</span>
					</div>
					<div class="bar" aria-hidden="true">
						<span class="bar-fill bar-other" :style="{ width: `${Math.min(100, pct(est.totals.other_cost_total))}%` }"></span>
					</div>
				</div>
				<div class="bd-subs">
					<div v-for="b in est.breakdown" :key="b.label" class="bd-line">
						<span class="bd-label">{{ b.label }}</span>
						<span>{{ amount(b.amount) }}</span>
						<span class="bd-pct">{{ number(pct(b.amount)) }}%</span>
					</div>
				</div>
				<div class="bd-line bd-total">
					<span class="bd-label">Total cost</span>
					<span class="is-cost">{{ amount(est.totals.total_cost) }}</span>
					<span class="bd-pct">100%</span>
				</div>
			</section>
		</template>
	</main>
</template>
