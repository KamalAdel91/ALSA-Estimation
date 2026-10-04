<script setup>
import { ref } from "vue";
import { call } from "../api.js";

const props = defineProps({
	estimation: { type: String, required: true },
	modified: { type: String, required: true },
	edit: { type: Object, required: true },
	dots: { type: Object, default: () => ({}) },
});
const emit = defineEmits(["cancel", "saved"]);

const workingDays = ref(props.edit.working_days_per_month);
const rows = ref(props.edit.rows.map((r) => ({ ...r })));
const saving = ref(false);
const error = ref("");

async function save() {
	saving.value = true;
	error.value = "";
	try {
		await call(
			"alsa_estimation.editing.save_rates",
			{
				name: props.estimation,
				working_days_per_month: workingDays.value,
				rows: rows.value,
				modified: props.modified,
			},
			{ write: true },
		);
		emit("saved");
	} catch (e) {
		error.value = e.message;
	} finally {
		saving.value = false;
	}
}
</script>

<template>
	<section class="card">
		<div class="row-between">
			<label class="total-label" for="rates-days">Working days per month</label>
			<input id="rates-days" v-model.number="workingDays" class="input input-short" type="number" inputmode="numeric" min="1" />
		</div>
	</section>
	<section v-for="(r, i) in rows" :key="r.designation" class="card">
		<div class="row-head">
			<span class="dot dot-lg" :style="{ background: dots[r.designation] || '#64748B' }"></span>
			<h2 class="row-title">{{ r.designation }}</h2>
		</div>
		<div class="field-grid">
			<div class="field">
				<label class="label" :for="`rate-basic-${i}`">Basic salary</label>
				<input :id="`rate-basic-${i}`" v-model.number="r.basic_salary" class="input" type="number" inputmode="decimal" min="0" step="0.01" />
			</div>
			<div class="field">
				<label class="label" :for="`rate-factor-${i}`">Factor</label>
				<input :id="`rate-factor-${i}`" v-model.number="r.factor" class="input" type="number" inputmode="decimal" min="0" step="0.01" />
			</div>
		</div>
	</section>
	<p v-if="error" class="error">{{ error }}</p>
	<div class="actions">
		<button type="button" class="btn-secondary" @click="emit('cancel')">Cancel</button>
		<button type="button" class="btn-primary" :disabled="saving" @click="save">
			{{ saving ? "Saving…" : "Save rates" }}
		</button>
	</div>
</template>
