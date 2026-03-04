"""
HTTP Client für die knews Data API (https://api.knews.press).

Auth: KNEWS_API_KEY Umgebungsvariable → X-Api-Key Header.
Fehler werden als Strings zurückgegeben, nicht als Exceptions —
so dass MCP Tools niemals crashen.
"""

import os
from typing import Any

import httpx

API_BASE = "https://api.knews.press"
DEFAULT_TIMEOUT = 30.0


def _get_api_key() -> str | None:
    return os.environ.get("KNEWS_API_KEY")


def _make_headers() -> dict[str, str]:
    key = _get_api_key()
    if key:
        return {"X-Api-Key": key}
    return {}


async def api_get(path: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
    """
    Führt einen GET-Request gegen die knews API aus.

    Returns:
        dict mit "ok": True und den Antwortdaten — oder "ok": False und "error": str.
    """
    key = _get_api_key()
    if not key:
        return {
            "ok": False,
            "error": (
                "Kein API Key konfiguriert. "
                "Bitte setze die Umgebungsvariable KNEWS_API_KEY. "
                "Einen API Key erhältst du unter https://knews.press/portal"
            ),
        }

    # Remove None values from params
    clean_params: dict[str, Any] = {}
    if params:
        for k, v in params.items():
            if v is not None:
                clean_params[k] = v

    url = f"{API_BASE}{path}"
    headers = {"X-Api-Key": key, "User-Agent": "knews-mcp/0.2.0"}

    try:
        async with httpx.AsyncClient(timeout=DEFAULT_TIMEOUT) as client:
            response = await client.get(url, params=clean_params, headers=headers)

        if response.status_code == 200:
            return {"ok": True, "data": response.json()}
        elif response.status_code == 401:
            return {"ok": False, "error": "Ungültiger API Key. Bitte prüfe KNEWS_API_KEY."}
        elif response.status_code == 403:
            return {
                "ok": False,
                "error": (
                    f"Kein Zugriff (403 Forbidden). "
                    f"Dein API Key hat nicht den erforderlichen Scope für {path}. "
                    f"Upgrade dein Abonnement unter https://knews.press/portal"
                ),
            }
        elif response.status_code == 429:
            return {
                "ok": False,
                "error": "Rate Limit überschritten (429). Bitte warte einen Moment und versuche es erneut.",
            }
        elif response.status_code == 404:
            return {"ok": False, "error": f"Nicht gefunden (404): {path}"}
        else:
            try:
                detail = response.json().get("detail", response.text[:200])
            except Exception:
                detail = response.text[:200]
            return {
                "ok": False,
                "error": f"API Fehler {response.status_code}: {detail}",
            }

    except httpx.TimeoutException:
        return {
            "ok": False,
            "error": f"Timeout beim Abrufen von {url} (>{DEFAULT_TIMEOUT}s). Die API ist möglicherweise überlastet.",
        }
    except httpx.ConnectError:
        return {
            "ok": False,
            "error": f"Verbindungsfehler zu {API_BASE}. Bitte prüfe deine Internetverbindung.",
        }
    except Exception as exc:
        return {"ok": False, "error": f"Unerwarteter Fehler: {type(exc).__name__}: {exc}"}
