// Capture / downscale helpers. Keep uploads modest (<= 1600px longest edge,
// JPEG q0.85) — well within the Edge Function 256MB / 2s-CPU limits, and the
// engine downscales further internally.

const MAX_EDGE = 1600;
const JPEG_QUALITY = 0.85;

function fit(w: number, h: number): { w: number; h: number } {
  const longest = Math.max(w, h);
  if (longest <= MAX_EDGE) return { w, h };
  const scale = MAX_EDGE / longest;
  return { w: Math.round(w * scale), h: Math.round(h * scale) };
}

function toJpeg(canvas: HTMLCanvasElement): Promise<Blob> {
  return new Promise((resolve, reject) => {
    canvas.toBlob(
      (b) => (b ? resolve(b) : reject(new Error("canvas.toBlob returned null"))),
      "image/jpeg",
      JPEG_QUALITY,
    );
  });
}

/** Draw the current live video frame to a downscaled, UN-mirrored JPEG blob. */
export async function captureFromVideo(video: HTMLVideoElement): Promise<Blob> {
  const vw = video.videoWidth;
  const vh = video.videoHeight;
  if (!vw || !vh) throw new Error("camera not ready");
  const { w, h } = fit(vw, vh);
  const canvas = document.createElement("canvas");
  canvas.width = w;
  canvas.height = h;
  const ctx = canvas.getContext("2d");
  if (!ctx) throw new Error("2d context unavailable");
  ctx.drawImage(video, 0, 0, w, h); // un-flipped: saved image is not mirrored
  return toJpeg(canvas);
}

/**
 * Downscale an uploaded image to a JPEG blob, applying EXIF orientation so the
 * pixels are upright (the engine then sees the same upright bytes we render).
 * Falls back to the original file if the browser can't decode it (e.g. HEIC) —
 * the engine handles HEIC + EXIF itself.
 */
export async function fileToUploadBlob(file: File): Promise<Blob> {
  try {
    const bitmap = await createImageBitmap(file, { imageOrientation: "from-image" });
    const { w, h } = fit(bitmap.width, bitmap.height);
    const canvas = document.createElement("canvas");
    canvas.width = w;
    canvas.height = h;
    const ctx = canvas.getContext("2d");
    if (!ctx) throw new Error("2d context unavailable");
    ctx.drawImage(bitmap, 0, 0, w, h);
    bitmap.close();
    return await toJpeg(canvas);
  } catch {
    return file; // e.g. HEIC — forward original bytes; engine decodes it
  }
}
