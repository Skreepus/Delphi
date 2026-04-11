import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import cesium from "vite-plugin-cesium";

/**
 * GCP/nginx: DELPHI_VITE_BASE=/radar/ (npm run build:deploy).
 * Local dev: unset → base "/".
 * Do not set CESIUM_BASE_URL here — vite-plugin-cesium merges it with base; run scripts/fix-cesium-dist.mjs after build.
 */
const rawBase = process.env.DELPHI_VITE_BASE?.trim() || "";
const appBase =
  rawBase === "" || rawBase === "/"
    ? "/"
    : rawBase.endsWith("/")
      ? rawBase
      : `${rawBase}/`;

export default defineConfig({
  base: appBase,
  plugins: [react(), cesium()],
  server: {
    port: 5173,
    headers: {
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
