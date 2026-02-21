import { tanstackRouter } from "@tanstack/router-plugin/vite";
import react from "@vitejs/plugin-react-swc";
import path from "node:path";
import { normalizePath } from "vite";
import { viteStaticCopy } from "vite-plugin-static-copy";
import { defineConfig } from "vitest/config";
import tailwindcss from "@tailwindcss/vite";
import { onSuccess } from "vite-plugin-on-success";

// https://vitejs.dev/config/
export default defineConfig({
	base: "./",

	build: {
		outDir: "app", // Change 'my-custom-folder' to your desired name
		emptyOutDir: true, // Optional: Clears the output directory before a build
	},
	plugins: [
		react(),
		tailwindcss(),
		viteStaticCopy({
			targets: [
				{
					src: normalizePath(path.resolve("./src/assets/locales")),
					dest: normalizePath(path.resolve("./app")),
				},
			],
		}),
	],
	server: {
		host: true,
		strictPort: true,
		hmr: {
			host: "localhost", // Or the specific IP address of the development machine
			port: 5173, // The port your Vite server is running on (default 5173)
		},
	},
	test: {
		environment: "jsdom",
		setupFiles: ["./vitest.setup.ts"],
		css: true,
	},
});
