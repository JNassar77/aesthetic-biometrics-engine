import { useState } from "react";

export default function ConsentScreen({ onStart }: { onStart: () => void }) {
  const [agreed, setAgreed] = useState(false);
  return (
    <section className="screen consent">
      <h1>Facial aesthetic analysis</h1>
      <p className="lead">
        This app takes four standardized photos of your face (front, two 45° angles, and a
        side profile) and returns a visual analysis with a downloadable PDF report. Photos are
        processed in the EU.
      </p>
      <label className="consent-box">
        <input
          type="checkbox"
          checked={agreed}
          onChange={(e) => setAgreed(e.target.checked)}
        />
        <span>
          I consent to my facial photographs being processed for this aesthetic analysis.
        </span>
      </label>
      <button className="btn primary wide" disabled={!agreed} onClick={onStart}>
        Start
      </button>
      <p className="fine-print">
        DEV/TEST environment — for consenting test subjects only. Not a medical device; results
        must not be used for clinical decisions.
      </p>
    </section>
  );
}
