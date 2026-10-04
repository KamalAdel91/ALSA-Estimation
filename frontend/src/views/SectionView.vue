<script setup>
import { onMounted, ref } from "vue";
import { useRoute } from "vue-router";
import { call } from "../api.js";
import { figure } from "../format.js";
import TopBar from "../components/TopBar.vue";

const route = useRoute();
const data = ref(null);
const error = ref("");

onMounted(async () => {
	try {
		data.value = await call("alsa_estimation.estimation.get_section", {
			name: route.params.name,
			section: route.params.section,
		});
	} catch (e) {
		error.value = e.message;
	}
});
</script>

<template>
	<TopBar
		:title="data ? data.title : ''"
		:subtitle="route.params.name"
		:back="{ name: 'estimation', params: { name: route.params.name } }"
	/>
	<main class="page-body">
		<p v-if="error" class="error">{{ error }}</p>
		<p v-else-if="!data" class="muted">Loading…</p>
		<template v-else>
			<dl v-if="data.facts.length" class="card facts">
				<div v-for="f in data.facts" :key="f.label">
					<dt>{{ f.label }}</dt>
					<dd>{{ f.value }}</dd>
				</div>
			</dl>
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
			</article>
			<p v-if="!data.rows.length" class="muted">{{ data.empty }}</p>
			<section class="card totals">
				<div v-for="t in data.totals" :key="t.label" class="row-between">
					<span class="total-label">{{ t.label }}</span>
					<strong class="total-value" :class="t.tone ? `is-${t.tone}` : ''">{{ figure(t) }}</strong>
				</div>
			</section>
		</template>
	</main>
</template>
