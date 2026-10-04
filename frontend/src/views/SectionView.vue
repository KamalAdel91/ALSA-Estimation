<script setup>
import { computed, onMounted, ref } from "vue";
import { useRoute } from "vue-router";
import { call } from "../api.js";
import { figure } from "../format.js";
import RatesEditor from "../components/RatesEditor.vue";
import ScopeEditor from "../components/ScopeEditor.vue";
import TopBar from "../components/TopBar.vue";

const route = useRoute();
const section = route.params.section;
const data = ref(null);
const error = ref("");
const trades = ref([]);
const editingRow = ref(null);
const editingRates = ref(false);

const canEdit = computed(() => Boolean(data.value && data.value.can_edit));
const dots = computed(() => Object.fromEntries((data.value ? data.value.rows : []).map((r) => [r.title, r.dot])));

async function load() {
	error.value = "";
	try {
		data.value = await call("alsa_estimation.estimation.get_section", { name: route.params.name, section });
	} catch (e) {
		error.value = e.message;
	}
}

async function editScope(row) {
	try {
		if (!trades.value.length) trades.value = await call("alsa_estimation.editing.get_trades");
		editingRow.value = row;
	} catch (e) {
		error.value = e.message;
	}
}

async function saved() {
	editingRow.value = null;
	editingRates.value = false;
	await load();
}

onMounted(load);
</script>

<template>
	<TopBar
		:title="data ? data.title : ''"
		:subtitle="route.params.name"
		:back="{ name: 'estimation', params: { name: route.params.name } }"
	/>
	<main class="page-body">
		<p v-if="error" class="error">{{ error }}</p>
		<p v-if="!data && !error" class="muted">Loading…</p>
		<template v-if="data">
			<RatesEditor
				v-if="editingRates"
				:estimation="data.name"
				:modified="data.modified"
				:edit="data.edit"
				:dots="dots"
				@cancel="editingRates = false"
				@saved="saved"
			/>
			<template v-else>
				<dl v-if="data.facts.length" class="card facts">
					<div v-for="f in data.facts" :key="f.label">
						<dt>{{ f.label }}</dt>
						<dd>{{ f.value }}</dd>
					</div>
				</dl>
				<button v-if="canEdit && section === 'rates'" type="button" class="btn-primary" @click="editingRates = true">
					Edit rates
				</button>
				<article v-for="(row, i) in data.rows" :key="i" class="card">
					<div class="row-between row-top">
						<div class="row-head">
							<span v-if="row.dot" class="dot dot-lg" :style="{ background: row.dot }"></span>
							<div>
								<h2 class="row-title">{{ row.title }}</h2>
								<span v-if="row.subtitle" class="muted">{{ row.subtitle }}</span>
							</div>
						</div>
						<span v-if="row.badge" class="badge" :class="`tone-${row.badge.tone}`">{{ row.badge.text }}</span>
						<strong v-else-if="row.aside" class="row-aside">{{ row.aside }}</strong>
					</div>
					<div v-if="row.chips && row.chips.length" class="trade-chips">
						<span v-for="c in row.chips" :key="c.text" class="trade-chip">
							<span class="dot" :style="{ background: c.dot }"></span>{{ c.text }} × {{ c.count }}
						</span>
					</div>
					<div class="figures">
						<div v-for="f in row.figures" :key="f.label" class="figure">
							<span>{{ f.label }}</span>
							<strong :class="f.tone ? `is-${f.tone}` : ''">{{ figure(f) }}</strong>
						</div>
					</div>
					<button
						v-if="canEdit && section === 'scope'"
						type="button"
						class="btn-secondary btn-small"
						@click="editScope(row)"
					>
						Edit days and crew
					</button>
				</article>
				<p v-if="!data.rows.length" class="muted">{{ data.empty }}</p>
				<section class="card totals">
					<div v-for="t in data.totals" :key="t.label" class="row-between">
						<span class="total-label">{{ t.label }}</span>
						<strong class="total-value" :class="t.tone ? `is-${t.tone}` : ''">{{ figure(t) }}</strong>
					</div>
				</section>
			</template>
		</template>
	</main>
	<ScopeEditor
		v-if="editingRow"
		:estimation="data.name"
		:modified="data.modified"
		:row="editingRow"
		:trades="trades"
		@close="editingRow = null"
		@saved="saved"
	/>
</template>
