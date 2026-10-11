<script setup>
import { computed, onMounted, ref } from "vue";
import { useRoute } from "vue-router";
import { call } from "../api.js";
import { amount, number } from "../format.js";
import Sheet from "../components/Sheet.vue";
import SkeletonCards from "../components/SkeletonCards.vue";
import StepPager from "../components/StepPager.vue";
import Stepper from "../components/Stepper.vue";
import TopBar from "../components/TopBar.vue";

// Sending and the line actions run in nexlify_budget_control, with the desk's checks.
const SC = "nexlify_budget_control.nexlify_budget_control.supply_chain.";
const TONES = { Priced: "green", Waiting: "amber", "Not Sent": "gray", Manual: "blue", Cancelled: "red" };
const ORDER = ["Priced", "Waiting", "Not Sent", "Manual", "Cancelled"];

const route = useRoute();
const name = route.params.name;
const data = ref(null);
const error = ref("");
const busy = ref(false);
const sheetError = ref("");
const confirmSend = ref(false);
const line = ref(null);
const edit = ref({ qty: 0, rate: 0, description: "" });
const adding = ref(false);
const search = ref("");
const results = ref([]);
const picked = ref(null);
const draft = ref({ qty: 1, price_source: "Supply Chain", rate: 0, description: "" });
let timer;

const counts = computed(() =>
	data.value ? ORDER.filter((k) => data.value.counts[k]).map((k) => ({ label: k, n: data.value.counts[k] })) : [],
);
const waiting = computed(() => (data.value ? data.value.counts.Waiting || 0 : 0));
const qtyClearsPrice = computed(
	() => line.value && line.value.price_source !== "Manual" && line.value.status === "Priced" && edit.value.qty !== line.value.qty,
);

function items(n) {
	return n === 1 ? "1 item" : `${n} items`;
}

async function load() {
	error.value = "";
	try {
		data.value = await call("alsa_estimation.supply.get_supply", { name });
	} catch (e) {
		error.value = e.message;
	}
}

async function run(fn) {
	busy.value = true;
	sheetError.value = "";
	try {
		await fn();
		await load();
		return true;
	} catch (e) {
		sheetError.value = e.message;
		return false;
	} finally {
		busy.value = false;
	}
}

function openSend() {
	sheetError.value = "";
	confirmSend.value = true;
}

async function sendAll() {
	if (await run(() => call(`${SC}send_to_supply_chain`, { estimation: name }, { write: true }))) confirmSend.value = false;
}

function openLine(l) {
	sheetError.value = "";
	edit.value = { qty: l.qty, rate: l.rate, description: l.description || "" };
	line.value = l;
}

async function saveLine() {
	const l = line.value;
	const args = { name, row: l.name, modified: data.value.modified };
	if (l.qty_editable && edit.value.qty !== l.qty) args.qty = edit.value.qty;
	if (l.rate_editable && edit.value.rate !== l.rate) args.rate = edit.value.rate;
	if (l.description_editable && edit.value.description !== (l.description || "")) args.description = edit.value.description;
	if (args.qty === undefined && args.rate === undefined && args.description === undefined) {
		line.value = null;
		return;
	}
	if (await run(() => call("alsa_estimation.supply.update_supply_line", args, { write: true }))) line.value = null;
}

async function lineAction(a) {
	const l = line.value;
	let fn;
	if (a.action === "send_line") fn = () => call(`${SC}send_to_supply_chain`, { estimation: name, rows: [l.name] }, { write: true });
	else if (a.action === "remove")
		fn = () => call("alsa_estimation.supply.remove_supply_line", { name, row: l.name, modified: data.value.modified }, { write: true });
	else fn = () => call(`${SC}supply_line_action`, { estimation: name, row: l.name, action: a.action }, { write: true });
	if (await run(fn)) line.value = null;
}

function openAdd() {
	sheetError.value = "";
	picked.value = null;
	search.value = "";
	draft.value = { qty: 1, price_source: "Supply Chain", rate: 0, description: "" };
	adding.value = true;
	findItems();
}

async function findItems() {
	try {
		results.value = await call("alsa_estimation.supply.search_items", { txt: search.value });
	} catch (e) {
		sheetError.value = e.message;
	}
}

function onSearch() {
	clearTimeout(timer);
	timer = setTimeout(findItems, 250);
}

function pick(it) {
	picked.value = it;
	draft.value.description = it.item_name || it.name;
}

async function addLine() {
	const d = draft.value;
	const args = {
		name,
		item_code: picked.value.name,
		qty: d.qty,
		price_source: d.price_source,
		description: d.description,
		rate: d.price_source === "Manual" ? d.rate : 0,
		modified: data.value.modified,
	};
	if (await run(() => call("alsa_estimation.supply.add_supply_line", args, { write: true }))) adding.value = false;
}

onMounted(load);
</script>

<template>
	<TopBar title="Supply" :subtitle="name" :back="{ name: 'estimation', params: { name } }" />
	<main class="page-body">
		<p v-if="error" class="error">{{ error }}</p>
		<SkeletonCards v-if="!data && !error" :count="3" />
		<template v-if="data">
			<section class="subtotal">
				<div class="row-between">
					<span class="total-label">Total supply</span>
					<strong class="total-value is-cost">{{ amount(data.supply_total) }}</strong>
				</div>
				<div v-if="counts.length" class="trade-chips">
					<span v-for="c in counts" :key="c.label" class="badge" :class="`tone-${TONES[c.label]}`">{{ c.label }} {{ c.n }}</span>
				</div>
			</section>

			<section v-if="waiting" class="banner banner-warn">
				<strong>Waiting for Supply Chain</strong>
				<span>{{ items(waiting) }} being priced in {{ data.pending.join(", ") }}.</span>
			</section>
			<section v-if="data.to_send" class="banner supply-send">
				<span>{{ items(data.to_send) }} not sent to Supply Chain yet.</span>
				<button v-if="data.editable" type="button" class="btn-primary btn-small" @click="openSend">
					Send {{ items(data.to_send) }} to Supply Chain
				</button>
			</section>
			<p v-if="data.locked_reason" class="muted">{{ data.locked_reason }}</p>

			<button
				v-for="l in data.lines"
				:key="l.name"
				type="button"
				class="card supply-line"
				:class="{ 'is-cancelled': l.status === 'Cancelled' }"
				@click="openLine(l)"
			>
				<div class="row-between row-top">
					<div>
						<h2 class="row-title">{{ l.description || l.item_code }}</h2>
						<span class="muted">{{ l.item_code }}, {{ number(l.qty) }} {{ l.uom || "" }}</span>
					</div>
					<span class="badge" :class="`tone-${TONES[l.status] || 'gray'}`">{{ l.status }}</span>
				</div>
				<div class="figures">
					<div class="figure">
						<span>Rate</span>
						<strong>{{ l.rate ? amount(l.rate) : "No price yet" }}</strong>
					</div>
					<div class="figure">
						<span>Cost</span>
						<strong class="is-cost">{{ amount(l.cost) }}</strong>
					</div>
					<div v-if="l.supplier" class="figure">
						<span>Supplier</span>
						<strong>{{ l.supplier }}</strong>
					</div>
				</div>
			</button>
			<p v-if="!data.lines.length" class="muted">No supply items yet.</p>
			<button v-if="data.editable" type="button" class="btn-dashed" @click="openAdd">Add an item</button>
			<StepPager :estimation="name" current="supply" />
		</template>
	</main>

	<Sheet v-if="confirmSend" title="Send to Supply Chain?" :subtitle="name" @close="confirmSend = false">
		<p>
			{{ items(data.to_send) }} go to Supply Chain in a new Supply Request. They show as Waiting until Supply Chain
			sends the prices.
		</p>
		<p v-if="sheetError" class="error">{{ sheetError }}</p>
		<template #footer>
			<button type="button" class="btn-secondary" @click="confirmSend = false">Cancel</button>
			<button type="button" class="btn-primary" :disabled="busy" @click="sendAll">{{ busy ? "Sending…" : "Send" }}</button>
		</template>
	</Sheet>

	<Sheet v-if="line" :title="line.description || line.item_code" :subtitle="`${line.item_code}, ${line.status}`" @close="line = null">
		<div v-if="line.description_editable" class="field">
			<label class="label" for="supply-desc">Description</label>
			<input id="supply-desc" v-model="edit.description" class="input" type="text" maxlength="140" />
		</div>
		<div v-if="line.qty_editable" class="field">
			<span class="label">Quantity{{ line.uom ? ` (${line.uom})` : "" }}</span>
			<Stepper v-model="edit.qty" label="quantity" :min="0" />
		</div>
		<p v-if="qtyClearsPrice" class="banner banner-warn">
			A new quantity clears the Supply Chain price. Send the line again after you save.
		</p>
		<div v-if="line.rate_editable" class="field">
			<label class="label" for="supply-rate">Rate</label>
			<input id="supply-rate" v-model.number="edit.rate" class="input" type="number" inputmode="decimal" min="0" step="0.01" />
		</div>
		<div v-if="line.actions.length" class="field">
			<span class="label">Actions</span>
			<div class="sheet-actions">
				<button
					v-for="a in line.actions"
					:key="a.action"
					type="button"
					class="btn-secondary btn-small"
					:class="{ 'is-danger': a.action === 'cancel' || a.action === 'remove' }"
					:disabled="busy"
					@click="lineAction(a)"
				>
					{{ a.label }}
				</button>
			</div>
		</div>
		<div v-if="line.supplier_quotation || line.supply_request" class="field">
			<span class="label">On the desk</span>
			<a
				v-if="line.supplier_quotation"
				class="link"
				:href="`/app/supplier-quotation/${encodeURIComponent(line.supplier_quotation)}`"
				target="_blank"
				rel="noopener"
			>
				Supplier Quotation {{ line.supplier_quotation }}
			</a>
			<a
				v-if="line.supply_request"
				class="link"
				:href="`/app/supply-request/${encodeURIComponent(line.supply_request)}`"
				target="_blank"
				rel="noopener"
			>
				Supply Request {{ line.supply_request }}
			</a>
		</div>
		<p v-if="sheetError" class="error">{{ sheetError }}</p>
		<template #footer>
			<button type="button" class="btn-secondary" @click="line = null">Close</button>
			<button
				type="button"
				class="btn-primary"
				:disabled="busy || (!line.qty_editable && !line.rate_editable && !line.description_editable)"
				@click="saveLine"
			>
				{{ busy ? "Saving…" : "Save" }}
			</button>
		</template>
	</Sheet>

	<Sheet
		v-if="adding"
		:title="picked ? picked.item_name || picked.name : 'Add an item'"
		:subtitle="picked ? picked.name : 'Search by code or name'"
		@close="adding = false"
	>
		<template v-if="!picked">
			<label class="search">
				<span class="sr-only">Search items</span>
				<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
					<circle cx="11" cy="11" r="7" />
					<path d="M20 20l-3.5-3.5" />
				</svg>
				<input v-model="search" type="search" placeholder="Item code or name" @input="onSearch" />
			</label>
			<div class="list-card">
				<button v-for="it in results" :key="it.name" type="button" class="list-row pick-row" @click="pick(it)">
					<span class="list-main">
						<span class="list-title">{{ it.item_name || it.name }}</span>
						<span class="muted">{{ it.name }}</span>
					</span>
					<span class="muted">{{ it.stock_uom }}</span>
				</button>
				<p v-if="!results.length" class="list-empty muted">No items match.</p>
			</div>
		</template>
		<template v-else>
			<div class="field">
				<label class="label" for="add-desc">Description</label>
				<input id="add-desc" v-model="draft.description" class="input" type="text" maxlength="140" />
			</div>
			<div class="field">
				<span class="label">Quantity{{ picked.stock_uom ? ` (${picked.stock_uom})` : "" }}</span>
				<Stepper v-model="draft.qty" label="quantity" :min="0" />
			</div>
			<div class="field">
				<span class="label">Price from</span>
				<div class="segmented seg-2">
					<button
						v-for="s in data.sources"
						:key="s"
						type="button"
						class="segment"
						:class="{ 'is-on': draft.price_source === s }"
						:aria-pressed="String(draft.price_source === s)"
						@click="draft.price_source = s"
					>
						{{ s }}
					</button>
				</div>
				<p class="muted">
					{{ draft.price_source === "Manual" ? "You type the rate." : "Supply Chain prices it after you send it." }}
				</p>
			</div>
			<div v-if="draft.price_source === 'Manual'" class="field">
				<label class="label" for="add-rate">Rate</label>
				<input id="add-rate" v-model.number="draft.rate" class="input" type="number" inputmode="decimal" min="0" step="0.01" />
			</div>
			<button type="button" class="link-btn" @click="picked = null">Pick another item</button>
		</template>
		<p v-if="sheetError" class="error">{{ sheetError }}</p>
		<template #footer>
			<button type="button" class="btn-secondary" @click="adding = false">Cancel</button>
			<button type="button" class="btn-primary" :disabled="busy || !picked" @click="addLine">
				{{ busy ? "Adding…" : "Add item" }}
			</button>
		</template>
	</Sheet>
</template>
