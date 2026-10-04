import { copyFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import vue from "@vitejs/plugin-vue";
import { defineConfig } from "vite";

const app = fileURLToPath(new URL("../alsa_estimation/", import.meta.url));
const outDir = `${app}public/frontend`;

// The build output is committed, so Frappe Cloud serves it as is and never runs this build.
export default defineConfig({
	base: "/assets/alsa_estimation/frontend/",
	plugins: [
		vue(),
		{
			name: "copy-index-to-www",
			closeBundle() {
				copyFileSync(`${outDir}/index.html`, `${app}www/alsa_estimation.html`);
			},
		},
	],
	build: { outDir, emptyOutDir: true },
});
