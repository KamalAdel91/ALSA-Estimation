<script setup>
import { onMounted, ref } from "vue";
import { useRouter } from "vue-router";
import { call } from "../api.js";
import { when } from "../format.js";
import { isIOS, isStandalone } from "../install.js";
import { disablePush, enablePush, pushAvailable, pushOn } from "../push.js";

const router = useRouter();
const rows = ref([]);
const more = ref(false);
const loading = ref(true);
const error = ref("");

// iPhones get web push only inside the installed app.
const needsInstall = isIOS() && !isStandalone();
const showPush = Boolean(window.alsa_boot.push) && (pushAvailable() || needsInstall);
const push = ref(pushOn());
const pushBusy = ref(false);
const pushError = ref("");

async function load(append = false) {
	loading.value = true;
	error.value = "";
	try {
		const data = await call("alsa_estimation.notify.get_alerts", { start: append ? rows.value.length : 0 });
		rows.value = append ? [...rows.value, ...data.rows] : data.rows;
		more.value = data.more;
	} catch (e) {
		error.value = e.message;
	} finally {
		loading.value = false;
	}
}

async function open(alert) {
	if (!alert.read) {
		await call("alsa_estimation.notify.mark_read", { name: alert.name }, { write: true }).catch(() => {});
		alert.read = 1;
	}
	if (alert.estimation) router.push({ name: "estimation", params: { name: alert.estimation } });
}

async function markAll() {
	await call("alsa_estimation.notify.mark_read", {}, { write: true }).catch(() => {});
	rows.value.forEach((r) => (r.read = 1));
	window.dispatchEvent(new Event("alsa-alerts-read"));
}

async function togglePush() {
	pushBusy.value = true;
	pushError.value = "";
	try {
		if (push.value) await disablePush();
		else await enablePush();
		push.value = pushOn();
	} catch (e) {
		pushError.value = e.message;
	} finally {
		pushBusy.value = false;
	}
}

onMounted(() => load());
</script>

<template>
	<header class="page-head list-head">
		<div class="row-between">
			<h1>Alerts</h1>
			<button v-if="rows.some((r) => !r.read)" type="button" class="link-btn" @click="markAll">Mark all as read</button>
		</div>
	</header>
	<main class="page-body">
		<section v-if="showPush" class="card">
			<div class="row-between">
				<div>
					<strong>Alerts on this phone</strong>
					<p class="muted">
						{{
							needsInstall
								? "Install the app first (Share, then Add to Home Screen), then turn them on from inside it."
								: push
									? "On. New alerts come to this phone."
									: "Get a notification on this phone for each new alert."
						}}
					</p>
				</div>
				<button
					v-if="!needsInstall"
					type="button"
					:class="push ? 'btn-secondary btn-small' : 'btn-primary btn-small'"
					:disabled="pushBusy"
					@click="togglePush"
				>
					{{ push ? "Turn off" : "Turn on" }}
				</button>
			</div>
			<p v-if="pushError" class="error">{{ pushError }}</p>
		</section>
		<p v-if="error" class="error">{{ error }}</p>
		<button
			v-for="a in rows"
			:key="a.name"
			type="button"
			class="alert-row"
			:class="{ 'is-unread': !a.read }"
			@click="open(a)"
		>
			<span class="alert-dot" aria-hidden="true"></span>
			<span class="alert-text">
				<span class="row-between">
					<strong class="alert-title">
						<span v-if="!a.read" class="sr-only">Unread: </span>{{ a.title }}
					</strong>
					<span class="muted alert-when">{{ when(a.when) }}</span>
				</span>
				<span v-if="a.body" class="alert-body">{{ a.body }}</span>
			</span>
		</button>
		<p v-if="!loading && !error && !rows.length" class="muted">No alerts yet.</p>
		<button v-if="more" type="button" class="btn-secondary" :disabled="loading" @click="load(true)">Load more</button>
		<p v-if="loading" class="muted">Loading…</p>
	</main>
</template>
