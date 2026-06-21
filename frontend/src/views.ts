import type { ViewKey } from "./types";

const OBLIQUE_VIEWS: ViewKey[] = ["oblique_left", "oblique_right"];

/**
 * Map an engine CANONICAL overlay view name ("frontal" | "oblique" | "profile")
 * to the PHYSICAL uploaded view we hold a photo for, so a heatmap renders on the
 * correct image.
 *
 * For "oblique": prefer the engine's explicit `canonicalObliqueView`; otherwise
 * resolve only when unambiguous (exactly one oblique present + analyzed). With
 * both obliques and no hint (older engine), return undefined — skip the heatmap
 * rather than risk drawing it on the wrong cheek.
 */
export function physicalForCanonical(
  canon: string,
  hasShot: (k: ViewKey) => boolean,
  analyzed: readonly string[],
  canonicalObliqueView: string | null | undefined,
): ViewKey | undefined {
  if (canon === "oblique") {
    if (canonicalObliqueView && hasShot(canonicalObliqueView as ViewKey)) {
      return canonicalObliqueView as ViewKey;
    }
    const present = OBLIQUE_VIEWS.filter((k) => hasShot(k) && analyzed.includes(k));
    return present.length === 1 ? present[0] : undefined;
  }
  // frontal / profile / any direct match → same physical key (if we have it).
  return hasShot(canon as ViewKey) ? (canon as ViewKey) : undefined;
}
