"""Clinical PDF report generation for a V2 assessment.

Renders an `AssessmentResponse` into a clinician-facing PDF: summary, global
metrics, ranked treatment zones with per-zone measurements (estimated values
clearly flagged), the treatment plan, contraindications, and an honesty/limitation
footer. Pure function — takes the response model, returns PDF bytes; no I/O.

reportlab is a pure-Python dependency (no system libraries), so this runs anywhere
the API runs, including the slim Railway/Docker image.
"""

from __future__ import annotations

import io

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    HRFlowable,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from app.models.schemas_v2 import AssessmentResponse

# ──────────────────────── Palette ────────────────────────

_NAVY = colors.HexColor("#1f2d4d")
_SLATE = colors.HexColor("#43506b")
_LIGHT = colors.HexColor("#eef1f7")
_LINE = colors.HexColor("#c7cfde")
_MUTED = colors.HexColor("#6b7280")
_ESTIMATED = colors.HexColor("#b45309")  # amber — "not a validated value"
_GOOD = colors.HexColor("#15803d")
_WARN = colors.HexColor("#b91c1c")

# Marker appended to any measurement value that is not a validated metric value.
_EST_MARK = "†"


def _severity_color(sev: float) -> colors.Color:
    if sev >= 6.0:
        return _WARN
    if sev >= 3.0:
        return _ESTIMATED
    return _GOOD


def _styles() -> dict:
    ss = getSampleStyleSheet()
    return {
        "title": ParagraphStyle(
            "title", parent=ss["Title"], textColor=_NAVY, fontSize=20,
            spaceAfter=2, alignment=TA_LEFT,
        ),
        "subtitle": ParagraphStyle(
            "subtitle", parent=ss["Normal"], textColor=_MUTED, fontSize=9, spaceAfter=8,
        ),
        "h2": ParagraphStyle(
            "h2", parent=ss["Heading2"], textColor=_NAVY, fontSize=13,
            spaceBefore=12, spaceAfter=4,
        ),
        "body": ParagraphStyle("body", parent=ss["Normal"], fontSize=9, leading=12),
        "small": ParagraphStyle("small", parent=ss["Normal"], fontSize=8, textColor=_MUTED, leading=10),
        "cell": ParagraphStyle("cell", parent=ss["Normal"], fontSize=8, leading=10),
        "cell_hdr": ParagraphStyle(
            "cell_hdr", parent=ss["Normal"], fontSize=8, leading=10,
            textColor=colors.white, fontName="Helvetica-Bold",
        ),
        "score": ParagraphStyle(
            "score", parent=ss["Normal"], fontSize=26, textColor=_NAVY,
            fontName="Helvetica-Bold", alignment=TA_CENTER,
        ),
        "score_lbl": ParagraphStyle(
            "score_lbl", parent=ss["Normal"], fontSize=8, textColor=_MUTED, alignment=TA_CENTER,
        ),
        "warn": ParagraphStyle("warn", parent=ss["Normal"], fontSize=9, textColor=_WARN, leading=12),
    }


def _table_style(header_bg=_NAVY) -> TableStyle:
    return TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), header_bg),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, _LIGHT]),
        ("LINEBELOW", (0, 0), (-1, -1), 0.4, _LINE),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
    ])


def _fmt_range(lo, hi, unit: str) -> str:
    if lo is None or hi is None:
        return "—"
    return f"{lo:g}–{hi:g}{unit}"


def render_assessment_report(
    response: AssessmentResponse,
    *,
    clinic_name: str = "Praxis Nassar",
    patient_label: str | None = None,
) -> bytes:
    """Render an AssessmentResponse into a clinical PDF, returning the bytes."""
    st = _styles()
    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf, pagesize=A4,
        topMargin=16 * mm, bottomMargin=16 * mm,
        leftMargin=16 * mm, rightMargin=16 * mm,
        title="Aesthetic Biometric Assessment",
        author=clinic_name,
    )
    flow: list = []
    has_estimated = False

    # ── Header ──
    flow.append(Paragraph("Aesthetic Biometric Assessment", st["title"]))
    pid = patient_label or (str(response.patient_id) if response.patient_id else "—")
    ts = response.timestamp.strftime("%Y-%m-%d %H:%M UTC")
    flow.append(Paragraph(
        f"{clinic_name} &nbsp;·&nbsp; Patient: {pid} &nbsp;·&nbsp; "
        f"Assessment {str(response.assessment_id)[:8]} &nbsp;·&nbsp; {ts} &nbsp;·&nbsp; "
        f"Engine v{response.engine_version}",
        st["subtitle"],
    ))
    flow.append(HRFlowable(width="100%", thickness=1, color=_NAVY, spaceAfter=8))

    # ── Summary band: score + key facts ──
    rec = response.reconstruction
    depth_line = "relative-z (estimated)"
    if rec and rec.available:
        depth_line = (
            f"3D multi-view · {rec.n_views} views ({', '.join(rec.views_used)}) · "
            f"spread {rec.angular_spread_deg:g}° · reproj RMS {rec.reprojection_rms_mm:g} mm"
        )
    cal = response.calibration
    cal_line = (
        f"{cal.method} · conf {cal.confidence:.2f} · "
        f"{'reliable' if cal.reliable else 'UNRELIABLE — mm are estimates'}"
    )
    facts = [
        ("Calibration", cal_line),
        ("Depth source", depth_line),
        ("Views analyzed", ", ".join(response.views_analyzed) or "—"),
        ("Zones assessed", str(len(response.zones))),
        ("Processing", f"{response.processing_time_ms or 0} ms"),
    ]
    facts_tbl = Table(
        [[Paragraph(f"<b>{k}</b>", st["cell"]), Paragraph(v, st["cell"])] for k, v in facts],
        colWidths=[32 * mm, 96 * mm],
    )
    facts_tbl.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 2),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
    ]))
    score_tbl = Table(
        [[Paragraph(f"{response.aesthetic_score:g}", st["score"])],
         [Paragraph("Aesthetic Score / 100", st["score_lbl"])]],
        colWidths=[40 * mm],
    )
    score_tbl.setStyle(TableStyle([
        ("BOX", (0, 0), (-1, -1), 0.6, _LINE),
        ("BACKGROUND", (0, 0), (-1, -1), _LIGHT),
        ("TOPPADDING", (0, 0), (-1, 0), 8),
    ]))
    band = Table([[score_tbl, facts_tbl]], colWidths=[44 * mm, 130 * mm])
    band.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "MIDDLE")]))
    flow.append(band)

    # ── Assessment-level warnings ──
    if response.warnings:
        flow.append(Spacer(1, 6))
        for w in response.warnings:
            flow.append(Paragraph(f"⚠ {w}", st["warn"]))

    # ── Global metrics ──
    gm = response.global_metrics
    flow.append(Paragraph("Global Metrics", st["h2"]))
    thirds = gm.facial_thirds
    hp = gm.head_pose
    gm_rows = [
        [Paragraph("Metric", st["cell_hdr"]), Paragraph("Value", st["cell_hdr"])],
        ["Symmetry index", f"{gm.symmetry_index:.1f} / 100"],
        ["Facial thirds (upper / middle / lower)",
         f"{thirds.upper:.2f} / {thirds.middle:.2f} / {thirds.lower:.2f}"],
        ["Golden-ratio deviation", f"{gm.golden_ratio_deviation:.1f}%"],
        ["Lip ratio (upper:lower)", f"{gm.lip_ratio:.2f}" if gm.lip_ratio is not None else "—"],
        ["Head pose (yaw / pitch / roll)",
         f"{hp.yaw:.1f}° / {hp.pitch:.1f}° / {hp.roll:.1f}°" if hp else "—"],
    ]
    gm_tbl = Table(gm_rows, colWidths=[90 * mm, 84 * mm])
    gm_tbl.setStyle(_table_style())
    flow.append(gm_tbl)

    # ── Zones (ranked by severity) ──
    flow.append(Paragraph("Treatment Zones (ranked by severity)", st["h2"]))
    if response.zones:
        zone_rows = [[
            Paragraph("Zone", st["cell_hdr"]), Paragraph("Region", st["cell_hdr"]),
            Paragraph("Sev.", st["cell_hdr"]), Paragraph("View", st["cell_hdr"]),
            Paragraph("Key finding", st["cell_hdr"]),
        ]]
        for z in response.zones:
            finding = z.findings[0].description if z.findings else "—"
            sev_p = Paragraph(
                f'<font color="{_severity_color(z.severity).hexval()}"><b>{z.severity:.1f}</b></font>',
                st["cell"],
            )
            views = "+".join([z.primary_view] + list(z.confirmed_by))
            zone_rows.append([
                Paragraph(f"<b>{z.zone_id}</b> {z.zone_name}", st["cell"]),
                Paragraph(z.region.replace("_", " "), st["cell"]),
                sev_p,
                Paragraph(views, st["cell"]),
                Paragraph(finding, st["cell"]),
            ])
        zt = Table(zone_rows, colWidths=[34 * mm, 22 * mm, 12 * mm, 22 * mm, 84 * mm], repeatRows=1)
        zt.setStyle(_table_style())
        flow.append(zt)

        # ── Per-zone measurements (estimated values flagged) ──
        flow.append(Paragraph("Measurements per Zone", st["h2"]))
        m_rows = [[
            Paragraph("Zone", st["cell_hdr"]), Paragraph("Measurement", st["cell_hdr"]),
            Paragraph("Value", st["cell_hdr"]), Paragraph("Ideal range", st["cell_hdr"]),
            Paragraph("Dev.", st["cell_hdr"]),
        ]]
        for z in response.zones:
            for m in z.measurements:
                val = f"{m.value:g} {m.unit}".strip()
                if m.estimated:
                    has_estimated = True
                    val = (
                        f'<font color="{_ESTIMATED.hexval()}">{val} {_EST_MARK}</font>'
                    )
                dev = f"{m.deviation_pct:+.0f}%" if m.deviation_pct is not None else "—"
                m_rows.append([
                    Paragraph(z.zone_id, st["cell"]),
                    Paragraph(m.name.replace("_", " "), st["cell"]),
                    Paragraph(val, st["cell"]),
                    Paragraph(_fmt_range(m.ideal_min, m.ideal_max, m.unit), st["cell"]),
                    Paragraph(dev, st["cell"]),
                ])
        if len(m_rows) > 1:
            mt = Table(m_rows, colWidths=[18 * mm, 56 * mm, 34 * mm, 38 * mm, 28 * mm], repeatRows=1)
            mt.setStyle(_table_style(header_bg=_SLATE))
            flow.append(mt)
            if has_estimated:
                flow.append(Spacer(1, 3))
                flow.append(Paragraph(
                    f"{_EST_MARK} <b>estimated</b> — not a validated clinical measurement. "
                    "Depth/projection values derived from 3D reconstruction or relative z; "
                    "do not base injection volumes on them (threshold calibration pending).",
                    st["small"],
                ))
    else:
        flow.append(Paragraph("No zones met the analysis criteria.", st["body"]))

    # ── Treatment plan ──
    tp = response.treatment_plan
    flow.append(Paragraph("Treatment Plan", st["h2"]))
    concerns = list(tp.primary_concerns) + list(tp.secondary_concerns)
    if concerns:
        tp_rows = [[
            Paragraph("Pr.", st["cell_hdr"]), Paragraph("Zone", st["cell_hdr"]),
            Paragraph("Concern", st["cell_hdr"]), Paragraph("Recommendation", st["cell_hdr"]),
            Paragraph("Sess.", st["cell_hdr"]),
        ]]
        for c in concerns:
            recs = []
            for r in c.filler_recommendations:
                vol = f"{r.volume_range_ml[0]:g}–{r.volume_range_ml[1]:g} ml" if r.volume_range_ml else ""
                recs.append(f"{r.category}: {', '.join(r.products[:2])} {vol}".strip())
            for n in c.neurotoxin_recommendations:
                u = f"{n.dose_range_units[0]}–{n.dose_range_units[1]} U" if n.dose_range_units else ""
                recs.append(f"Toxin ({n.target_muscle}): {u}".strip())
            risk = " ⚠high-risk" if c.is_high_risk else ""
            tp_rows.append([
                Paragraph(str(c.priority), st["cell"]),
                Paragraph(f"<b>{c.zone_id}</b> {c.zone_name}", st["cell"]),
                Paragraph(f"{c.concern}{risk}", st["cell"]),
                Paragraph("<br/>".join(recs) or "—", st["cell"]),
                Paragraph(str(c.session), st["cell"]),
            ])
        tpt = Table(tp_rows, colWidths=[10 * mm, 32 * mm, 44 * mm, 76 * mm, 12 * mm], repeatRows=1)
        tpt.setStyle(_table_style())
        flow.append(tpt)

        vol = tp.total_volume_estimate_ml
        units = tp.total_neurotoxin_units
        flow.append(Spacer(1, 4))
        flow.append(Paragraph(
            f"<b>Totals:</b> filler {vol[0]:g}–{vol[1]:g} ml · "
            f"neurotoxin {units[0]}–{units[1]} U · {tp.session_count} session(s).",
            st["body"],
        ))
    else:
        flow.append(Paragraph("No treatment concerns prioritized.", st["body"]))

    # ── Contraindications ──
    if tp.contraindications:
        flow.append(Paragraph("Safety / Contraindications", st["h2"]))
        for ci in tp.contraindications:
            flow.append(Paragraph(
                f'<b><font color="{_WARN.hexval()}">{ci.severity}</font></b> '
                f"[{ci.code}] {ci.message} — <i>{ci.recommendation}</i>",
                st["body"],
            ))

    # ── Footer / disclaimer ──
    flow.append(Spacer(1, 12))
    flow.append(HRFlowable(width="100%", thickness=0.6, color=_LINE, spaceAfter=4))
    flow.append(Paragraph(
        "Clinical decision support only — not a diagnosis. All measurements are "
        "estimated from standardized photographs and must be confirmed by clinical "
        "examination before any treatment. Values marked "
        f"{_EST_MARK} are not validated metric measurements. mm scale derives from "
        "iris calibration (11.7 mm reference); 3D depth uses an orthographic "
        "approximation pending clinical validation.",
        st["small"],
    ))

    doc.build(flow)
    return buf.getvalue()
