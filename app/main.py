from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1_routes import router as v1_router
from app.api.v2_routes import router as v2_router
from app.config import settings
from app.utils.logging import setup_logging

setup_logging()

app = FastAPI(
    title="Aesthetic Biometrics Engine",
    description="Biometric facial analysis for aesthetic medicine. "
                "Multi-view zone-based analysis with treatment planning "
                "for Botulinum toxin and dermal fillers.",
    version="2.0.0",
)

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


@app.get("/")
async def root():
    return {
        "service": "Aesthetic Biometrics Engine",
        "version": "2.0.0",
        "docs": "/docs",
        "endpoints": {
            "v2_assessment": "/api/v2/assessment",
            "v2_compare": "/api/v2/compare",
            "v2_health": "/api/v2/health",
            "v1_analyze": "/api/v1/analyze",
            "v1_health": "/api/v1/health",
        },
    }
