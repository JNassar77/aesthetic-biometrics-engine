# ── Stage 1: Dependencies + model download ──
FROM python:3.11-slim-bookworm AS builder

WORKDIR /build

COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# Download the pinned MediaPipe Face Landmarker model at build time (it is not in
# git). The SHA256 is verified against the value pinned in
# app/detection/face_landmarker.py (EXPECTED_MODEL_SHA256) so the build FAILS on
# any drift — provenance/reproducibility for a medical-device model artifact.
ARG MODEL_VERSION=float16/1
ARG MODEL_SHA256=64184e229b263107bc2b804c6625db1341ff2bb731874b0bcc2fe6544e0bc9ff
RUN apt-get update && apt-get install -y --no-install-recommends curl ca-certificates \
    && mkdir -p /build/models \
    && curl -fsSL -o /build/models/face_landmarker.task \
       "https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/${MODEL_VERSION}/face_landmarker.task" \
    && echo "${MODEL_SHA256}  /build/models/face_landmarker.task" | sha256sum -c - \
    && apt-get purge -y curl && apt-get autoremove -y && rm -rf /var/lib/apt/lists/*

# ── Stage 2: Runtime ──
FROM python:3.11-slim-bookworm

WORKDIR /app

# System libs required by OpenCV headless + MediaPipe 0.10.35 (needs GLES/EGL)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 \
    libglib2.0-0 \
    libgles2 \
    libegl1 \
    && rm -rf /var/lib/apt/lists/*

# Copy installed Python packages from builder
COPY --from=builder /install /usr/local

# Copy application code + the verified model from the builder stage
COPY app/ app/
COPY --from=builder /build/models/ models/

# Non-root user for security
RUN useradd --create-home appuser
USER appuser

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/api/v2/health')" || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
