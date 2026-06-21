import { describe, it, expect } from "vitest";
import { toOriginalNorm, hexToRgba } from "./overlay";

describe("toOriginalNorm", () => {
  it("is identity when there is no crop", () => {
    expect(toOriginalNorm({ x: 0.5, y: 0.5 }, { width: 100, height: 100 })).toEqual({ x: 0.5, y: 0.5 });
  });

  it("maps cropped-frame coords back to the original upload", () => {
    // Real dims observed from the live engine: source 1158x1544, crop (8,499) 1072x1045.
    const dim = {
      width: 1072, height: 1045,
      source_width: 1158, source_height: 1544,
      crop_x: 8, crop_y: 499, crop_width: 1072, crop_height: 1045,
    };
    const p = toOriginalNorm({ x: 0.5, y: 0.5 }, dim);
    expect(p.x).toBeCloseTo((8 + 0.5 * 1072) / 1158, 6);
    expect(p.y).toBeCloseTo((499 + 0.5 * 1045) / 1544, 6);
    // A centre point stays inside the original image.
    expect(p.x).toBeGreaterThan(0);
    expect(p.x).toBeLessThan(1);
    expect(p.y).toBeGreaterThan(0);
    expect(p.y).toBeLessThan(1);
  });

  it("maps the crop origin (0,0) to the crop offset over source", () => {
    const dim = {
      width: 1072, height: 1045,
      source_width: 1158, source_height: 1544,
      crop_x: 8, crop_y: 499, crop_width: 1072, crop_height: 1045,
    };
    expect(toOriginalNorm({ x: 0, y: 0 }, dim)).toEqual({ x: 8 / 1158, y: 499 / 1544 });
  });

  it("returns identity when crop fields are incomplete", () => {
    const partial = { width: 10, height: 10, source_width: 100 } as never;
    expect(toOriginalNorm({ x: 0.3, y: 0.4 }, partial)).toEqual({ x: 0.3, y: 0.4 });
  });
});

describe("hexToRgba", () => {
  it("parses 6-digit hex with leading #", () => {
    expect(hexToRgba("#22c55e", 0.5)).toBe("rgba(34, 197, 94, 0.5)");
  });
  it("parses 6-digit hex without #", () => {
    expect(hexToRgba("dc2626", 1)).toBe("rgba(220, 38, 38, 1)");
  });
  it("expands 3-digit hex", () => {
    expect(hexToRgba("#abc", 1)).toBe("rgba(170, 187, 204, 1)");
  });
  it("falls back to amber on invalid input", () => {
    expect(hexToRgba("not-a-color", 0.2)).toBe("rgba(245, 158, 11, 0.2)");
  });
});
