/**
 * vite-plugin-cesium copies into dist/<base>/cesium/ when base is /radar/.
 * Deploy rsyncs dist/* → .../radar/, so we need dist/cesium/ (URL /radar/cesium/).
 */
import fs from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const dist = path.join(__dirname, "..", "dist");
const nested = path.join(dist, "radar", "cesium");
const flat = path.join(dist, "cesium");

async function exists(p) {
  try {
    await fs.access(p);
    return true;
  } catch {
    return false;
  }
}

if (await exists(nested)) {
  await fs.rm(flat, { recursive: true, force: true }).catch(() => {});
  await fs.rename(nested, flat);
  try {
    await fs.rm(path.join(dist, "radar"), { recursive: true, force: true });
  } catch {
    /* ignore */
  }
  console.log("[delphi] moved dist/radar/cesium → dist/cesium for /radar/ deploy");
}
