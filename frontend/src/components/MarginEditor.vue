<script setup>
import { computed, ref } from "vue";
import { call } from "../api.js";
import { amount } from "../format.js";

const props = defineProps({
	estimation: { type: String, required: true },
	modified: { type: String, required: true },
	value: { type: Number, default: 0 },
	cost: { type: Number, default: 0 },
	currency: { type: String, default: "" },
});
const emit = defineEmits(["saved"]);

const margin = ref(props.value);
const saving = ref(false);
const error = ref("");

// A preview only: the server works out the saved price.
const preview = computed(() => (Number(props.cost) || 0) * (1 + (Number(margin.value) || 0) / 100));

async function save() {
	saving.value = true;
	error.value = "";
	try {
		await call(
			"alsa_estimation.editing.save_margin",
			{ name: props.estimation, margin_percentage: margin.value, modified: props.modified },
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
			<div>
				<label class="total-label" for="margin-percentage">Margin</label>
				<p class="muted">Percent of total cost</p>
			</div>
			<div class="inline-field">
				<input id="margin-percentage" v-model.number="margin" class="input input-short" type="number" inputmode="decimal" min="0" step="0.01" />
				<span class="total-label">%</span>
			</div>
		</div>
		<p v-if="margin !== value && cost" class="muted">
			New price about <strong class="is-price">{{ currency }} {{ amount(preview) }}</strong>
		</p>
		<p v-if="error" class="error">{{ error }}</p>
		<button v-if="margin !== value" type="button" class="btn-primary" :disabled="saving" @click="save">
			{{ saving ? "Saving…" : "Save margin" }}
		</button>
	</section>
</template>
