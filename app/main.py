from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import router
from app.config import settings

app = FastAPI(
    title="Aesthetic Biometrics Engine",
    description="Biometric facial analysis for aesthetic medicine. "
                "Extracts objective measurements from frontal, oblique, and profile images "
                "to support treatment planning with Botulinum toxin and dermal fillers.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api/v1", tags=["analysis"])


@app.get("/")
async def root():
    return {
        "service": "Aesthetic Biometrics Engine",
        "version": "0.1.0",
        "docs": "/docs",
        "endpoints": {
            "analyze": "/api/v1/analyze",
            "health": "/api/v1/health",
        },
    }
