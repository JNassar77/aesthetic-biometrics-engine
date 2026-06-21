import { useCallback, useEffect, useRef } from "react";
import type { Overlay } from "../types";
import { toOriginalNorm, hexToRgba } from "../overlay";

export default function HeatmapView({
  canonicalView,
  label,
  src,
  overlay,
}: {
  canonicalView: string; // engine's canonical view name: "frontal" | "oblique" | "profile"
  label: string;
  src: string;
  overlay: Overlay | null;
}) {
  const imgRef = useRef<HTMLImageElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);

  const dim = overlay?.image_dimensions?.[canonicalView];
  const zones = (overlay?.zones ?? []).filter((z) => z.view === canonicalView);

  const draw = useCallback(() => {
    const img = imgRef.current;
    const canvas = canvasRef.current;
    if (!img || !canvas) return;
    const w = img.clientWidth;
    const h = img.clientHeight;
    if (!w || !h) return;
    const dpr = window.devicePixelRatio || 1;
    canvas.width = Math.round(w * dpr);
    canvas.height = Math.round(h * dpr);
    canvas.style.width = `${w}px`;
    canvas.style.height = `${h}px`;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    ctx.clearRect(0, 0, w, h);
    if (!dim) return;

    for (const z of zones) {
      const c = toOriginalNorm({ x: z.centroid_x, y: z.centroid_y }, dim);
      const cx = c.x * w;
      const cy = c.y * h;
      const radius = Math.max(w, h) * 0.13;
      const col = z.color_code || "#f59e0b";
      const alpha = Math.min(0.85, Math.max(0.18, z.intensity));
      const grd = ctx.createRadialGradient(cx, cy, 0, cx, cy, radius);
      grd.addColorStop(0, hexToRgba(col, alpha));
      grd.addColorStop(1, hexToRgba(col, 0));
      ctx.fillStyle = grd;
      ctx.beginPath();
      ctx.arc(cx, cy, radius, 0, Math.PI * 2);
      ctx.fill();

      for (const p of z.injection_points ?? []) {
        const op = toOriginalNorm(p, dim);
        ctx.beginPath();
        ctx.arc(op.x * w, op.y * h, 3.5, 0, Math.PI * 2);
        ctx.fillStyle = col;
        ctx.fill();
        ctx.lineWidth = 1.5;
        ctx.strokeStyle = "rgba(255,255,255,0.92)";
        ctx.stroke();
      }
    }
  }, [dim, zones]);

  useEffect(() => {
    draw();
    window.addEventListener("resize", draw);
    return () => window.removeEventListener("resize", draw);
  }, [draw]);

  return (
    <figure className="heatmap-card">
      <div className="heatmap-wrap">
        <img ref={imgRef} src={src} alt={label} onLoad={draw} />
        <canvas ref={canvasRef} className="heatmap-canvas" />
      </div>
      <figcaption className="heatmap-label">
        {label} · {zones.length} zone{zones.length === 1 ? "" : "s"}
      </figcaption>
    </figure>
  );
}
