import { useEffect, useRef, useState } from "react";
import type { ChangeEvent } from "react";
import type { ViewKey } from "../types";
import type { Shots } from "../App";
import { VIEW_ORDER } from "../App";
import { captureFromVideo, fileToUploadBlob } from "../image";
import SilhouetteGuide from "./SilhouetteGuide";

const CAPTIONS: Record<ViewKey, { title: string; note?: string }> = {
  frontal: { title: "Look straight ahead (0°)", note: "Neutral expression, eyes open, hair off the face." },
  oblique_left: { title: "Turn your head to your LEFT, ~45°" },
  oblique_right: { title: "Turn your head to your RIGHT, ~45°" },
  profile: { title: "Full profile — turn 90° (left)", note: "Must be a true side view or it will be rejected." },
};

export default function CaptureScreen({
  shots,
  onShot,
  onClear,
  onDone,
}: {
  shots: Shots;
  onShot: (k: ViewKey, b: Blob) => void;
  onClear: (k: ViewKey) => void;
  onDone: () => void;
}) {
  const [idx, setIdx] = useState(0);
  const key = VIEW_ORDER[idx];
  const videoRef = useRef<HTMLVideoElement>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const fileRef = useRef<HTMLInputElement>(null);
  const [camError, setCamError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  // Start the camera once; stop all tracks on unmount.
  useEffect(() => {
    let cancelled = false;
    async function start() {
      if (!navigator.mediaDevices?.getUserMedia) {
        setCamError("This browser has no camera API. Use 'Upload instead'.");
        return;
      }
      try {
        const stream = await navigator.mediaDevices.getUserMedia({
          video: { facingMode: "user", width: { ideal: 1920 }, height: { ideal: 1080 } },
          audio: false,
        });
        if (cancelled) {
          stream.getTracks().forEach((t) => t.stop());
          return;
        }
        streamRef.current = stream;
        if (videoRef.current) videoRef.current.srcObject = stream;
      } catch (e) {
        setCamError((e as Error).message || "Camera unavailable — use 'Upload instead'.");
      }
    }
    void start();
    return () => {
      cancelled = true;
      streamRef.current?.getTracks().forEach((t) => t.stop());
      streamRef.current = null;
    };
  }, []);

  const current = shots[key];
  const allDone = VIEW_ORDER.every((k) => shots[k]);

  async function shoot() {
    if (!videoRef.current) return;
    setBusy(true);
    try {
      onShot(key, await captureFromVideo(videoRef.current));
    } catch (e) {
      setCamError((e as Error).message);
    } finally {
      setBusy(false);
    }
  }

  async function onFile(e: ChangeEvent<HTMLInputElement>) {
    const f = e.target.files?.[0];
    e.target.value = "";
    if (!f) return;
    setBusy(true);
    try {
      onShot(key, await fileToUploadBlob(f));
    } finally {
      setBusy(false);
    }
  }

  function next() {
    if (idx < VIEW_ORDER.length - 1) setIdx(idx + 1);
    else if (allDone) onDone();
  }

  return (
    <section className="screen capture">
      <div className="step-caption">
        <span className="step-num">{idx + 1}/4</span>
        <div>
          <h2>{CAPTIONS[key].title}</h2>
          {CAPTIONS[key].note && <p className="note">{CAPTIONS[key].note}</p>}
        </div>
      </div>

      <div className="camera-frame">
        {current ? (
          <img className="captured-preview" src={current.url} alt={key} />
        ) : camError ? (
          <div className="cam-fallback">
            <p>Camera not available.</p>
            <p className="muted">{camError}</p>
            <button className="btn" onClick={() => fileRef.current?.click()}>
              Upload a photo
            </button>
          </div>
        ) : (
          <>
            <video ref={videoRef} autoPlay playsInline muted className="cam-video" />
            <SilhouetteGuide view={key} />
          </>
        )}
      </div>

      <input
        ref={fileRef}
        type="file"
        accept="image/*,.heic,.heif"
        hidden
        onChange={onFile}
      />

      <div className="capture-actions">
        {current ? (
          <>
            <button className="btn ghost" onClick={() => onClear(key)} disabled={busy}>
              Retake
            </button>
            <button className="btn primary" onClick={next} disabled={busy}>
              {idx < VIEW_ORDER.length - 1 ? "Next" : "Continue"}
            </button>
          </>
        ) : (
          <>
            <button className="btn ghost" onClick={() => fileRef.current?.click()} disabled={busy}>
              Upload instead
            </button>
            <button
              className="btn shutter"
              onClick={shoot}
              disabled={busy || !!camError}
              aria-label="Capture photo"
            >
              <span className="shutter-ring" />
            </button>
            <div className="spacer" />
          </>
        )}
      </div>

      <div className="thumb-row">
        {VIEW_ORDER.map((k, i) => (
          <button
            key={k}
            className={`thumb ${i === idx ? "active" : ""} ${shots[k] ? "filled" : ""}`}
            onClick={() => setIdx(i)}
            title={k}
          >
            {shots[k] ? <img src={shots[k]!.url} alt={k} /> : <span>{i + 1}</span>}
          </button>
        ))}
      </div>

      {allDone && (
        <button className="btn primary wide" onClick={onDone}>
          Review &amp; analyze →
        </button>
      )}
    </section>
  );
}
