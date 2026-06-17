# Test Images — local only, never committed

Drop face photos here for end-to-end testing. **This folder is gitignored** —
real face photos are biometric/personal data (DSGVO Art. 9) and must not be committed.

## What to drop

- **Quick functional test:** any clear face photo — JPEG / PNG / WebP / **HEIC** (iPhone) all work.
- **3D depth / mm accuracy:** three photos of the *same person*, same session,
  neutral expression, eyes clearly visible, even lighting:
  - `<name>_frontal.jpg` — 0° (straight on)
  - `<name>_oblique.jpg` — 45° (turned half)
  - `<name>_profile.jpg` — 90° (full side)

iPhone HEIC is supported directly — no need to convert.
