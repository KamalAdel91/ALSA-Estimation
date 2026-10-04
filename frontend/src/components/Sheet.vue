<script setup>
defineProps({
	title: { type: String, default: "" },
	subtitle: { type: String, default: "" },
});
const emit = defineEmits(["close"]);
</script>

<template>
	<Teleport to="body">
		<div class="sheet-overlay" @click.self="emit('close')">
			<section class="sheet" role="dialog" aria-modal="true" :aria-label="title">
				<span class="sheet-grabber" aria-hidden="true"></span>
				<header class="sheet-head">
					<div class="topbar-title">
						<h2 class="row-title">{{ title }}</h2>
						<span v-if="subtitle" class="muted">{{ subtitle }}</span>
					</div>
					<button type="button" class="icon-btn icon-btn-soft" aria-label="Close" @click="emit('close')">
						<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true">
							<path d="M6 6l12 12M18 6L6 18" />
						</svg>
					</button>
				</header>
				<div class="sheet-body">
					<slot />
				</div>
				<footer class="sheet-foot">
					<slot name="footer" />
				</footer>
			</section>
		</div>
	</Teleport>
</template>
