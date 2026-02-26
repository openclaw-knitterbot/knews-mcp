"""
MCP Resources für die knews Datenplattform.

Stellt browsbare Datenquellen als MCP Resources bereit:
- Statische Resources: Feeds-Liste, SMARD-Filter-Übersicht
- Dynamische Resource Templates: Unternehmen, Berichte, Drucksachen, Energie, Förderung

URI-Schema: knews://{bereich}/{id}

Registrierung: register_resources(server) in server.py aufrufen.
"""

import re
from typing import Any

from mcp.server import Server
from mcp.types import (
    AnyUrl,
    Resource,
    ResourceTemplate,
    TextResourceContents,
)

from .client import api_get
from .formatting import (
    format_error,
    format_energie_filters,
    format_energie_timeseries,
    format_foerderung_programm,
    format_bundestag_drucksache,
    format_bundesanzeiger_report,
    format_handelsregister_company,
    format_news_feeds,
)


# ---------------------------------------------------------------------------
# Hilfsfunktion: URI → Kategorie + ID parsen
# ---------------------------------------------------------------------------

def _parse_uri(uri: str) -> tuple[str, str]:
    """
    Zerlegt eine knews://-URI in (pfad, id).

    Beispiele:
      knews://company/12345          → ("company", "12345")
      knews://bundesanzeiger/report/99 → ("bundesanzeiger/report", "99")
      knews://energie/filter/4169    → ("energie/filter", "4169")
    """
    # URI-Objekte von Pydantic als String normalisieren
    uri_str = str(uri)
    # knews://company/12345 → company/12345
    match = re.match(r"knews://(.+)/([^/]+)$", uri_str)
    if not match:
        return (uri_str, "")
    return (match.group(1), match.group(2))


def _text_resource(uri: AnyUrl, text: str) -> list[TextResourceContents]:
    """Erzeugt eine einzige TextResourceContents-Antwort."""
    return [TextResourceContents(uri=uri, mimeType="text/plain", text=text)]


# ---------------------------------------------------------------------------
# Statische Resource-Definitionen
# ---------------------------------------------------------------------------

STATIC_RESOURCES: list[Resource] = [
    Resource(
        uri=AnyUrl("knews://feeds"),  # type: ignore[arg-type]
        name="knews-news-feeds",
        description="Liste aller verfügbaren News-Feeds der knews Datenplattform (60+ Quellen)",
        mimeType="text/plain",
    ),
    Resource(
        uri=AnyUrl("knews://energie/filters"),  # type: ignore[arg-type]
        name="knews-energie-smard-filter",
        description="Alle verfügbaren SMARD-Datenreihen (Filter-IDs für Stromerzeugung/-verbrauch)",
        mimeType="text/plain",
    ),
]

# ---------------------------------------------------------------------------
# Resource Templates (dynamische URIs)
# ---------------------------------------------------------------------------

RESOURCE_TEMPLATES: list[ResourceTemplate] = [
    ResourceTemplate(
        uriTemplate="knews://company/{id}",
        name="knews-handelsregister-company",
        description="Handelsregister-Unternehmensprofil: Stammdaten + Organe/Personen",
        mimeType="text/plain",
    ),
    ResourceTemplate(
        uriTemplate="knews://bundesanzeiger/report/{id}",
        name="knews-bundesanzeiger-report",
        description="Jahresabschluss-Bericht: Bilanz, GuV und Stammdaten aus dem Bundesanzeiger",
        mimeType="text/plain",
    ),
    ResourceTemplate(
        uriTemplate="knews://bundestag/drucksache/{id}",
        name="knews-bundestag-drucksache",
        description="Bundestag-Drucksache mit LLM-Klassifikation (Themen, Keywords)",
        mimeType="text/plain",
    ),
    ResourceTemplate(
        uriTemplate="knews://energie/filter/{id}",
        name="knews-energie-smard-timeseries",
        description="SMARD-Zeitreihe der letzten 7 Tage für einen Energie-Filter",
        mimeType="text/plain",
    ),
    ResourceTemplate(
        uriTemplate="knews://foerderung/programm/{id}",
        name="knews-foerderung-programm",
        description="Förderprogramm-Detail: Fördergeber, Berechtigte, Konditionen",
        mimeType="text/plain",
    ),
]


# ---------------------------------------------------------------------------
# Handler-Logik
# ---------------------------------------------------------------------------

async def _handle_feeds(uri: AnyUrl) -> list[TextResourceContents]:
    """Gibt alle News-Feeds zurück."""
    result = await api_get("/v1/news/feeds")
    if not result.get("ok"):
        return _text_resource(uri, format_error(result.get("error", "Unbekannter Fehler")))
    return _text_resource(uri, format_news_feeds(result["data"]))


async def _handle_energie_filters(uri: AnyUrl) -> list[TextResourceContents]:
    """Gibt alle SMARD-Filter zurück."""
    result = await api_get("/v1/energie/filters")
    if not result.get("ok"):
        return _text_resource(uri, format_error(result.get("error", "Unbekannter Fehler")))
    return _text_resource(uri, format_energie_filters(result["data"]))


async def _handle_company(uri: AnyUrl, company_id: str) -> list[TextResourceContents]:
    """Handelsregister-Unternehmen + Officers."""
    result = await api_get(f"/v1/handelsregister/companies/{company_id}")
    if not result.get("ok"):
        return _text_resource(uri, format_error(result.get("error", "Unbekannter Fehler")))
    return _text_resource(uri, format_handelsregister_company(result["data"]))


async def _handle_bundesanzeiger_report(uri: AnyUrl, report_id: str) -> list[TextResourceContents]:
    """Bundesanzeiger-Jahresabschluss mit Bilanz und GuV."""
    result = await api_get(f"/v1/bundesanzeiger/reports/{report_id}")
    if not result.get("ok"):
        return _text_resource(uri, format_error(result.get("error", "Unbekannter Fehler")))
    return _text_resource(uri, format_bundesanzeiger_report(result["data"]))


async def _handle_bundestag_drucksache(uri: AnyUrl, drucksache_id: str) -> list[TextResourceContents]:
    """Bundestag-Drucksache mit LLM-Klassifikation."""
    result = await api_get(f"/v1/bundestag/drucksachen/{drucksache_id}")
    if not result.get("ok"):
        return _text_resource(uri, format_error(result.get("error", "Unbekannter Fehler")))
    return _text_resource(uri, format_bundestag_drucksache(result["data"]))


async def _handle_energie_filter(uri: AnyUrl, filter_id: str) -> list[TextResourceContents]:
    """SMARD-Zeitreihe für einen Filter, letzte 7 Tage."""
    result = await api_get("/v1/energie/timeseries", params={"filter_id": filter_id, "days": 7})
    if not result.get("ok"):
        return _text_resource(uri, format_error(result.get("error", "Unbekannter Fehler")))
    return _text_resource(uri, format_energie_timeseries(result["data"]))


async def _handle_foerderung_programm(uri: AnyUrl, programm_id: str) -> list[TextResourceContents]:
    """Förderprogramm-Detail."""
    result = await api_get(f"/v1/foerderung/programme/{programm_id}")
    if not result.get("ok"):
        return _text_resource(uri, format_error(result.get("error", "Unbekannter Fehler")))
    return _text_resource(uri, format_foerderung_programm(result["data"]))


# ---------------------------------------------------------------------------
# Haupt-Dispatch: read_resource
# ---------------------------------------------------------------------------

async def handle_read_resource(uri: AnyUrl) -> list[TextResourceContents]:
    """
    Dispatcht read_resource-Aufrufe anhand der knews://-URI.

    Unterstützte Muster:
      knews://feeds                      → alle News-Feeds
      knews://energie/filters            → alle SMARD-Filter
      knews://company/{id}               → Handelsregister-Unternehmen
      knews://bundesanzeiger/report/{id} → Jahresabschluss
      knews://bundestag/drucksache/{id}  → Drucksache
      knews://energie/filter/{id}        → SMARD-Zeitreihe
      knews://foerderung/programm/{id}   → Förderprogramm
    """
    uri_str = str(uri)

    # Statische Resources
    if uri_str == "knews://feeds":
        return await _handle_feeds(uri)
    if uri_str == "knews://energie/filters":
        return await _handle_energie_filters(uri)

    # Dynamische Resources — Muster matchen
    path, resource_id = _parse_uri(uri_str)

    if path == "company":
        return await _handle_company(uri, resource_id)
    if path == "bundesanzeiger/report":
        return await _handle_bundesanzeiger_report(uri, resource_id)
    if path == "bundestag/drucksache":
        return await _handle_bundestag_drucksache(uri, resource_id)
    if path == "energie/filter":
        return await _handle_energie_filter(uri, resource_id)
    if path == "foerderung/programm":
        return await _handle_foerderung_programm(uri, resource_id)

    # Unbekannte URI
    return _text_resource(
        uri,
        f"❌ Unbekannte Resource URI: {uri_str}\n\n"
        "Unterstützte URIs:\n"
        "  knews://feeds\n"
        "  knews://energie/filters\n"
        "  knews://company/{id}\n"
        "  knews://bundesanzeiger/report/{id}\n"
        "  knews://bundestag/drucksache/{id}\n"
        "  knews://energie/filter/{id}\n"
        "  knews://foerderung/programm/{id}\n",
    )


# ---------------------------------------------------------------------------
# Registrierung am MCP-Server
# ---------------------------------------------------------------------------

def register_resources(server: Server) -> None:
    """
    Registriert alle Resource-Handler am übergebenen MCP-Server.
    Wird einmalig aus server.py aufgerufen.
    """

    @server.list_resources()
    async def list_resources() -> list[Resource]:
        """Gibt alle statischen knews Resources zurück."""
        return STATIC_RESOURCES

    @server.list_resource_templates()
    async def list_resource_templates() -> list[ResourceTemplate]:
        """Gibt alle dynamischen knews Resource Templates zurück."""
        return RESOURCE_TEMPLATES

    @server.read_resource()
    async def read_resource(uri: AnyUrl) -> list[TextResourceContents]:
        """Liest den Inhalt einer knews Resource anhand ihrer URI."""
        return await handle_read_resource(uri)
