"""Offline validation of the multi-view 3D reconstruction on REAL photos.

Why this exists: the synthetic round-trip tests prove the math is exact under the
orthographic model, but they cannot catch a real-data convention mismatch (e.g. a
y-axis flip between MediaPipe's transformation matrix and image-space landmarks).
This script runs the full detect -> calibrate -> reconstruct path on real captures
and checks the reconstruction against an anatomical oracle:

    interpupillary distance (iris-centre to iris-centre) should land in 58-66 mm
    (population norm ~63 mm), and reprojection RMS should be small (a few mm).

Usage (model + photos are gitignored, so this is a manual tool, not a CI test):

    .venv/Scripts/python.exe scripts/validate_3d_reconstruction.py [IMAGE_DIR]

IMAGE_DIR defaults to test_images/. Filenames are matched heuristically by the
substrings "frontal", "oblique"/"obliqu" (+ "link"/"links" / "recht"/"rechts"),
and "profil".
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.analysis.multiview_reconstruction import (  # noqa: E402
    reconstruct_from_views,
    RECONSTRUCTION_EXCLUDED_VIEWS,
)
from app.detection.face_landmarker import FaceLandmarkerV2  # noqa: E402
from app.pipeline.image_preprocessor import preprocess, reprocess_with_face_center  # noqa: E402
from app.utils.pixel_calibration import calibrate  # noqa: E402
from app.detection.head_pose import extract_head_pose  # noqa: E402

# Iris centre landmarks (MediaPipe refine_landmarks).
LEFT_IRIS_CENTER = 468
RIGHT_IRIS_CENTER = 473


def _classify(name: str) -> str | None:
    n = name.lower()
    if "frontal" in n:
        return "frontal"
    if "profil" in n:
        return "profile"
    if "obliqu" in n or "oblique" in n:
        if "link" in n:
            return "oblique_left"
        if "recht" in n:
            return "oblique_right"
        return "oblique"
    return None


def main(image_dir: str) -> int:
    d = Path(image_dir)
    if not d.is_dir():
        print(f"Image dir not found: {d}")
        return 1

    files: dict[str, Path] = {}
    for p in sorted(d.iterdir()):
        if p.suffix.lower() not in {".jpg", ".jpeg", ".png", ".heic", ".webp"}:
            continue
        view = _classify(p.name)
        if view and view not in files:
            files[view] = p

    if not files:
        print(f"No view images found in {d}")
        return 1

    print("Detected views:")
    for v, p in files.items():
        print(f"  {v:14s} <- {p.name}")
    print()

    landmarker = FaceLandmarkerV2()
    views_for_recon = []

    for view, path in files.items():
        image = preprocess(path.read_bytes(), apply_face_crop=False)
        if image is None:
            print(f"  [{view}] decode failed")
            continue
        det = landmarker.detect(image)
        if not getattr(det, "face_detected", False):
            print(f"  [{view}] no face detected")
            continue
        # Reprocess centred on the face, like the orchestrator does.
        rep = reprocess_with_face_center(image, det.landmarks, det.image_width, det.image_height)
        det2 = landmarker.detect(rep)
        if getattr(det2, "face_detected", False):
            det = det2
        cal = calibrate(det.landmarks, det.image_width, det.image_height)
        pose = extract_head_pose(det.transformation_matrix)
        pose_str = (
            f"yaw={pose.yaw:+.1f} pitch={pose.pitch:+.1f} roll={pose.roll:+.1f}"
            if pose else "no-pose"
        )
        excluded = " [excluded from 3D by policy]" if view in RECONSTRUCTION_EXCLUDED_VIEWS else ""
        print(
            f"  [{view}] face ok | cal={cal.method} ppmm={cal.px_per_mm:.2f} "
            f"conf={cal.confidence:.2f} | {pose_str}{excluded}"
        )
        views_for_recon.append((view, det, cal))

    print()
    # Use the production reconstruction policy (excludes profile, requires iris).
    rec = reconstruct_from_views(views_for_recon)
    if rec is None:
        print("reconstruct_from_views returned None (need >=2 qualifying views + spread).")
        return 1

    interpupillary = rec.distance(LEFT_IRIS_CENTER, RIGHT_IRIS_CENTER)
    iris_w_left = rec.distance(469, 471)
    iris_w_right = rec.distance(474, 476)

    print("=== Reconstruction ===")
    print(f"  views used         : {rec.views_used}")
    print(f"  n_views            : {rec.n_views}")
    print(f"  angular spread     : {rec.angular_spread_deg}°")
    print(f"  reprojection RMS   : {rec.reprojection_rms_mm} mm")
    print()
    print("=== Anatomical oracle (metric scale check) ===")
    print(f"  interpupillary     : {interpupillary:.1f} mm   (norm 58-66, ~63)")
    print(f"  iris width (left)  : {iris_w_left:.1f} mm   (norm ~11.7)")
    print(f"  iris width (right) : {iris_w_right:.1f} mm   (norm ~11.7)")
    print()

    ok = 58.0 <= interpupillary <= 66.0
    print("RESULT:", "PASS — metric scale plausible" if ok
          else "CHECK — interpupillary outside anatomical norm (convention?)")
    return 0 if ok else 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1] if len(sys.argv) > 1 else str(ROOT / "test_images")))
