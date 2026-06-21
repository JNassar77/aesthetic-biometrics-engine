// Typed subset of the engine's AssessmentResponse — only what the UI needs.
// The response carries many more fields; index signatures keep us tolerant of them.

export type ViewKey = "frontal" | "oblique_left" | "oblique_right" | "profile";

export interface Point {
  x: number; // normalized [0,1]
  y: number; // normalized [0,1]
}

export interface OverlayZone {
  zone_id: string;
  zone_name: string;
  view: string; // which uploaded image this maps to (frontal / oblique_left / ...)
  severity: number; // 0..10
  intensity: number; // 0..1 -> heatmap opacity
  color_code: string; // hex, e.g. "#22c55e" | "#f59e0b" | "#dc2626"
  centroid_x: number; // normalized [0,1] in the analyzed (cropped) frame
  centroid_y: number;
  injection_points: Point[];
}

export interface ImageDimensions {
  width: number;
  height: number;
  source_width?: number;
  source_height?: number;
  crop_x?: number;
  crop_y?: number;
  crop_width?: number;
  crop_height?: number;
}

export interface Overlay {
  image_dimensions: Record<string, ImageDimensions>;
  zones: OverlayZone[];
  // Which PHYSICAL oblique upload the canonical "oblique" overlay was computed on
  // ("oblique_left" | "oblique_right" | "oblique"). Lets the UI place the oblique
  // heatmap on the correct uploaded photo. May be absent on older engines.
  canonical_oblique_view?: string | null;
}

export interface ZoneResult {
  zone_id: string;
  zone_name: string;
  severity: number;
  [k: string]: unknown;
}

export interface Contraindication {
  severity: string;
  code: string;
  message: string;
  recommendation: string;
}

export interface ImageQualityEntry {
  accepted: boolean;
  warnings: { code: string; message?: string }[];
}

export interface AssessmentResponse {
  aesthetic_score: number; // 0..100
  global_metrics: { symmetry_index?: number;[k: string]: unknown };
  zones: ZoneResult[];
  treatment_plan: {
    primary_concerns: unknown[];
    contraindications: Contraindication[];
    [k: string]: unknown;
  };
  calibration: { reliable: boolean;[k: string]: unknown };
  warnings: string[];
  views_analyzed: string[];
  image_quality: Record<string, ImageQualityEntry>;
  overlay: Overlay | null;
  [k: string]: unknown;
}
