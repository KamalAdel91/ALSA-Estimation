<script setup>
import { computed, ref } from "vue";
import { call } from "../api.js";
import { amount } from "../format.js";
import Stepper from "./Stepper.vue";

const props = defineProps({
	estimation: { type: String, required: true },
	modified: { type: String, required: true },
	edit: { type: Object, required: true },
	dots: { type: Object, default: () => ({}) },
});
const emit = defineEmits(["cancel", "saved"]);

const basis = ref(props.edit.basis);
const rows = ref(props.edit.rows.map((r) => ({ ...r })));
const saving = ref(false);
const error = ref("");
const typed = computed(() => props.edit.typed_bases.includes(basis.value));

async function save() {
	saving.value = true;
	error.value = "";
	try {
		await call(
			"alsa_estimation.editing.save_accommodation",
			{ name: props.estimation, basis: basis.value, rows: rows.value, modified: props.modified },
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
	<fieldset class="card fieldset">
		<legend class="total-label">Accommodation basis</legend>
		<div class="segmented">
			<button
				v-for="b in edit.bases"
				:key="b"
				type="button"
				class="segment"
				:class="{ 'is-on': basis === b }"
				:aria-pressed="String(basis === b)"
				@click="basis = b"
			>
				{{ b }}
			</button>
		</div>
		<p class="muted">
			{{ typed ? "Type the monthly cost per person." : "The monthly cost per person comes from the basic salary when you save." }}
		</p>
	</fieldset>
	<section v-for="(r, i) in rows" :key="r.designation" class="card">
		<div class="row-head">
			<span class="dot dot-lg" :style="{ background: dots[r.designation] || '#64748B' }"></span>
			<h2 class="row-title">{{ r.designation }}</h2>
		</div>
		<div class="field-grid">
			<div class="field">
				<span class="label">Persons</span>
				<Stepper v-model="r.persons" :label="`${r.designation} persons`" :min="0" />
			</div>
			<div class="field">
				<template v-if="typed">
					<label class="label" :for="`acc-monthly-${i}`">Monthly per person</label>
					<input :id="`acc-monthly-${i}`" v-model.number="r.monthly_cost_per_person" class="input" type="number" inputmode="decimal" min="0" step="0.01" />
				</template>
				<template v-else>
					<span class="label">Monthly per person</span>
					<strong class="readonly-value">{{ amount(r.monthly_cost_per_person) }}</strong>
				</template>
			</div>
		</div>
	</section>
	<p v-if="error" class="error">{{ error }}</p>
	<div class="actions">
		<button type="button" class="btn-secondary" @click="emit('cancel')">Cancel</button>
		<button type="button" class="btn-primary" :disabled="saving" @click="save">
			{{ saving ? "Saving…" : "Save accommodation" }}
		</button>
	</div>
</template>
