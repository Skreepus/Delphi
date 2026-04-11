import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import cesium from "vite-plugin-cesium";

export default defineConfig({
  plugins: [react(), cesium()],
  server: {
    port: 5173,
    headers: {
      // Streamlit embeds this app from another origin/port; allow iframe embedding.
      "Content-Security-Policy": "frame-ancestors *",
    },
  },
  preview: {
    port: 5173,
    headers: {
      "Content-Security-Policy": "frame-ancestors *",
    },
  },
});
