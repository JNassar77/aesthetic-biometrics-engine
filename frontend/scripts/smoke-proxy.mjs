// Live smoke test: drive the engine-proxy exactly as the app does.
// Posts up to 4 images to /assessment, then the response to /report.
//
//   node scripts/smoke-proxy.mjs [imageDir]   (default: ../test_images)
//
// Reads VITE_ENGINE_PROXY_URL + VITE_SUPABASE_ANON_KEY from the environment,
// falling back to frontend/.env. Never commits secrets — .env is gitignored.

import { readFileSync, readdirSync, writeFileSync, existsSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join, resolve } from "node:path";

const here = dirname(fileURLToPath(import.meta.url));
const frontendDir = resolve(here, "..");

function loadEnv() {
  const env = { ...process.env };
  const envFile = join(frontendDir, ".env");
  if (existsSync(envFile)) {
    for (const line of readFileSync(envFile, "utf8").split(/\r?\n/)) {
      const m = line.match(/^\s*([A-Z0-9_]+)\s*=\s*(.*)\s*$/);
      if (m && env[m[1]] === undefined) env[m[1]] = m[2];
    }
  }
  return env;
}

const env = loadEnv();
const PROXY = (env.VITE_ENGINE_PROXY_URL ?? "").replace(/\/+$/, "");
const ANON = env.VITE_SUPABASE_ANON_KEY ?? "";
if (!PROXY || !ANON) {
  console.error("Missing VITE_ENGINE_PROXY_URL / VITE_SUPABASE_ANON_KEY (env or frontend/.env).");
  process.exit(2);
}
const auth = { Authorization: `Bearer ${ANON}`, apikey: ANON };

const imageDir = resolve(process.argv[2] ?? join(frontendDir, "..", "test_images"));
const PATTERNS = [
  ["frontal", /frontal/i],
  ["oblique_left", /oblique[_-]?l|links|_l[_.]/i],
  ["oblique_right", /oblique[_-]?r|rechts|obliqu_rechts|_r[_.]/i],
  ["profile", /profile|profil/i],
];

function pickImages(dir) {
  const files = readdirSync(dir).filter((f) => /\.(jpe?g|png|webp|heic|heif)$/i.test(f));
  const picked = {};
  for (const [field, re] of PATTERNS) {
    const hit = files.find((f) => re.test(f) && !Object.values(picked).includes(f));
    if (hit) picked[field] = hit;
  }
  return picked;
}

const contentType = (f) =>
  /\.png$/i.test(f) ? "image/png" : /\.webp$/i.test(f) ? "image/webp" : /\.heic|\.heif$/i.test(f) ? "image/heic" : "image/jpeg";

async function main() {
  if (!existsSync(imageDir)) {
    console.error(`Image dir not found: ${imageDir}`);
    process.exit(2);
  }
  const picked = pickImages(imageDir);
  const fields = Object.keys(picked);
  if (!fields.length) {
    console.error(`No matching images in ${imageDir}`);
    process.exit(2);
  }
  console.log(`Proxy : ${PROXY}`);
  console.log(`Images: ${fields.map((k) => `${k}=${picked[k]}`).join(", ")}\n`);

  // --- /assessment (multipart, exactly like the app) ---
  const fd = new FormData();
  for (const field of fields) {
    const buf = readFileSync(join(imageDir, picked[field]));
    fd.append(field, new Blob([buf], { type: contentType(picked[field]) }), `${field}.jpg`);
  }
  const t0 = Date.now();
  const res = await fetch(`${PROXY}/assessment`, { method: "POST", headers: auth, body: fd });
  const text = await res.text();
  console.log(`POST /assessment -> ${res.status} (${Date.now() - t0} ms)`);
  if (!res.ok) {
    console.error(text.slice(0, 800));
    process.exit(1);
  }
  const a = JSON.parse(text);
  writeFileSync(join(frontendDir, "last-assessment.json"), JSON.stringify(a, null, 2));
  const overlayZones = a.overlay?.zones?.length ?? 0;
  const overlayViews = a.overlay ? Object.keys(a.overlay.image_dimensions ?? {}) : [];
  console.log("  aesthetic_score :", a.aesthetic_score);
  console.log("  views_analyzed  :", a.views_analyzed);
  console.log("  symmetry_index  :", a.global_metrics?.symmetry_index);
  console.log("  calibration     :", a.calibration?.reliable);
  console.log("  warnings        :", a.warnings);
  console.log("  zones           :", (a.zones ?? []).length);
  console.log("  overlay         :", `${overlayZones} zones across views [${overlayViews.join(", ")}]`);

  // Sanity-check the overlay back-transform fields the UI relies on.
  for (const v of overlayViews) {
    const d = a.overlay.image_dimensions[v];
    console.log(`    dim[${v}] source=${d.source_width}x${d.source_height} crop=${d.crop_x},${d.crop_y} ${d.crop_width}x${d.crop_height}`);
  }

  // --- /report (JSON -> PDF) ---
  const t1 = Date.now();
  const pdfRes = await fetch(`${PROXY}/report`, {
    method: "POST",
    headers: { ...auth, "Content-Type": "application/json" },
    body: JSON.stringify(a),
  });
  console.log(`\nPOST /report -> ${pdfRes.status} (${Date.now() - t1} ms)`);
  if (!pdfRes.ok) {
    console.error((await pdfRes.text()).slice(0, 800));
    process.exit(1);
  }
  const pdf = Buffer.from(await pdfRes.arrayBuffer());
  const magic = pdf.subarray(0, 5).toString("latin1");
  const out = join(frontendDir, "smoke-report.pdf");
  writeFileSync(out, pdf);
  console.log(`  pdf bytes       : ${pdf.length} (magic "${magic}")`);
  console.log(`  saved           : ${out}`);
  console.log(`\n${magic === "%PDF-" && overlayZones > 0 ? "PASS" : "CHECK"} — full chain via the live proxy.`);
}

main().catch((e) => {
  console.error("ERROR:", e);
  process.exit(1);
});
