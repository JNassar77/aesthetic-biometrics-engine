"""Tests for image preprocessing pipeline."""

import cv2
import numpy as np
import pytest
from app.pipeline.image_preprocessor import (
    decode_image,
    normalize_face_crop,
    _apply_orientation,
    TARGET_SIZE,
)


class TestDecodeImage:
    def test_valid_jpeg(self):
        image = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
        _, buf = cv2.imencode(".jpg", image)
        result = decode_image(buf.tobytes())
        assert result is not None
        assert result.shape[2] == 3

    def test_valid_png(self):
        image = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
        _, buf = cv2.imencode(".png", image)
        result = decode_image(buf.tobytes())
        assert result is not None

    def test_invalid_bytes(self):
        result = decode_image(b"not an image")
        assert result is None

    def test_empty_bytes(self):
        result = decode_image(b"")
        assert result is None


class TestNormalizeFaceCrop:
    def test_output_is_square(self):
        image = np.random.randint(0, 255, (1080, 1920, 3), dtype=np.uint8)
        result = normalize_face_crop(image)
        assert result.shape[0] == TARGET_SIZE
        assert result.shape[1] == TARGET_SIZE

    def test_with_face_center(self):
        image = np.random.randint(0, 255, (1080, 1920, 3), dtype=np.uint8)
        result = normalize_face_crop(image, face_center=(960, 540), face_size=400)
        assert result.shape == (TARGET_SIZE, TARGET_SIZE, 3)

    def test_face_at_edge(self):
        image = np.random.randint(0, 255, (500, 500, 3), dtype=np.uint8)
        result = normalize_face_crop(image, face_center=(10, 10), face_size=200)
        assert result.shape[0] == TARGET_SIZE  # Should still produce valid output

    def test_small_image(self):
        image = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
        result = normalize_face_crop(image)
        assert result.shape == (TARGET_SIZE, TARGET_SIZE, 3)


class TestExifOrientation:
    def test_no_rotation(self):
        image = np.zeros((100, 200, 3), dtype=np.uint8)
        result = _apply_orientation(image, 1)
        assert result.shape == (100, 200, 3)

    def test_rotate_180(self):
        image = np.zeros((100, 200, 3), dtype=np.uint8)
        image[0, 0] = [255, 0, 0]  # Mark top-left
        result = _apply_orientation(image, 3)
        assert result.shape == (100, 200, 3)
        assert np.array_equal(result[99, 199], [255, 0, 0])  # Now bottom-right

    def test_rotate_90_cw(self):
        image = np.zeros((100, 200, 3), dtype=np.uint8)
        result = _apply_orientation(image, 6)
        assert result.shape == (200, 100, 3)  # Width/height swapped

    def test_rotate_90_ccw(self):
        image = np.zeros((100, 200, 3), dtype=np.uint8)
        result = _apply_orientation(image, 8)
        assert result.shape == (200, 100, 3)
