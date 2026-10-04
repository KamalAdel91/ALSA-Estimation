<script setup>
import { ref } from "vue";
import { call } from "../api.js";
import Sheet from "./Sheet.vue";

const props = defineProps({
	estimation: { type: String, required: true },
	modified: { type: String, required: true },
	action: { type: Object, required: true },
	state: { type: String, default: "" },
});
const emit = defineEmits(["close", "done"]);

const running = ref(false);
const error = ref("");

async function run() {
	running.value = true;
	error.value = "";
	try {
		await call(
			"alsa_estimation.actions.apply_action",
			{ name: props.estimation, action: props.action.action, modified: props.modified },
			{ write: true },
		);
		emit("done");
	} catch (e) {
		error.value = e.message;
	} finally {
		running.value = false;
	}
}
</script>

<template>
	<Sheet :title="`${action.action}?`" :subtitle="estimation" @close="emit('close')">
		<p>
			{{ estimation }} moves from <strong>{{ state }}</strong> to <strong>{{ action.next_state }}</strong>.
		</p>
		<p v-if="action.note" class="banner">{{ action.note }}</p>
		<p v-if="error" class="error">{{ error }}</p>
		<template #footer>
			<button type="button" class="btn-secondary" @click="emit('close')">Cancel</button>
			<button
				type="button"
				:class="action.tone === 'red' ? 'btn-danger' : 'btn-primary'"
				:disabled="running"
				@click="run"
			>
				{{ running ? "Working…" : action.action }}
			</button>
		</template>
	</Sheet>
</template>
