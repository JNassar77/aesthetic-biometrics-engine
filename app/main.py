from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1_routes import router as v1_router
from app.api.v2_routes import router as v2_router
from app.api.rate_limit import RateLimitMiddleware
from app.config import settings
from app.utils.logging import setup_logging

setup_logging()

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
    version="2.1.0",
    contact={"name": "Praxis Nassar", "email": "info@praxis-nassar.de"},
    license_info={"name": "Proprietary"},
    openapi_tags=[
        {
            "name": "v2-assessment",
            "description": "V2 Zone-based analysis, comparison, and patient history.",
        },
        {
            "name": "v1-legacy",
            "description": "V1 Legacy endpoints (backward compatibility).",
        },
    ],
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

# V1 Legacy endpoints (backward compatibility)
app.include_router(v1_router, prefix="/api/v1", tags=["v1-legacy"])

# V2 Zone-based endpoints
app.include_router(v2_router, prefix="/api/v2", tags=["v2-assessment"])


@app.get("/", tags=["root"])
async def root():
    return {
        "service": "Aesthetic Biometrics Engine",
        "version": "2.1.0",
        "docs": "/docs",
        "endpoints": {
            "v2_assessment": "/api/v2/assessment",
            "v2_compare": "/api/v2/compare",
            "v2_health": "/api/v2/health",
            "v1_analyze": "/api/v1/analyze",
            "v1_health": "/api/v1/health",
        },
    }
