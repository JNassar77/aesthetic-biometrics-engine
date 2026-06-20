# Frontend MVP — Lovable Build Spec

The thin, guided **capture → heatmap → PDF** web app that sits on top of the engine.
Build it in **Lovable**; it talks ONLY to the Supabase Edge Function `engine-proxy`
(never to the engine directly, never holding the engine key).

- **Setting:** in-practice, tablet-first, responsive (also phone + desktop browser).
- **Posture:** DEV/TEST — consenting subjects only. Real-patient launch is gated on
  Gate 0 (DSGVO Art. 9). The consent screen below is the MVP minimum, not the full DPIA.

---

## 1. Copy-paste prompt for Lovable

> Build a responsive, tablet-first medical web app called **"Aesthetic Scan"** for an
> aesthetic-medicine practice. Calm, clean, clinical design (white/near-white background,
> one teal accent `#0EA5A4`, generous spacing, large touch targets, rounded cards). It is
> a single guided flow with a top progress indicator (Consent → Capture → Review → Results).
>
> **Screen 1 — Consent.** Short heading "Facial aesthetic analysis". One paragraph: the app
> takes four standardized photos of the face and returns a visual analysis and a PDF report;
> photos are processed in the EU. A required checkbox: "I consent to my facial photographs
> being processed for this aesthetic analysis." The "Start" button is disabled until checked.
>
> **Screen 2 — Guided capture (4 shots).** Use the live device camera (`getUserMedia`,
> front camera). Show the live video full-width with a semi-transparent **face-silhouette
> guide overlay** that changes per step, and a step caption:
>   1. "Look straight ahead (0°)" — front-facing silhouette.
>   2. "Turn your head to your LEFT, ~45°" — silhouette angled left.
>   3. "Turn your head to your RIGHT, ~45°" — silhouette angled right.
>   4. "Full profile, turn 90° (left)" — side silhouette. Caption note: "must be a true
>      side view or it will be rejected."
> A large round shutter button captures the current frame. After each capture show a small
> thumbnail with "Retake" / "Next". Keep neutral expression, eyes open, hair off the face.
> When all four are captured, enable "Analyze".
>
> Downscale each captured frame before upload: draw the video frame to a canvas at **max
> 1600px on the longest edge**, export `image/jpeg` quality 0.85. (Do NOT mirror the saved
> image — draw the video un-flipped.)
>
> **Screen 3 — Review.** Show the four thumbnails with their labels; allow retaking any one.
> "Analyze" submits.
>
> **Screen 4 — Results.** While loading show "Analyzing…". On success:
>   - A large card per analyzed view showing the uploaded photo with a **heatmap overlay**:
>     for each overlay zone draw a soft radial blob at its centroid, coloured by `color_code`
>     with opacity = `intensity`, and small dots at each injection point. (Coordinate mapping
>     in the technical appendix.) A legend: green = minimal, amber = moderate, red = marked.
>   - A summary card: `aesthetic_score` (0–100, "100 = no treatment need"), `symmetry_index`,
>     and the top 3 zones by severity (name + severity/10).
>   - A treatment-plan card: list primary concerns and any contraindications (show
>     contraindication messages prominently in amber/red).
>   - A **"Download PDF report"** button (calls the report endpoint, opens/saves the PDF).
>   - A banner if any warning is present (e.g. calibration unreliable, a view was rejected).
>   - A "New scan" button to restart.
>
> Handle errors gracefully: if the analyze call returns 422 (no face) or a view is rejected,
> show which view and offer to retake it. Show a friendly message on network errors.
>
> Read the API base URL and key from app config/secrets: `ENGINE_PROXY_URL` and
> `SUPABASE_ANON_KEY`. Use plain `fetch` with `FormData` for the analyze call (let the
> browser set the multipart boundary).

---

## 2. Technical contract (give this to Lovable too)

### Config
```
ENGINE_PROXY_URL = https://mbwteypkehrmeqzdzdph.supabase.co/functions/v1/engine-proxy
SUPABASE_ANON_KEY = <project anon key>   # public-safe; from Supabase → Project Settings → API
```
Every call sends both headers:
```
Authorization: Bearer <SUPABASE_ANON_KEY>
apikey:        <SUPABASE_ANON_KEY>
```

### Health (optional preflight)
```
GET {ENGINE_PROXY_URL}/health  ->  { "status": "healthy", "model_loaded": true, ... }
```

### Run assessment
```js
const fd = new FormData();
fd.append("frontal",       frontalBlob,  "frontal.jpg");
fd.append("oblique_left",  leftBlob,     "oblique_left.jpg");
fd.append("oblique_right", rightBlob,    "oblique_right.jpg");
fd.append("profile",       profileBlob,  "profile.jpg");   // ≥1 of these four required

const res = await fetch(`${ENGINE_PROXY_URL}/assessment`, {
  method: "POST",
  headers: { Authorization: `Bearer ${ANON}`, apikey: ANON }, // no Content-Type!
  body: fd,
});
const assessment = await res.json();   // AssessmentResponse (keep it for the PDF call)
```
Do NOT send `organization_id` — the proxy injects the tenant server-side.

### Download the PDF
```js
const pdf = await fetch(`${ENGINE_PROXY_URL}/report`, {
  method: "POST",
  headers: { Authorization: `Bearer ${ANON}`, apikey: ANON, "Content-Type": "application/json" },
  body: JSON.stringify(assessment),     // the SAME object returned by /assessment
});
const url = URL.createObjectURL(await pdf.blob());
window.open(url);                        // or trigger a download
```

### Response shape (subset the UI needs)
```ts
interface AssessmentResponse {
  aesthetic_score: number;                       // 0–100
  global_metrics: { symmetry_index: number; /* … */ };
  zones: { zone_id: string; zone_name: string; severity: number /*0–10*/; /* … */ }[];
  treatment_plan: {
    primary_concerns: any[];
    contraindications: { severity: string; code: string; message: string; recommendation: string }[];
    // …
  };
  calibration: { reliable: boolean };            // false -> show "measurements estimated" banner
  warnings: string[];                            // e.g. "CALIBRATION_UNRELIABLE: …"
  views_analyzed: string[];                      // which views made it through the quality gate
  image_quality: Record<string, { accepted: boolean; warnings: { code: string }[] }>;
  overlay: {
    image_dimensions: Record<string, {
      width: number; height: number;             // analyzed-frame size
      source_width?: number; source_height?: number;
      crop_x?: number; crop_y?: number; crop_width?: number; crop_height?: number;
    }>;
    zones: {
      zone_id: string; zone_name: string; view: string;   // which uploaded image this maps to
      severity: number; intensity: number;        // intensity 0–1 -> heatmap opacity
      color_code: string;                         // "#22c55e" | "#f59e0b" | "#dc2626"
      centroid_x: number; centroid_y: number;     // normalized [0,1] in the analyzed frame
      injection_points: { x: number; y: number }[];
    }[];
  } | null;
}
```

### Mapping overlay coords onto the **original** uploaded photo
Overlay coords are normalized to the analyzed (face-cropped) frame. Map to the original
upload with the per-view back-transform, then scale to the rendered `<img>` size:
```js
function toOriginalNorm(p, dim) {
  if (dim.crop_width == null) return p;            // no crop -> identity
  return {
    x: (dim.crop_x + p.x * dim.crop_width)  / dim.source_width,
    y: (dim.crop_y + p.y * dim.crop_height) / dim.source_height,
  };
}
// pixel position on screen = origNorm * renderedImageSize
```

### Errors & quality
| Situation | Signal | UI |
|---|---|---|
| No face anywhere | HTTP 422 | "No face detected — retake in better light." |
| A view rejected (e.g. profile not a true 90°) | view missing from `views_analyzed`; `image_quality[view].warnings` has `HEAD_NOT_PROFILE` / `POSE_REJECTED` | Offer to retake that view. |
| Calibration weak | `calibration.reliable === false` or `CALIBRATION_UNRELIABLE` in `warnings` | Banner: "Measurements are estimates." |
| Oversized image | HTTP 413 | Shouldn't happen with the 1600px cap; otherwise "image too large." |

---

## 3. MVP vs. later
- **MVP (this build):** static silhouette guides + post-capture server validation with retake;
  no accounts/history; consent = required checkbox.
- **Phase 2 (same foundation, no rebuild):** live in-browser pose feedback (MediaPipe FaceMesh
  JS) to auto-validate angle before capture; patient accounts + history/compare UI; patient
  self-upload from home; full Art. 9 consent flow + retention controls (Gate 0).

---

## 4. Before it works end-to-end
1. Engine live at `https://biometrics.novasyn.de` (see `deploy/hetzner/README.md`).
2. Edge Function secrets set: `ENGINE_URL`, `ENGINE_API_KEY`, `ENGINE_ORG_ID`
   (see `supabase/functions/engine-proxy/README.md`).
3. Set `ALLOWED_ORIGIN` on the function to the Lovable app's domain once known
   (CORS hardening; `*` is only for dev).
