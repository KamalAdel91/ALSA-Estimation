<script setup>
import { onMounted, ref } from "vue";
import { call } from "../api.js";

const props = defineProps({
	estimation: { type: String, required: true },
	modified: { type: String, required: true },
	edit: { type: Object, required: true },
});
const emit = defineEmits(["cancel", "saved"]);

const rows = ref(props.edit.rows.map((r) => ({ ...r })));
const categories = ref([]);
const saving = ref(false);
const error = ref("");

function add() {
	rows.value.push({ description: "", budget_category: "", cost: 0 });
}

async function save() {
	saving.value = true;
	error.value = "";
	try {
		await call(
			"alsa_estimation.editing.save_other_costs",
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

onMounted(async () => {
	try {
		categories.value = await call("alsa_estimation.editing.get_options", { kind: "budget_category" });
	} catch (e) {
		error.value = e.message;
	}
});
</script>

<template>
	<section v-for="(r, i) in rows" :key="i" class="card">
		<div class="field">
			<div class="row-between">
				<label class="label" :for="`oc-desc-${i}`">Description</label>
				<button type="button" class="icon-btn icon-btn-danger" :aria-label="`Remove ${r.description || 'this cost'}`" @click="rows.splice(i, 1)">
					<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
						<path d="M4 7h16M9 7V4.5h6V7M6.5 7l1 13h9l1-13" />
					</svg>
				</button>
			</div>
			<input :id="`oc-desc-${i}`" v-model="r.description" class="input" type="text" />
		</div>
		<div class="field-grid">
			<div class="field">
				<label class="label" :for="`oc-cat-${i}`">Budget category</label>
				<select :id="`oc-cat-${i}`" v-model="r.budget_category" class="input">
					<option value="">Choose…</option>
					<option v-for="c in categories" :key="c.name" :value="c.name">{{ c.name }}</option>
				</select>
			</div>
			<div class="field">
				<label class="label" :for="`oc-cost-${i}`">Cost</label>
				<input :id="`oc-cost-${i}`" v-model.number="r.cost" class="input" type="number" inputmode="decimal" min="0" step="0.01" />
			</div>
		</div>
	</section>
	<p v-if="!rows.length" class="muted">No other costs. Add one below.</p>
	<button type="button" class="btn-dashed" @click="add">Add a cost</button>
	<p v-if="error" class="error">{{ error }}</p>
	<div class="actions">
		<button type="button" class="btn-secondary" @click="emit('cancel')">Cancel</button>
		<button type="button" class="btn-primary" :disabled="saving" @click="save">
			{{ saving ? "Saving…" : "Save other costs" }}
		</button>
	</div>
</template>
