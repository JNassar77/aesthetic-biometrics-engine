import httpx
from app.config import settings


async def notify_n8n(payload: dict) -> bool:
    """Send analysis result to n8n webhook for downstream processing."""
    if not settings.n8n_webhook_url:
        return False

    try:
        async with httpx.AsyncClient() as http:
            resp = await http.post(
                settings.n8n_webhook_url,
                json=payload,
                timeout=15,
            )
            return resp.status_code < 400
    except httpx.HTTPError:
        return False
