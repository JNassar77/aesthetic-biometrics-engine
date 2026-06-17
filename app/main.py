import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v2_routes import router as v2_router
from app.api.rate_limit import RateLimitMiddleware
from app.config import settings
from app.pipeline.orchestrator import get_landmarker
from app.utils.logging import setup_logging
from app.version import ENGINE_VERSION

setup_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Warm the shared face landmarker once at startup (model ~3.6 MB)."""
    try:
        get_landmarker()
        logger.info("Face landmarker pre-loaded at startup.")
    except FileNotFoundError as exc:
        logger.warning("Face landmarker not pre-loaded: %s", exc)
    yield


app = FastAPI(
    title="Aesthetic Biometrics Engine",
    description=(
        "AI-powered biometric facial analysis for aesthetic medicine.\n\n"
        "Extracts 478 facial landmarks from standardized photographs "
        "(frontal 0°, oblique 45°, profile 90°) and provides:\n"
        "- **19-zone analysis** with severity scoring\n"
        "- **Treatment planning** with product recommendations\n"
        "- **Before/After comparison** with improvement metrics\n"
        "- **Patient history** tracking via Supabase\n\n"
        "### Authentication\n"
        "Set `X-API-Key` header. In dev mode (no API_KEYS configured), "
        "authentication is bypassed.\n\n"
        "### Rate Limiting\n"
        f"Default: {settings.rate_limit_rpm} requests/minute per IP. "
        "Health endpoints are exempt."
    ),
    version=ENGINE_VERSION,
    contact={"name": "Praxis Nassar", "email": "info@praxis-nassar.de"},
    license_info={"name": "Proprietary"},
    openapi_tags=[
        {
            "name": "v2-assessment",
            "description": "V2 Zone-based analysis, comparison, and patient history.",
        },
    ],
    lifespan=lifespan,
)

# Rate limiting middleware (must be added before CORS)
app.add_middleware(RateLimitMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# V2 Zone-based endpoints
app.include_router(v2_router, prefix="/api/v2", tags=["v2-assessment"])


@app.get("/", tags=["root"])
async def root():
    return {
        "service": "Aesthetic Biometrics Engine",
        "version": ENGINE_VERSION,
        "docs": "/docs",
        "endpoints": {
            "v2_assessment": "/api/v2/assessment",
            "v2_compare": "/api/v2/compare",
            "v2_health": "/api/v2/health",
        },
    }
