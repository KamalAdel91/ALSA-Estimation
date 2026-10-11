<script setup>
import { ref } from "vue";

// Company logo and the signed-in employee, from the boot data the page sends.
const boot = window.alsa_boot || {};
const brand = boot.company || boot.title || "";
const name = boot.full_name || (boot.user || "").split("@")[0];
const initials = name
	.split(/[\s._-]+/)
	.filter(Boolean)
	.slice(0, 2)
	.map((w) => w[0].toUpperCase())
	.join("");
const logoOk = ref(Boolean(boot.logo));
const imageOk = ref(Boolean(boot.user_image));
</script>

<template>
	<header class="brandbar">
		<div class="brand">
			<img v-if="logoOk" :src="boot.logo" :alt="brand" class="brand-logo" @error="logoOk = false" />
			<span v-else class="brand-name">{{ brand }}</span>
		</div>
		<div class="me">
			<div class="me-text">
				<span class="me-hello">Welcome</span>
				<strong class="me-name">{{ name }}</strong>
			</div>
			<img v-if="imageOk" :src="boot.user_image" alt="" class="avatar" @error="imageOk = false" />
			<span v-else class="avatar initials">{{ initials }}</span>
		</div>
	</header>
</template>

<style scoped>
.brandbar {
	display: flex;
	align-items: center;
	justify-content: space-between;
	gap: 12px;
	padding: 10px 16px;
	padding-top: max(10px, env(safe-area-inset-top));
}
.brand {
	min-width: 0;
	display: flex;
	align-items: center;
}
.brand-logo {
	height: 36px;
	max-width: 150px;
	object-fit: contain;
}
.brand-name {
	font-weight: 800;
	font-size: 16px;
	white-space: nowrap;
	overflow: hidden;
	text-overflow: ellipsis;
}
.me {
	display: flex;
	align-items: center;
	gap: 10px;
	min-width: 0;
}
.me-text {
	display: flex;
	flex-direction: column;
	align-items: flex-end;
	min-width: 0;
	line-height: 1.2;
}
.me-hello {
	font-size: 11px;
	opacity: 0.6;
}
.me-name {
	font-size: 14px;
	max-width: 160px;
	white-space: nowrap;
	overflow: hidden;
	text-overflow: ellipsis;
}
.avatar {
	width: 38px;
	height: 38px;
	border-radius: 50%;
	object-fit: cover;
	flex-shrink: 0;
}
.initials {
	display: grid;
	place-items: center;
	background: #172033;
	color: #fff;
	font-weight: 700;
	font-size: 14px;
}
</style>
