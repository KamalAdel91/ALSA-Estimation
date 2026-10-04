<script setup>
import { computed, onMounted, ref } from "vue";
import { installEvent, isIOS, isStandalone } from "../install.js";

const KEY = "alsa_estimation_install_later";
const WAIT_DAYS = 7;
const title = window.alsa_boot.title;
// Served by the site (branding.py), not bundled.
const icon = "/alsa-estimation-icon-192.png";
const ios = isIOS();
const snoozed = ref(true);

const show = computed(() => !snoozed.value && !isStandalone() && Boolean(installEvent.value || ios));

function later() {
	snoozed.value = true;
	try {
		localStorage.setItem(KEY, String(Date.now()));
	} catch (e) {
		// private browsing: the prompt comes back next time
	}
}

async function install() {
	const event = installEvent.value;
	if (!event) return;
	event.prompt();
	const choice = await event.userChoice;
	installEvent.value = null;
	if (choice.outcome !== "accepted") later();
}

onMounted(() => {
	try {
		snoozed.value = Date.now() - Number(localStorage.getItem(KEY) || 0) < WAIT_DAYS * 864e5;
	} catch (e) {
		snoozed.value = false;
	}
});
</script>

<template>
	<aside v-if="show" class="install" aria-label="Install the app">
		<img :src="icon" alt="" class="install-icon" />
		<div class="install-text">
			<strong>Install {{ title }}</strong>
			<span v-if="installEvent" class="muted">Add it to your home screen and open it like an app.</span>
			<span v-else class="muted">Tap Share, then Add to Home Screen.</span>
			<div class="install-actions">
				<button v-if="installEvent" type="button" class="btn-primary btn-small" @click="install">Install</button>
				<button type="button" class="btn-secondary btn-small" @click="later">
					{{ installEvent ? "Not now" : "Got it" }}
				</button>
			</div>
		</div>
	</aside>
</template>
