import react from "@vitejs/plugin-react-swc";
import { defineConfig } from "vitest/config";
import tailwindcss from "@tailwindcss/vite";

// https://vitejs.dev/config/
export default defineConfig({
	base: "./",

	build: {
		outDir: "app", // Change 'my-custom-folder' to your desired name
		emptyOutDir: true, // Optional: Clears the output directory before a build
	},
	plugins: [react(), tailwindcss()],
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
