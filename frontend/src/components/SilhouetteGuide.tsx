import type { ViewKey } from "../types";

/**
 * Semi-transparent face-silhouette guide drawn over the live camera. Purely a
 * framing aid — final pose is validated server-side by the quality gate.
 */
export default function SilhouetteGuide({ view }: { view: ViewKey }) {
  return (
    <svg
      className="silhouette"
      viewBox="0 0 200 280"
      preserveAspectRatio="xMidYMid meet"
      aria-hidden="true"
    >
      {view === "frontal" && (
        <g>
          <ellipse cx="100" cy="120" rx="56" ry="76" />
          <line x1="100" y1="48" x2="100" y2="196" className="thin" />
          <line x1="52" y1="112" x2="148" y2="112" className="thin" />
        </g>
      )}
      {view === "oblique_left" && (
        <g transform="rotate(-10 104 120)">
          <ellipse cx="104" cy="120" rx="50" ry="76" />
          <line x1="118" y1="50" x2="118" y2="192" className="thin" />
        </g>
      )}
      {view === "oblique_right" && (
        <g transform="rotate(10 96 120)">
          <ellipse cx="96" cy="120" rx="50" ry="76" />
          <line x1="82" y1="50" x2="82" y2="192" className="thin" />
        </g>
      )}
      {view === "profile" && (
        <path
          d="M126 50
             C 96 50, 80 78, 80 104
             C 80 116, 74 122, 66 130
             C 60 136, 64 142, 74 146
             C 76 158, 78 172, 92 182
             C 104 190, 120 192, 132 190
             L 132 196
             C 110 202, 86 198, 78 196"
          fill="none"
        />
      )}
    </svg>
  );
}
