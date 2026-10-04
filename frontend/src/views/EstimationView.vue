<script setup>
import { onMounted, ref } from "vue";
import { useRoute } from "vue-router";
import { call } from "../api.js";
import { amount, date, number, when } from "../format.js";
import PriceHero from "../components/PriceHero.vue";
import StateBadge from "../components/StateBadge.vue";
import TopBar from "../components/TopBar.vue";

const route = useRoute();
const est = ref(null);
const error = ref("");

function target(section) {
	const name = route.params.name;
	if (section.key === "rfq" || section.key === "cost") return { name: section.key, params: { name } };
	return { name: "section", params: { name, section: section.key } };
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
	<TopBar
		:title="route.params.name"
		:subtitle="est && est.opportunity ? `Opportunity ${est.opportunity}` : ''"
		:back="{ name: 'list' }"
	>
		<StateBadge v-if="est" :state="est.state" :tone="est.tone" />
	</TopBar>
	<main class="page-body">
		<p v-if="error" class="error">{{ error }}</p>
		<p v-else-if="!est" class="muted">Loading…</p>
		<template v-else>
			<section class="card">
				<div>
					<h2 class="est-title">{{ est.customer }}</h2>
					<p v-if="est.title || est.project_type" class="muted">
						{{ [est.title, est.project_type].filter(Boolean).join(", ") }}
					</p>
				</div>
				<dl class="facts">
					<div>
						<dt>Currency</dt>
						<dd>{{ est.currency }}</dd>
					</div>
					<div>
						<dt>Rate</dt>
						<dd>{{ number(est.conversion_rate) }}</dd>
					</div>
					<div>
						<dt>Estimation date</dt>
						<dd>{{ date(est.estimation_date) }}</dd>
					</div>
				</dl>
			</section>

			<section v-if="est.revision" class="banner banner-warn" aria-label="Revision from Sales">
				<strong>Sales asked for a revision</strong>
				<span>{{ est.revision.text }}</span>
				<span class="banner-when">{{ when(est.revision.when) }}</span>
			</section>
			<p v-else-if="est.hint" class="banner">{{ est.hint }}</p>

			<RouterLink
				:to="{ name: 'cost', params: { name: est.name } }"
				class="summary"
				:class="{ 'summary-price': est.price }"
			>
				<PriceHero v-if="est.price" :price="est.price" :currency="est.currency" />
				<div class="summary-kpis">
					<div>
						<span>Total cost</span>
						<strong class="is-cost">{{ amount(est.totals.total_cost) }}</strong>
					</div>
					<div v-if="est.price">
						<span>Margin {{ number(est.price.margin_percentage) }}%</span>
						<strong class="is-margin">{{ amount(est.price.margin_amount) }}</strong>
					</div>
					<div>
						<span>Duration</span>
						<strong>{{ number(est.totals.total_work_days) }} days</strong>
					</div>
				</div>
			</RouterLink>

			<nav class="sections" aria-label="Estimation sections">
				<RouterLink v-for="s in est.sections" :key="s.key" :to="target(s)" class="section-row">
					<span class="section-label">{{ s.label }}</span>
					<span v-if="s.text" class="muted">{{ s.text }}</span>
					<span v-else class="section-amount">{{ amount(s.amount) }}</span>
					<svg class="chev" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
						<path d="M9 6l6 6-6 6" />
					</svg>
				</RouterLink>
			</nav>

			<section class="card">
				<h2 class="section-title">Attachments</h2>
				<div class="attachment">
					<span class="attachment-icon" aria-hidden="true">
						<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round">
							<path d="M14 3H7a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V8z" />
							<path d="M14 3v5h5" />
						</svg>
					</span>
					<div class="attachment-text">
						<span class="attachment-name">Signed contract</span>
						<a v-if="est.attachments.signed_contract" :href="est.attachments.signed_contract" target="_blank" rel="noopener">Open</a>
						<span v-else class="muted">Arrives when Sales marks the Opportunity Closed Won</span>
					</div>
				</div>
				<div class="attachment">
					<span class="attachment-icon" aria-hidden="true">
						<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round">
							<path d="M14 3H7a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V8z" />
							<path d="M14 3v5h5" />
						</svg>
					</span>
					<div class="attachment-text">
						<span class="attachment-name">Contract (No Prices)</span>
						<a v-if="est.attachments.contract_no_prices" :href="est.attachments.contract_no_prices" target="_blank" rel="noopener">Open</a>
						<span v-else class="muted">Needed before Handover to Planning</span>
					</div>
				</div>
			</section>
		</template>
	</main>
</template>
