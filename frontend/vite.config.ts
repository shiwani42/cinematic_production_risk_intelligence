import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import tailwindcss from "@tailwindcss/vite";

export default defineConfig({
  base: "/dashboard/",
  plugins: [react(), tailwindcss()],
  server: {
    port: 5173,
    proxy: {
      "/api": "http://127.0.0.1:8080",
      "/list-apps": "http://127.0.0.1:8080",
      "/apps": "http://127.0.0.1:8080",
      "/run": "http://127.0.0.1:8080",
    },
  },
});
