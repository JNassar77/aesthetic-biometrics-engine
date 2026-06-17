"""Tests for image decoding, including HEIF/HEIC (iPhone) support."""

import io

import numpy as np
import pytest

from app.pipeline.image_preprocessor import decode_image, _looks_like_heif


def _make_heic(arr_rgb: np.ndarray) -> bytes:
    pillow_heif = pytest.importorskip("pillow_heif")
    from PIL import Image
    pillow_heif.register_heif_opener()
    buf = io.BytesIO()
    Image.fromarray(arr_rgb, "RGB").save(buf, format="HEIF")
    return buf.getvalue()


def _make_jpeg(arr_rgb: np.ndarray) -> bytes:
    from PIL import Image
    buf = io.BytesIO()
    Image.fromarray(arr_rgb, "RGB").save(buf, format="JPEG")
    return buf.getvalue()


@pytest.fixture
def sample_rgb():
    arr = np.zeros((120, 90, 3), dtype=np.uint8)
    arr[:, :, 0] = 200  # R
    arr[:, :, 1] = 120  # G
    arr[:, :, 2] = 40   # B
    return arr


class TestImageDecode:
    def test_heic_detected(self, sample_rgb):
        assert _looks_like_heif(_make_heic(sample_rgb))

    def test_heic_decodes_to_bgr(self, sample_rgb):
        img = decode_image(_make_heic(sample_rgb))
        assert img is not None
        assert img.shape == (120, 90, 3)
        # BGR order; HEIF is near-lossless so allow tolerance
        b, g, r = img[0, 0].tolist()
        assert abs(b - 40) < 20 and abs(g - 120) < 20 and abs(r - 200) < 20

    def test_jpeg_still_decodes(self, sample_rgb):
        img = decode_image(_make_jpeg(sample_rgb))
        assert img is not None
        assert img.shape == (120, 90, 3)

    def test_garbage_returns_none(self):
        assert decode_image(b"not an image at all") is None

    def test_empty_returns_none(self):
        assert decode_image(b"") is None
