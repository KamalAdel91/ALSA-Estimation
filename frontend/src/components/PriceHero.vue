<script setup>
import { amount, number } from "../format.js";

defineProps({
	price: { type: Object, required: true },
	currency: { type: String, default: "" },
});
</script>

<template>
	<div class="hero">
		<div class="row-between">
			<span class="hero-label">Total price</span>
			<span class="hero-sub">{{ amount(price.price_per_day) }} per team day</span>
		</div>
		<span class="hero-value">{{ currency }} {{ amount(price.total_price) }}</span>
		<div class="split" aria-hidden="true">
			<span class="split-cost" :style="{ width: `${price.cost_share}%` }"></span>
			<span class="split-margin"></span>
		</div>
		<div class="legend">
			<span><span class="dot dot-cost"></span>Cost {{ number(price.cost_share) }}%</span>
			<span><span class="dot dot-margin"></span>Margin {{ number(100 - price.cost_share) }}%</span>
		</div>
	</div>
</template>
