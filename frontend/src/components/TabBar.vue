<template>
	<nav class="tabbar" aria-label="Main">
		<RouterLink :to="{ name: 'home' }" class="tab" exact-active-class="is-active">
			<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
				<path d="M3 10.5L12 3l9 7.5V20a1 1 0 0 1-1 1h-5v-6H9v6H4a1 1 0 0 1-1-1z" />
			</svg>
			<span>Home</span>
		</RouterLink>
		<RouterLink :to="{ name: 'list' }" class="tab" active-class="is-active">
			<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
				<path d="M9 6h11M9 12h11M9 18h11M4.5 6h.01M4.5 12h.01M4.5 18h.01" />
			</svg>
			<span>Estimations</span>
		</RouterLink>
	</nav>
</template>
