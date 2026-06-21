import { describe, it, expect } from "vitest";
import { physicalForCanonical } from "./views";
import type { ViewKey } from "./types";

const has = (...keys: ViewKey[]) => (k: ViewKey) => keys.includes(k);

describe("physicalForCanonical", () => {
  it("maps frontal/profile to themselves when present", () => {
    expect(physicalForCanonical("frontal", has("frontal"), ["frontal"], null)).toBe("frontal");
    expect(physicalForCanonical("profile", has("profile"), ["profile"], null)).toBe("profile");
  });

  it("returns undefined for a canonical view whose photo we don't have", () => {
    expect(physicalForCanonical("frontal", has(), [], null)).toBeUndefined();
  });

  it("uses the engine's explicit canonical_oblique_view", () => {
    expect(
      physicalForCanonical("oblique", has("oblique_left", "oblique_right"),
        ["frontal", "oblique_left", "oblique_right"], "oblique_right"),
    ).toBe("oblique_right");
  });

  it("resolves oblique unambiguously when only one oblique is present + analyzed", () => {
    expect(
      physicalForCanonical("oblique", has("oblique_left"), ["frontal", "oblique_left"], null),
    ).toBe("oblique_left");
  });

  it("returns undefined for oblique when ambiguous (both present, no engine hint)", () => {
    expect(
      physicalForCanonical("oblique", has("oblique_left", "oblique_right"),
        ["frontal", "oblique_left", "oblique_right"], null),
    ).toBeUndefined();
  });

  it("ignores an explicit oblique view we have no photo for, falling back to the unambiguous one", () => {
    expect(
      physicalForCanonical("oblique", has("oblique_left"), ["oblique_left"], "oblique_right"),
    ).toBe("oblique_left");
  });
});
