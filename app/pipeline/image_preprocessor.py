"""
Image preprocessing pipeline.

Steps:
1. Decode image bytes → OpenCV array
2. Fix EXIF orientation (phone cameras rotate metadata, not pixels)
3. Normalize face crop (center square, eliminates lens edge distortion)
4. Resize to standard resolution for consistent landmark detection
"""

import cv2
import numpy as np

TARGET_SIZE = 1024
FACE_PADDING_RATIO = 0.35  # 35% padding around detected face


def decode_image(image_bytes: bytes) -> np.ndarray | None:
    """Decode raw bytes into BGR numpy array. Returns None on failure."""
    if not image_bytes:
        return None
    arr = np.frombuffer(image_bytes, np.uint8)
    try:
        image = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    except cv2.error:
        return None
    return image


def fix_exif_orientation(image: np.ndarray, image_bytes: bytes) -> np.ndarray:
    """Rotate image based on EXIF orientation tag.

    Mobile cameras often store the image in one orientation but set an EXIF
    tag indicating the correct rotation. OpenCV ignores EXIF, so we fix it.
    """
    # Check for EXIF orientation marker in JPEG
    # EXIF starts with 0xFFE1, orientation tag is 0x0112
    try:
        # Simple EXIF orientation detection without PIL dependency
        # Look for orientation tag in JPEG APP1 segment
        if len(image_bytes) < 12:
            return image

        # Check if JPEG
        if image_bytes[0:2] != b'\xff\xd8':
            return image

        # Find EXIF APP1 marker
        offset = 2
        while offset < min(len(image_bytes), 65536):
            if image_bytes[offset] != 0xFF:
                break
            marker = image_bytes[offset + 1]
            if marker == 0xE1:  # APP1 (EXIF)
                # Parse EXIF to find orientation
                exif_data = image_bytes[offset + 4:offset + 4 + 256]
                orientation = _parse_exif_orientation(exif_data)
                return _apply_orientation(image, orientation)
            # Skip to next marker
            segment_len = int.from_bytes(image_bytes[offset + 2:offset + 4], 'big')
            offset += 2 + segment_len
    except Exception:
        pass  # If EXIF parsing fails, return image as-is

    return image


def _parse_exif_orientation(exif_data: bytes) -> int:
    """Extract orientation value from EXIF data. Returns 1 (normal) on failure."""
    try:
        if exif_data[:4] != b'Exif':
            return 1

        # Determine byte order
        tiff_header = exif_data[6:]
        if tiff_header[:2] == b'MM':
            byte_order = 'big'
        elif tiff_header[:2] == b'II':
            byte_order = 'little'
        else:
            return 1

        # Find IFD0
        ifd_offset = int.from_bytes(tiff_header[4:8], byte_order)
        num_entries = int.from_bytes(tiff_header[ifd_offset:ifd_offset + 2], byte_order)

        for i in range(min(num_entries, 20)):
            entry_offset = ifd_offset + 2 + i * 12
            tag = int.from_bytes(tiff_header[entry_offset:entry_offset + 2], byte_order)
            if tag == 0x0112:  # Orientation tag
                return int.from_bytes(tiff_header[entry_offset + 8:entry_offset + 10], byte_order)
    except Exception:
        pass
    return 1


def _apply_orientation(image: np.ndarray, orientation: int) -> np.ndarray:
    """Apply EXIF orientation transform."""
    if orientation == 1:
        return image
    elif orientation == 2:
        return cv2.flip(image, 1)
    elif orientation == 3:
        return cv2.rotate(image, cv2.ROTATE_180)
    elif orientation == 4:
        return cv2.flip(image, 0)
    elif orientation == 5:
        return cv2.flip(cv2.rotate(image, cv2.ROTATE_90_COUNTERCLOCKWISE), 1)
    elif orientation == 6:
        return cv2.rotate(image, cv2.ROTATE_90_CLOCKWISE)
    elif orientation == 7:
        return cv2.flip(cv2.rotate(image, cv2.ROTATE_90_CLOCKWISE), 1)
    elif orientation == 8:
        return cv2.rotate(image, cv2.ROTATE_90_COUNTERCLOCKWISE)
    return image


def normalize_face_crop(
    image: np.ndarray,
    face_center: tuple[float, float] | None = None,
    face_size: float | None = None,
) -> np.ndarray:
    """Crop image to center square around face, eliminating edge lens distortion.

    If face_center/face_size are not provided, crops to center of image.

    Args:
        image: BGR image
        face_center: (cx, cy) pixel coordinates of face center
        face_size: approximate face bounding box size in pixels

    Returns:
        Square cropped and resized image (TARGET_SIZE x TARGET_SIZE)
    """
    h, w = image.shape[:2]

    if face_center is None:
        cx, cy = w / 2, h / 2
    else:
        cx, cy = face_center

    if face_size is None:
        # Default: use 70% of shorter dimension as face size estimate
        face_size = min(w, h) * 0.7

    # Square crop with padding
    half = int(face_size / 2 * (1 + FACE_PADDING_RATIO))
    half = max(half, 100)  # minimum crop size

    x1 = max(0, int(cx - half))
    y1 = max(0, int(cy - half))
    x2 = min(w, int(cx + half))
    y2 = min(h, int(cy + half))

    crop = image[y1:y2, x1:x2]

    if crop.size == 0:
        return cv2.resize(image, (TARGET_SIZE, TARGET_SIZE))

    return cv2.resize(crop, (TARGET_SIZE, TARGET_SIZE))


def preprocess(
    image_bytes: bytes,
    apply_face_crop: bool = True,
) -> np.ndarray | None:
    """Full preprocessing pipeline.

    Args:
        image_bytes: Raw image file bytes (JPEG/PNG)
        apply_face_crop: Whether to apply center face crop (lens distortion fix)

    Returns:
        Preprocessed BGR image or None if decode fails.
    """
    image = decode_image(image_bytes)
    if image is None:
        return None

    image = fix_exif_orientation(image, image_bytes)

    if apply_face_crop:
        # First pass: simple center crop without face detection
        # (Face detection happens after preprocessing)
        image = normalize_face_crop(image)

    return image
