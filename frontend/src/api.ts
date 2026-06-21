import { ENGINE_PROXY_URL, SUPABASE_ANON_KEY } from "./config";
import type { AssessmentResponse, ViewKey } from "./types";

function authHeaders(): Record<string, string> {
  return {
    Authorization: `Bearer ${SUPABASE_ANON_KEY}`,
    apikey: SUPABASE_ANON_KEY,
  };
}

export class ApiError extends Error {
  status: number;
  body: unknown;
  constructor(status: number, message: string, body?: unknown) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.body = body;
  }
}

export interface ShotInput {
  key: ViewKey;
  blob: Blob;
  filename: string;
}

/** POST the captured views to the proxy. NO Content-Type — the browser sets the multipart boundary. */
export async function runAssessment(shots: ShotInput[]): Promise<AssessmentResponse> {
  const fd = new FormData();
  for (const s of shots) fd.append(s.key, s.blob, s.filename);

  const res = await fetch(`${ENGINE_PROXY_URL}/assessment`, {
    method: "POST",
    headers: authHeaders(),
    body: fd,
  });

  const text = await res.text();
  let data: unknown = null;
  try {
    data = text ? JSON.parse(text) : null;
  } catch {
    data = text;
  }

  if (!res.ok) {
    const d = data as { detail?: unknown; error?: unknown } | null;
    const detail = d?.detail ?? d?.error ?? res.statusText;
    throw new ApiError(res.status, typeof detail === "string" ? detail : `HTTP ${res.status}`, data);
  }
  return data as AssessmentResponse;
}

/** POST the AssessmentResponse back to render the clinical PDF. Returns the PDF blob. */
export async function fetchReport(assessment: AssessmentResponse): Promise<Blob> {
  const res = await fetch(`${ENGINE_PROXY_URL}/report`, {
    method: "POST",
    headers: { ...authHeaders(), "Content-Type": "application/json" },
    body: JSON.stringify(assessment),
  });
  if (!res.ok) {
    const t = await res.text().catch(() => "");
    throw new ApiError(res.status, `Report failed (HTTP ${res.status})`, t);
  }
  return await res.blob();
}

/** Optional preflight: is the engine healthy via the proxy? */
export async function checkHealth(): Promise<boolean> {
  try {
    const res = await fetch(`${ENGINE_PROXY_URL}/health`, { headers: authHeaders() });
    if (!res.ok) return false;
    const j = (await res.json()) as { status?: string };
    return j?.status === "healthy";
  } catch {
    return false;
  }
}
