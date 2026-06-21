import { useCallback, useMemo, useState } from "react";
import type { AssessmentResponse, ViewKey } from "./types";
import { runAssessment, ApiError } from "./api";
import { configError } from "./config";
import ProgressSteps from "./components/ProgressSteps";
import ConsentScreen from "./components/ConsentScreen";
import CaptureScreen from "./components/CaptureScreen";
import ReviewScreen from "./components/ReviewScreen";
import ResultsScreen from "./components/ResultsScreen";

export type Step = "consent" | "capture" | "review" | "results";

export interface Shot {
  blob: Blob;
  url: string;
}
export type Shots = Partial<Record<ViewKey, Shot>>;

export const VIEW_ORDER: ViewKey[] = ["frontal", "oblique_left", "oblique_right", "profile"];

export const VIEW_LABEL: Record<ViewKey, string> = {
  frontal: "Frontal 0°",
  oblique_left: "Oblique 45° L",
  oblique_right: "Oblique 45° R",
  profile: "Profile 90°",
};

export default function App() {
  const [step, setStep] = useState<Step>("consent");
  const [shots, setShots] = useState<Shots>({});
  const [result, setResult] = useState<AssessmentResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const cfgErr = useMemo(() => configError(), []);

  const setShot = useCallback((key: ViewKey, blob: Blob) => {
    setShots((prev) => {
      const old = prev[key];
      if (old) URL.revokeObjectURL(old.url);
      return { ...prev, [key]: { blob, url: URL.createObjectURL(blob) } };
    });
  }, []);

  const clearShot = useCallback((key: ViewKey) => {
    setShots((prev) => {
      const old = prev[key];
      if (old) URL.revokeObjectURL(old.url);
      const next = { ...prev };
      delete next[key];
      return next;
    });
  }, []);

  const analyze = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const inputs = VIEW_ORDER.filter((k) => shots[k]).map((k) => ({
        key: k,
        blob: shots[k]!.blob,
        filename: `${k}.jpg`,
      }));
      const res = await runAssessment(inputs);
      setResult(res);
      setStep("results");
    } catch (e) {
      if (e instanceof ApiError && e.status === 422) {
        setError("No face detected. Retake in better light with the face centered and well-lit.");
      } else if (e instanceof ApiError && e.status === 413) {
        setError("Image too large. Please retake — captures are normally well within the limit.");
      } else if (e instanceof ApiError) {
        setError(`Analysis failed (${e.status}): ${e.message}`);
      } else {
        setError(`Network error: ${(e as Error).message}. Check the connection and try again.`);
      }
    } finally {
      setLoading(false);
    }
  }, [shots]);

  const reset = useCallback(() => {
    setShots((prev) => {
      Object.values(prev).forEach((s) => s && URL.revokeObjectURL(s.url));
      return {};
    });
    setResult(null);
    setError(null);
    setStep("consent");
  }, []);

  if (cfgErr) {
    return (
      <div className="app">
        <header className="topbar">
          <div className="brand"><span className="logo-dot" /> Aesthetic Scan</div>
        </header>
        <main className="content">
          <div className="banner error">
            <strong>Configuration needed.</strong> {cfgErr}
          </div>
        </main>
      </div>
    );
  }

  return (
    <div className="app">
      <header className="topbar">
        <div className="brand"><span className="logo-dot" /> Aesthetic Scan</div>
        <span className="env-tag">EU · processed in-region</span>
      </header>
      <ProgressSteps step={step} />
      <main className="content">
        {step === "consent" && <ConsentScreen onStart={() => setStep("capture")} />}
        {step === "capture" && (
          <CaptureScreen
            shots={shots}
            onShot={setShot}
            onClear={clearShot}
            onDone={() => setStep("review")}
          />
        )}
        {step === "review" && (
          <ReviewScreen
            shots={shots}
            onRetake={() => setStep("capture")}
            onClear={clearShot}
            onAnalyze={analyze}
            loading={loading}
            error={error}
          />
        )}
        {step === "results" && result && (
          <ResultsScreen result={result} shots={shots} onReset={reset} />
        )}
      </main>
      <footer className="footer">
        DEV/TEST · consenting subjects only · not for clinical decisions
      </footer>
    </div>
  );
}
