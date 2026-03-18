import httpx
from supabase import create_client, Client
from app.config import settings


_client: Client | None = None


def get_client() -> Client:
    global _client
    if _client is None:
        _client = create_client(settings.supabase_url, settings.supabase_key)
    return _client


async def save_analysis(patient_id: str, view_angle: str, result: dict) -> dict:
    """Insert analysis result into Supabase."""
    client = get_client()
    row = {
        "patient_id": patient_id,
        "view_angle": view_angle,
        "result_json": result,
        "confidence": result.get("confidence", 0),
        "landmarks_detected": result.get("landmarks_detected", 0),
    }
    resp = client.table("biometric_analyses").insert(row).execute()
    return resp.data[0] if resp.data else {}


async def fetch_image_from_url(url: str) -> bytes:
    """Download image bytes from a Supabase storage URL."""
    async with httpx.AsyncClient() as http:
        resp = await http.get(url, timeout=30)
        resp.raise_for_status()
        return resp.content
