<script setup>
import { computed, ref } from "vue";
import { call } from "../api.js";
import { number } from "../format.js";
import Sheet from "./Sheet.vue";
import Stepper from "./Stepper.vue";

const props = defineProps({
	estimation: { type: String, required: true },
	modified: { type: String, required: true },
	row: { type: Object, required: true },
	trades: { type: Array, default: () => [] },
});
const emit = defineEmits(["close", "saved"]);

const days = ref(props.row.edit.days_per_equipment);
const crew = ref(props.row.edit.roles.map((r) => ({ ...r })));
const adding = ref("");
const saving = ref(false);
const error = ref("");

const teamDays = computed(() => Math.round(props.row.edit.quantity * days.value * 100) / 100);
const dots = computed(() => Object.fromEntries(props.trades.map((t) => [t.name, t.dot])));
const available = computed(() => props.trades.filter((t) => !crew.value.some((c) => c.trade === t.name)));

function addRole() {
	if (adding.value) crew.value.push({ trade: adding.value, count: 1 });
	adding.value = "";
}

async function save() {
	saving.value = true;
	error.value = "";
	try {
		await call(
			"alsa_estimation.editing.save_scope",
			{
				name: props.estimation,
				scope: props.row.key,
				days_per_equipment: days.value,
				roles: crew.value,
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
	<Sheet :title="row.title" :subtitle="`Qty ${number(row.edit.quantity)}`" @close="emit('close')">
		<div class="field">
			<label class="label" for="scope-days">Days per equipment</label>
			<div class="row-between">
				<Stepper id="scope-days" v-model="days" label="days" :step="0.5" />
				<strong>{{ number(teamDays) }} team days</strong>
			</div>
		</div>
		<div class="field">
			<span class="label">Crew</span>
			<div v-for="(c, i) in crew" :key="c.trade" class="crew-row">
				<span class="dot dot-lg" :style="{ background: dots[c.trade] || '#64748B' }"></span>
				<span class="crew-trade">{{ c.trade }}</span>
				<Stepper v-model="c.count" :label="c.trade" :min="1" />
				<button type="button" class="icon-btn" :aria-label="`Remove ${c.trade}`" @click="crew.splice(i, 1)">
					<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
						<path d="M4 7h16M9 7V4.5h6V7M6.5 7l1 13h9l1-13" />
					</svg>
				</button>
			</div>
			<label v-if="available.length" class="sr-only" for="scope-add-role">Add role</label>
			<select v-if="available.length" id="scope-add-role" v-model="adding" class="input" @change="addRole">
				<option value="">Add role…</option>
				<option v-for="t in available" :key="t.name" :value="t.name">{{ t.name }}</option>
			</select>
		</div>
		<p v-if="error" class="error">{{ error }}</p>
		<template #footer>
			<button type="button" class="btn-secondary" @click="emit('close')">Cancel</button>
			<button type="button" class="btn-primary" :disabled="saving" @click="save">
				{{ saving ? "Saving…" : "Save" }}
			</button>
		</template>
	</Sheet>
</template>
