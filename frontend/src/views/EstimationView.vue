<script setup>
import { onMounted, ref } from "vue";
import { useRoute } from "vue-router";
import { call } from "../api.js";
import { amount, date, number, when } from "../format.js";
import { uploadFile } from "../upload.js";
import ActionSheet from "../components/ActionSheet.vue";
import PriceHero from "../components/PriceHero.vue";
import StateBadge from "../components/StateBadge.vue";
import TopBar from "../components/TopBar.vue";

const route = useRoute();
const name = route.params.name;
const est = ref(null);
const actions = ref([]);
const error = ref("");
const confirming = ref(null);
const uploading = ref(false);
const uploadError = ref("");

function target(section) {
	if (section.key === "rfq" || section.key === "cost") return { name: section.key, params: { name } };
	return { name: "section", params: { name, section: section.key } };
}

function buttonClass(action, i) {
	if (action.tone === "red") return "btn-danger";
	return i === 0 ? "btn-primary" : "btn-secondary";
}

async function load() {
	error.value = "";
	try {
		const [estimation, available] = await Promise.all([
			call("alsa_estimation.estimation.get_estimation", { name }),
			call("alsa_estimation.actions.get_actions", { name }),
		]);
		est.value = estimation;
		actions.value = available;
	} catch (e) {
		error.value = e.message;
	}
}

async function attach(event) {
	const file = event.target.files && event.target.files[0];
	event.target.value = "";
	if (!file) return;
	uploading.value = true;
	uploadError.value = "";
	try {
		const uploaded = await uploadFile(file, {
			doctype: "Project Estimation",
			docname: name,
			fieldname: "contract_no_prices",
		});
		await call(
			"alsa_estimation.actions.attach_contract",
			{ name, file_url: uploaded.file_url, modified: est.value.modified },
			{ write: true },
		);
		await load();
	} catch (e) {
		uploadError.value = e.message;
	} finally {
		uploading.value = false;
	}
}

async function done() {
	confirming.value = null;
	await load();
}

onMounted(load);
</script>

<template>
	<TopBar :title="name" :subtitle="est && est.opportunity ? `Opportunity ${est.opportunity}` : ''" :back="{ name: 'list' }">
		<StateBadge v-if="est" :state="est.state" :tone="est.tone" />
	</TopBar>
	<main class="page-body">
		<p v-if="error" class="error">{{ error }}</p>
		<p v-if="!est && !error" class="muted">Loading…</p>
		<template v-if="est">
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

			<RouterLink :to="{ name: 'cost', params: { name } }" class="summary" :class="{ 'summary-price': est.price }">
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
				<div v-if="est.can_edit" class="upload-buttons">
					<label class="btn-secondary btn-small upload-btn">
						<input class="sr-only" type="file" accept="image/*" capture="environment" :disabled="uploading" @change="attach" />
						Take photo
					</label>
					<label class="btn-secondary btn-small upload-btn">
						<input class="sr-only" type="file" accept="image/*,application/pdf" :disabled="uploading" @change="attach" />
						{{ est.attachments.contract_no_prices ? "Replace file" : "Choose file" }}
					</label>
				</div>
				<p v-if="uploading" class="muted">Uploading the Contract (No Prices)…</p>
				<p v-if="uploadError" class="error">{{ uploadError }}</p>
			</section>
		</template>
	</main>
	<div v-if="est && actions.length" class="action-bar">
		<button
			v-for="(a, i) in actions"
			:key="a.action"
			type="button"
			:class="buttonClass(a, i)"
			@click="confirming = a"
		>
			{{ a.action }}
		</button>
	</div>
	<ActionSheet
		v-if="confirming"
		:estimation="name"
		:modified="est.modified"
		:action="confirming"
		:state="est.state"
		@close="confirming = null"
		@done="done"
	/>
</template>
