import type { ImageDimensions, Point } from "./types";

/**
 * Map a point normalized to the analyzed (face-cropped) frame back to the
 * ORIGINAL upload's normalized coords. If there was no crop, this is identity.
 * Mirrors the contract in docs/CONTRACTS.md / the Lovable spec.
 */
export function toOriginalNorm(p: Point, dim: ImageDimensions): Point {
  const { crop_x, crop_y, crop_width, crop_height, source_width, source_height } = dim;
  if (
    crop_width == null ||
    crop_height == null ||
    !source_width ||
    !source_height
  ) {
    return p; // no crop -> identity
  }
  return {
    x: ((crop_x ?? 0) + p.x * crop_width) / source_width,
    y: ((crop_y ?? 0) + p.y * crop_height) / source_height,
  };
}

/** "#rrggbb" + alpha -> "rgba(r,g,b,a)". Tolerates a leading '#', falls back to amber. */
export function hexToRgba(hex: string, alpha: number): string {
  let h = (hex || "").replace(/^#/, "");
  if (h.length === 3) h = h.split("").map((c) => c + c).join("");
  if (h.length !== 6 || /[^0-9a-fA-F]/.test(h)) h = "f59e0b";
  const r = parseInt(h.slice(0, 2), 16);
  const g = parseInt(h.slice(2, 4), 16);
  const b = parseInt(h.slice(4, 6), 16);
  return `rgba(${r}, ${g}, ${b}, ${alpha})`;
}
