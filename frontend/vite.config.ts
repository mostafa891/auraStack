import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";
import tailwindcss from "@tailwindcss/vite";
import { resolve } from "path";

export default defineConfig({
  plugins: [vue(), tailwindcss()],

  root: resolve(__dirname),

  base: "/static/dist/",

  resolve: {
    alias: {
      "@": resolve(__dirname, "src"),
    },
  },

  build: {
    outDir: resolve(__dirname, "../static/dist"),
    manifest: true,
    emptyOutDir: true,
    rollupOptions: {
      input: resolve(__dirname, "src/main.ts"),
    },
  },

  server: {
    host: "localhost",
    port: 5173,
    strictPort: true,
    origin: "http://localhost:5173",
  },
});
