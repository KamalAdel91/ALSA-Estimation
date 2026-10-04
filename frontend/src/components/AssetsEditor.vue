<script setup>
import { onMounted, ref } from "vue";
import { call } from "../api.js";

const props = defineProps({
	estimation: { type: String, required: true },
	modified: { type: String, required: true },
	section: { type: String, required: true },
	edit: { type: Object, required: true },
});
const emit = defineEmits(["cancel", "saved"]);

const cars = props.section === "transportation";
const items = ref([...props.edit.rows]);
const fuel = ref(props.edit.fuel_maintenance_total || 0);
const options = ref([]);
const adding = ref("");
const saving = ref(false);
const error = ref("");

function add() {
	if (adding.value) items.value.push(adding.value);
	adding.value = "";
}

async function save() {
	saving.value = true;
	error.value = "";
	try {
		await call(
			"alsa_estimation.editing.save_assets",
			{
				name: props.estimation,
				table: props.section,
				rows: items.value,
				fuel_maintenance_total: cars ? fuel.value : undefined,
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

onMounted(async () => {
	try {
		options.value = await call("alsa_estimation.editing.get_options", { kind: props.section });
	} catch (e) {
		error.value = e.message;
	}
});
</script>

<template>
	<section class="card">
		<h2 class="section-title">{{ cars ? "Cars" : "Test equipment" }}</h2>
		<div v-for="(item, i) in items" :key="`${item}-${i}`" class="edit-row">
			<span class="edit-row-title">{{ item }}</span>
			<button type="button" class="icon-btn" :aria-label="`Remove ${item}`" @click="items.splice(i, 1)">
				<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
					<path d="M4 7h16M9 7V4.5h6V7M6.5 7l1 13h9l1-13" />
				</svg>
			</button>
		</div>
		<p v-if="!items.length" class="muted">Nothing added yet.</p>
		<label class="sr-only" :for="`add-${section}`">{{ cars ? "Add a car" : "Add test equipment" }}</label>
		<select :id="`add-${section}`" v-model="adding" class="input" @change="add">
			<option value="">{{ cars ? "Add a car…" : "Add test equipment…" }}</option>
			<option v-for="o in options" :key="o.name" :value="o.name">
				{{ o.ownership ? `${o.name} (${o.ownership})` : o.name }}
			</option>
		</select>
	</section>
	<section v-if="cars" class="card">
		<div class="row-between">
			<div>
				<label class="total-label" for="fuel-total">Fuel &amp; maintenance</label>
				<p class="muted">One amount for the whole project</p>
			</div>
			<input id="fuel-total" v-model.number="fuel" class="input input-mid" type="number" inputmode="decimal" min="0" step="0.01" />
		</div>
	</section>
	<p v-if="error" class="error">{{ error }}</p>
	<div class="actions">
		<button type="button" class="btn-secondary" @click="emit('cancel')">Cancel</button>
		<button type="button" class="btn-primary" :disabled="saving" @click="save">
			{{ saving ? "Saving…" : "Save" }}
		</button>
	</div>
</template>
