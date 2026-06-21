import type { Shots } from "../App";
import { VIEW_ORDER, VIEW_LABEL } from "../App";

export default function ReviewScreen({
  shots,
  onRetake,
  onClear,
  onAnalyze,
  loading,
  error,
}: {
  shots: Shots;
  onRetake: () => void;
  onClear: (k: import("../types").ViewKey) => void;
  onAnalyze: () => void;
  loading: boolean;
  error: string | null;
}) {
  const present = VIEW_ORDER.filter((k) => shots[k]);

  return (
    <section className="screen review">
      <h2>Review your photos</h2>
      <p className="muted">
        Check each angle is correct. Retake any that look off, then analyze. At least one view is
        required; all four give the most accurate result.
      </p>

      <div className="review-grid">
        {VIEW_ORDER.map((k) => {
          const shot = shots[k];
          return (
            <div key={k} className={`review-card ${shot ? "" : "missing"}`}>
              <div className="review-img">
                {shot ? <img src={shot.url} alt={k} /> : <span className="muted">Not captured</span>}
              </div>
              <div className="review-meta">
                <span>{VIEW_LABEL[k]}</span>
                {shot && (
                  <button className="link" onClick={() => onClear(k)} disabled={loading}>
                    Clear
                  </button>
                )}
              </div>
            </div>
          );
        })}
      </div>

      {error && <div className="banner error">{error}</div>}

      <div className="review-actions">
        <button className="btn ghost" onClick={onRetake} disabled={loading}>
          ← Back to capture
        </button>
        <button
          className="btn primary"
          onClick={onAnalyze}
          disabled={loading || present.length === 0}
        >
          {loading ? "Analyzing…" : `Analyze ${present.length} view${present.length === 1 ? "" : "s"}`}
        </button>
      </div>

      {loading && <div className="analyzing-hint muted">Running the biometric analysis — this can take a few seconds.</div>}
    </section>
  );
}
