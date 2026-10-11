import { computed, onBeforeUnmount, onMounted, ref } from "vue";

// Pull down at the top of a screen to reload it; an installed app has no browser refresh.
const LIMIT = 72;

export function usePullRefresh(reload) {
	const pull = ref(0);
	const busy = ref(false);
	let startY = null;

	function start(e) {
		if (window.scrollY > 0 || busy.value) return;
		startY = e.touches[0].clientY;
	}
	function move(e) {
		if (startY === null) return;
		const dy = e.touches[0].clientY - startY;
		pull.value = dy > 0 ? Math.min(dy * 0.5, LIMIT + 16) : 0;
	}
	async function end() {
		if (startY === null) return;
		startY = null;
		if (pull.value < LIMIT) {
			pull.value = 0;
			return;
		}
		busy.value = true;
		pull.value = LIMIT * 0.6;
		try {
			await reload();
		} finally {
			busy.value = false;
			pull.value = 0;
		}
	}

	onMounted(() => {
		window.addEventListener("touchstart", start, { passive: true });
		window.addEventListener("touchmove", move, { passive: true });
		window.addEventListener("touchend", end);
	});
	onBeforeUnmount(() => {
		window.removeEventListener("touchstart", start);
		window.removeEventListener("touchmove", move);
		window.removeEventListener("touchend", end);
	});

	return { pull, busy, ready: computed(() => pull.value >= LIMIT) };
}
