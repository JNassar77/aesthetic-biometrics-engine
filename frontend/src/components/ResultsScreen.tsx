import { useState } from "react";
import type { AssessmentResponse, ViewKey } from "../types";
import type { Shots } from "../App";
import { VIEW_ORDER, VIEW_LABEL } from "../App";
import { fetchReport } from "../api";
import HeatmapView from "./HeatmapView";

function humanizeWarning(w: string): string {
  if (w.includes("CALIBRATION_UNRELIABLE")) return "Measurements are estimates (calibration weak).";
  if (w.includes("NON_NEUTRAL_EXPRESSION")) return "A non-neutral expression was detected — results may shift; retake relaxed for best accuracy.";
  return w;
}

function rejectReason(result: AssessmentResponse, view: ViewKey): string {
  const codes = result.image_quality?.[view]?.warnings?.map((x) => x.code) ?? [];
  if (codes.includes("HEAD_NOT_PROFILE")) return " — not a true 90° side view";
  if (codes.some((c) => c.includes("POSE"))) return " — head pose out of range";
  if (codes.some((c) => c.includes("BLUR") || c.includes("QUALITY"))) return " — image too blurry / low quality";
  if (codes.length) return ` — ${codes[0]}`;
  return "";
}

export default function ResultsScreen({
  result,
  shots,
  onReset,
}: {
  result: AssessmentResponse;
  shots: Shots;
  onReset: () => void;
}) {
  const [pdfBusy, setPdfBusy] = useState(false);
  const [pdfErr, setPdfErr] = useState<string | null>(null);

  const overlay = result.overlay;
  const analyzed = result.views_analyzed ?? [];
  const topZones = [...(result.zones ?? [])].sort((a, b) => b.severity - a.severity).slice(0, 3);
  const contra = result.treatment_plan?.contraindications ?? [];
  const symmetry = result.global_metrics?.symmetry_index;
  const calibrationWeak =
    result.calibration?.reliable === false ||
    (result.warnings ?? []).some((w) => w.includes("CALIBRATION_UNRELIABLE"));

  // The overlay speaks in CANONICAL view names ("frontal", "oblique", "profile").
  // Map each to the PHYSICAL photo we uploaded so markers land on the right image.
  const canonicalOblique = (overlay?.canonical_oblique_view ?? null) as ViewKey | null;
  function physicalFor(canon: string): ViewKey | undefined {
    if (canon === "frontal") return shots.frontal ? "frontal" : undefined;
    if (canon === "profile") return shots.profile ? "profile" : undefined;
    if (canon === "oblique") {
      // Prefer the engine's explicit answer; else only resolve when unambiguous
      // (exactly one oblique analyzed). With both obliques and no hint, skip the
      // heatmap rather than risk drawing on the wrong cheek.
      if (canonicalOblique && shots[canonicalOblique]) return canonicalOblique;
      const obl = (["oblique_left", "oblique_right"] as ViewKey[]).filter(
        (k) => shots[k] && analyzed.includes(k),
      );
      return obl.length === 1 ? obl[0] : undefined;
    }
    return shots[canon as ViewKey] ? (canon as ViewKey) : undefined;
  }

  const heatmaps = overlay
    ? Object.keys(overlay.image_dimensions)
        .map((canon) => ({ canon, phys: physicalFor(canon) }))
        .filter((x): x is { canon: string; phys: ViewKey } => Boolean(x.phys))
    : [];
  const rejected = VIEW_ORDER.filter((k) => shots[k] && !analyzed.includes(k));

  async function downloadPdf() {
    setPdfBusy(true);
    setPdfErr(null);
    try {
      const blob = await fetchReport(result);
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = "aesthetic-report.pdf";
      document.body.appendChild(a);
      a.click();
      a.remove();
      setTimeout(() => URL.revokeObjectURL(url), 15000);
    } catch (e) {
      setPdfErr((e as Error).message);
    } finally {
      setPdfBusy(false);
    }
  }

  return (
    <section className="screen results">
      <div className="score-card">
        <div className="score-num">{Math.round(result.aesthetic_score)}</div>
        <div className="score-meta">
          <strong>Aesthetic score</strong>
          <span className="muted">100 = no treatment need</span>
          {typeof symmetry === "number" && <span>Symmetry index: {symmetry.toFixed(1)}</span>}
          <span className="muted">{analyzed.length} view{analyzed.length === 1 ? "" : "s"} analyzed</span>
        </div>
      </div>

      {(result.warnings?.length ?? 0) > 0 && (
        <div className="banner warn">
          {result.warnings.map((w, i) => (
            <div key={i}>{humanizeWarning(w)}</div>
          ))}
        </div>
      )}
      {calibrationWeak && !(result.warnings ?? []).some((w) => w.includes("CALIBRATION_UNRELIABLE")) && (
        <div className="banner warn">Measurements are estimates (calibration weak).</div>
      )}

      {heatmaps.length > 0 && (
        <>
          <div className="heatmaps">
            {heatmaps.map(({ canon, phys }) => (
              <HeatmapView
                key={canon}
                canonicalView={canon}
                label={VIEW_LABEL[phys]}
                src={shots[phys]!.url}
                overlay={overlay}
              />
            ))}
          </div>
          <div className="legend">
            <span><i className="swatch" style={{ background: "#22c55e" }} /> minimal</span>
            <span><i className="swatch" style={{ background: "#f59e0b" }} /> moderate</span>
            <span><i className="swatch" style={{ background: "#dc2626" }} /> marked</span>
            <span className="muted">· dots = injection points</span>
          </div>
        </>
      )}

      {rejected.map((k) => (
        <div key={k} className="banner warn">
          The <strong>{VIEW_LABEL[k]}</strong> view was not usable{rejectReason(result, k)}. Start a new
          scan to retake it.
        </div>
      ))}

      <div className="card">
        <h3>Top concerns</h3>
        {topZones.length ? (
          <ul className="zone-list">
            {topZones.map((z) => (
              <li key={z.zone_id}>
                <span>{z.zone_name}</span>
                <span className="sev">{z.severity.toFixed(1)}/10</span>
              </li>
            ))}
          </ul>
        ) : (
          <p className="muted">No prioritized zones.</p>
        )}
      </div>

      {contra.length > 0 && (
        <div className="card contra">
          <h3>Contraindications</h3>
          {contra.map((c, i) => (
            <div key={i} className={`contra-item sev-${c.severity}`}>
              <strong>{c.code}</strong>
              <p>{c.message}</p>
              {c.recommendation && <p className="muted">{c.recommendation}</p>}
            </div>
          ))}
        </div>
      )}

      {pdfErr && <div className="banner error">PDF: {pdfErr}</div>}

      <div className="results-actions">
        <button className="btn primary" onClick={downloadPdf} disabled={pdfBusy}>
          {pdfBusy ? "Preparing PDF…" : "Download PDF report"}
        </button>
        <button className="btn ghost" onClick={onReset}>
          New scan
        </button>
      </div>
    </section>
  );
}
