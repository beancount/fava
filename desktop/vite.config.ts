import { defineConfig } from "vite";

// https://vitejs.dev/config/
export default defineConfig({
  // Vite options for Tauri
  clearScreen: false,
  server: {
    port: 1420,
    strictPort: true,
    watch: {
      ignored: ["**/src-tauri/**"],
    },
  },
});
