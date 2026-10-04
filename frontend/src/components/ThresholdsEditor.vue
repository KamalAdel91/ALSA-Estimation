<script setup>
import { ref } from "vue";
import { call } from "../api.js";

const props = defineProps({
	estimation: { type: String, required: true },
	modified: { type: String, required: true },
	edit: { type: Object, required: true },
});
const emit = defineEmits(["cancel", "saved"]);

const rows = ref(props.edit.rows.map((r) => ({ ...r })));
const saving = ref(false);
const error = ref("");

async function save() {
	saving.value = true;
	error.value = "";
	try {
		await call(
			"alsa_estimation.editing.save_thresholds",
			{ name: props.estimation, rows: rows.value, modified: props.modified },
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
		<p class="muted">Warn at this share of each category's estimated amount.</p>
		<div v-for="(r, i) in rows" :key="r.budget_category" class="edit-row">
			<label class="edit-row-title" :for="`threshold-${i}`">{{ r.budget_category }}</label>
			<div class="inline-field">
				<input :id="`threshold-${i}`" v-model.number="r.warning_threshold_percentage" class="input input-short" type="number" inputmode="decimal" min="0" max="100" step="1" />
				<span class="total-label">%</span>
			</div>
		</div>
		<p v-if="!rows.length" class="muted">No budget rows yet.</p>
	</section>
	<p v-if="error" class="error">{{ error }}</p>
	<div class="actions">
		<button type="button" class="btn-secondary" @click="emit('cancel')">Cancel</button>
		<button type="button" class="btn-primary" :disabled="saving" @click="save">
			{{ saving ? "Saving…" : "Save warning levels" }}
		</button>
	</div>
</template>
