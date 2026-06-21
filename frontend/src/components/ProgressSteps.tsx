import type { Step } from "../App";

const STEPS: { key: Step; label: string }[] = [
  { key: "consent", label: "Consent" },
  { key: "capture", label: "Capture" },
  { key: "review", label: "Review" },
  { key: "results", label: "Results" },
];

export default function ProgressSteps({ step }: { step: Step }) {
  const activeIdx = STEPS.findIndex((s) => s.key === step);
  return (
    <nav className="progress" aria-label="Progress">
      {STEPS.map((s, i) => (
        <div
          key={s.key}
          className={`progress-step ${i === activeIdx ? "active" : ""} ${i < activeIdx ? "done" : ""}`}
          aria-current={i === activeIdx ? "step" : undefined}
        >
          <span className="dot">{i < activeIdx ? "✓" : i + 1}</span>
          <span className="label">{s.label}</span>
        </div>
      ))}
    </nav>
  );
}
