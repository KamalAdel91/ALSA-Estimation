<script setup>
const props = defineProps({
	modelValue: { type: Number, default: 0 },
	label: { type: String, required: true },
	step: { type: Number, default: 1 },
	min: { type: Number, default: 0 },
	id: { type: String, default: undefined },
});
const emit = defineEmits(["update:modelValue"]);

function set(value) {
	const n = Math.round((Number(value) || 0) * 100) / 100;
	emit("update:modelValue", Math.max(props.min, n));
}
</script>

<template>
	<div class="stepper">
		<button type="button" class="step-btn" :aria-label="`Fewer ${label}`" @click="set(modelValue - step)">
			<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" aria-hidden="true">
				<path d="M5 12h14" />
			</svg>
		</button>
		<input
			:id="id"
			class="step-input"
			type="text"
			inputmode="decimal"
			:value="modelValue"
			:aria-label="label"
			@change="set($event.target.value)"
		/>
		<button type="button" class="step-btn" :aria-label="`More ${label}`" @click="set(modelValue + step)">
			<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" aria-hidden="true">
				<path d="M12 5v14M5 12h14" />
			</svg>
		</button>
	</div>
</template>
