<script setup>
import { ref } from "vue";
import { getTheme, setTheme } from "../theme.js";
import Sheet from "./Sheet.vue";

defineProps({
	name: { type: String, default: "" },
	email: { type: String, default: "" },
});
const emit = defineEmits(["close"]);

const OPTIONS = [
	{ value: "auto", label: "Auto" },
	{ value: "light", label: "Light" },
	{ value: "dark", label: "Dark" },
];
const theme = ref(getTheme());

function pick(value) {
	theme.value = value;
	setTheme(value);
}
</script>

<template>
	<Sheet :title="name" :subtitle="email" @close="emit('close')">
		<div class="field">
			<span class="label">Appearance</span>
			<div class="segmented">
				<button
					v-for="o in OPTIONS"
					:key="o.value"
					type="button"
					class="segment"
					:class="{ 'is-on': theme === o.value }"
					:aria-pressed="String(theme === o.value)"
					@click="pick(o.value)"
				>
					{{ o.label }}
				</button>
			</div>
			<p class="muted">Auto follows your phone's setting.</p>
		</div>
		<template #footer>
			<a class="btn-secondary btn-link" href="/app">Open the desk</a>
			<button type="button" class="btn-primary" @click="emit('close')">Done</button>
		</template>
	</Sheet>
</template>
