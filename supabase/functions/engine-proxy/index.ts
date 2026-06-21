// Aesthetic Biometrics Engine — secure Edge Function proxy.
//
// The browser (Lovable web app) calls THIS function; it never sees the engine's
// X-API-Key. The function authenticates the caller (verify_jwt) and forwards to the
// engine, injecting the tenant (organization_id) SERVER-SIDE.
//
// Routes:
//   GET  /engine-proxy/health       -> engine /api/v2/health (no engine key needed)
//   POST /engine-proxy/assessment   multipart (frontal/oblique_left/oblique_right/profile)
//                                   -> engine /api/v2/assessment  (AssessmentResponse JSON)
//   POST /engine-proxy/report       JSON (AssessmentResponse) -> engine /api/v2/report (PDF)
//
// Env (Supabase function secrets):
//   ENGINE_API_KEY   REQUIRED — one of the engine's API_KEYS (the ONLY secret to set).
//   ENGINE_URL       optional — defaults to https://biometrics.novasyn.de
//   ENGINE_ORG_ID    optional — defaults to the Praxis Nassar tenant
//   ALLOWED_ORIGIN   optional — CORS origin (default "*" for dev; set to the practice domain in prod)
//
// Design note: the proxy buffers the (size-capped) multipart request only to inject the
// tenant server-side, then streams the engine response straight back. Keep client images
// modest (~1600px) — well within the Edge Function 256MB / 2s-CPU limits.

const ENGINE_URL = (Deno.env.get("ENGINE_URL") ?? "https://biometrics.novasyn.de").replace(/\/+$/, "");
const ENGINE_API_KEY = Deno.env.get("ENGINE_API_KEY") ?? "";
const ENGINE_ORG_ID = Deno.env.get("ENGINE_ORG_ID") ?? "80c55491-46b6-4b82-98dc-2719758b4372";
const ALLOWED_ORIGIN = Deno.env.get("ALLOWED_ORIGIN") ?? "*";

const IMAGE_FIELDS = ["frontal", "oblique_left", "oblique_right", "oblique", "profile"];

function cors(): Record<string, string> {
  return {
    "Access-Control-Allow-Origin": ALLOWED_ORIGIN,
    "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
    "Access-Control-Allow-Headers": "authorization, x-client-info, apikey, content-type",
    "Vary": "Origin",
  };
}

function json(body: unknown, status = 200): Response {
  return new Response(JSON.stringify(body), {
    status,
    headers: { ...cors(), "Content-Type": "application/json" },
  });
}

function routeOf(req: Request): string {
  const path = new URL(req.url).pathname;
  return path.replace(/^.*\/engine-proxy/, "").replace(/^\/+|\/+$/g, "");
}

Deno.serve(async (req: Request) => {
  if (req.method === "OPTIONS") return new Response("ok", { headers: cors() });

  const route = routeOf(req);

  // Health needs no engine key — handy for a frontend preflight.
  if (route === "health" && req.method === "GET") {
    try {
      const r = await fetch(`${ENGINE_URL}/api/v2/health`);
      return new Response(r.body, { status: r.status, headers: { ...cors(), "Content-Type": "application/json" } });
    } catch (e) {
      return json({ error: "engine_unreachable", detail: String((e as Error)?.message ?? e) }, 502);
    }
  }

  if (!ENGINE_API_KEY) {
    return json({ error: "proxy_misconfigured", detail: "ENGINE_API_KEY secret must be set" }, 503);
  }

  if (req.method !== "POST") return json({ error: "method_not_allowed", detail: `${req.method} ${route}` }, 405);

  try {
    if (route === "assessment") return await proxyAssessment(req);
    if (route === "report") return await proxyReport(req);
    return json(
      { error: "not_found", detail: `unknown route '${route}'`, routes: ["POST assessment", "POST report", "GET health"] },
      404,
    );
  } catch (e) {
    return json({ error: "proxy_error", detail: String((e as Error)?.message ?? e) }, 502);
  }
});

async function proxyAssessment(req: Request): Promise<Response> {
  const inForm = await req.formData();
  const out = new FormData();
  let images = 0;
  for (const field of IMAGE_FIELDS) {
    const v = inForm.get(field);
    if (v instanceof File) {
      out.append(field, v, v.name || `${field}.jpg`);
      images++;
    }
  }
  if (images === 0) {
    return json({ error: "no_image", detail: "provide at least one of frontal/oblique_left/oblique_right/profile" }, 400);
  }

  // Tenant is set SERVER-SIDE — the browser does not choose the tenant.
  out.append("organization_id", ENGINE_ORG_ID);
  const patientId = inForm.get("patient_id");
  if (typeof patientId === "string" && patientId.length > 0) out.append("patient_id", patientId);

  const r = await fetch(`${ENGINE_URL}/api/v2/assessment`, {
    method: "POST",
    headers: { "X-API-Key": ENGINE_API_KEY },
    body: out,
  });
  return new Response(r.body, {
    status: r.status,
    headers: { ...cors(), "Content-Type": r.headers.get("Content-Type") ?? "application/json" },
  });
}

async function proxyReport(req: Request): Promise<Response> {
  const payload = await req.text(); // AssessmentResponse JSON, forwarded verbatim
  const r = await fetch(`${ENGINE_URL}/api/v2/report`, {
    method: "POST",
    headers: { "X-API-Key": ENGINE_API_KEY, "Content-Type": "application/json" },
    body: payload,
  });
  return new Response(r.body, {
    status: r.status,
    headers: {
      ...cors(),
      "Content-Type": r.headers.get("Content-Type") ?? "application/pdf",
      "Content-Disposition": r.headers.get("Content-Disposition") ?? 'inline; filename="assessment-report.pdf"',
    },
  });
}
