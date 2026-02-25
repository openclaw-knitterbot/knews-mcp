"""
MCP Tools für den Deutschen Bundestag (Drucksachen, Vorgänge, Statistiken).

Scope required: bundestag:read
"""

from mcp.types import TextContent, Tool

from ..client import api_get
from ..formatting import (
    format_bundestag_drucksache,
    format_bundestag_drucksachen,
    format_bundestag_stats,
    format_bundestag_vorgaenge,
    format_error,
)

BUNDESTAG_TOOLS = [
    Tool(
        name="bundestag_list_drucksachen",
        description=(
            "Listet Bundestag-Drucksachen (Anträge, Gesetzentwürfe, Anfragen etc.), "
            "LLM-klassifiziert nach Themenfeldern. "
            "Filtert nach Wahlperiode, Typ, Thema, Volltext im Titel und Zeitraum. "
            "Nützlich für: Parlamentsrecherche, Gesetzgebungsmonitoring, politische Themenanalyse.\n\n"
            "List Bundestag printed papers (Drucksachen), LLM-classified by topic. "
            "Filter by electoral period, type, topic, title search, date range."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "q": {
                    "type": "string",
                    "description": "Suche im Titel der Drucksache",
                },
                "wp": {
                    "type": "integer",
                    "description": "Wahlperiode (z.B. 20 für aktuelle, 19 für vorherige)",
                },
                "typ": {
                    "type": "string",
                    "description": "Drucksachetyp (Teilsuche, z.B. 'Antrag', 'Gesetzentwurf', 'Anfrage', 'Beschlussempfehlung')",
                },
                "thema": {
                    "type": "string",
                    "description": "Themenfeld (LLM-Klassifikation, z.B. 'Wirtschaft', 'Gesundheit', 'Verkehr', 'Bildung')",
                },
                "date_from": {
                    "type": "string",
                    "description": "Datum von (YYYY-MM-DD)",
                    "pattern": "^\\d{4}-\\d{2}-\\d{2}$",
                },
                "date_to": {
                    "type": "string",
                    "description": "Datum bis (YYYY-MM-DD)",
                    "pattern": "^\\d{4}-\\d{2}-\\d{2}$",
                },
                "page": {
                    "type": "integer",
                    "description": "Seite (0-basiert)",
                    "default": 0,
                    "minimum": 0,
                },
                "size": {
                    "type": "integer",
                    "description": "Ergebnisse pro Seite (Standard: 20, max: 100)",
                    "default": 20,
                    "minimum": 1,
                    "maximum": 100,
                },
            },
        },
    ),
    Tool(
        name="bundestag_get_drucksache",
        description=(
            "Ruft eine einzelne Bundestag-Drucksache mit vollständigen Details ab, "
            "inkl. LLM-Klassifikation (Themen, Keywords). "
            "Benötigt die numerische ID aus bundestag_list_drucksachen.\n\n"
            "Fetch a single Bundestag Drucksache with full details and LLM classification."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "doc_id": {
                    "type": "integer",
                    "description": "Numerische ID der Drucksache (aus bundestag_list_drucksachen)",
                },
            },
            "required": ["doc_id"],
        },
    ),
    Tool(
        name="bundestag_list_vorgaenge",
        description=(
            "Listet Bundestag-Vorgänge (Gesetzgebungsverfahren, parlamentarische Vorgänge). "
            "Ein Vorgang fasst mehrere Drucksachen und Debatten zusammen. "
            "Filtert nach Wahlperiode, Vorgangstyp und Titel.\n\n"
            "List Bundestag proceedings (Vorgänge). A Vorgang bundles multiple Drucksachen. "
            "Filter by electoral period, type, title."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "q": {
                    "type": "string",
                    "description": "Suche im Titel des Vorgangs",
                },
                "wp": {
                    "type": "integer",
                    "description": "Wahlperiode (z.B. 20)",
                },
                "typ": {
                    "type": "string",
                    "description": "Vorgangstyp (Teilsuche, z.B. 'Gesetzgebung', 'Anfrage', 'Antrag')",
                },
                "page": {
                    "type": "integer",
                    "description": "Seite (0-basiert)",
                    "default": 0,
                    "minimum": 0,
                },
                "size": {
                    "type": "integer",
                    "description": "Ergebnisse pro Seite (Standard: 20, max: 100)",
                    "default": 20,
                    "minimum": 1,
                    "maximum": 100,
                },
            },
        },
    ),
    Tool(
        name="bundestag_stats",
        description=(
            "Zeigt Statistiken zu Bundestag-Drucksachen: "
            "Verteilung nach Drucksachetyp und nach LLM-klassifiziertem Themenfeld. "
            "Filtert optional nach Wahlperiode.\n\n"
            "Show Bundestag statistics: distribution by document type and LLM topic classification."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "wp": {
                    "type": "integer",
                    "description": "Wahlperiode (optional, z.B. 20)",
                },
            },
        },
    ),
]


async def handle_bundestag(name: str, arguments: dict) -> list[TextContent]:
    if name == "bundestag_list_drucksachen":
        page = arguments.get("page", 0)
        size = arguments.get("size", 20)
        result = await api_get(
            "/v1/bundestag/drucksachen",
            params={
                "q": arguments.get("q"),
                "wp": arguments.get("wp"),
                "typ": arguments.get("typ"),
                "thema": arguments.get("thema"),
                "date_from": arguments.get("date_from"),
                "date_to": arguments.get("date_to"),
                "page": page,
                "size": size,
            },
        )
        if not result["ok"]:
            return [TextContent(type="text", text=format_error(result["error"]))]
        return [TextContent(type="text", text=format_bundestag_drucksachen(result["data"], page, size))]

    elif name == "bundestag_get_drucksache":
        doc_id = arguments["doc_id"]
        result = await api_get(f"/v1/bundestag/drucksachen/{doc_id}")
        if not result["ok"]:
            return [TextContent(type="text", text=format_error(result["error"]))]
        return [TextContent(type="text", text=format_bundestag_drucksache(result["data"]))]

    elif name == "bundestag_list_vorgaenge":
        page = arguments.get("page", 0)
        size = arguments.get("size", 20)
        result = await api_get(
            "/v1/bundestag/vorgaenge",
            params={
                "q": arguments.get("q"),
                "wp": arguments.get("wp"),
                "typ": arguments.get("typ"),
                "page": page,
                "size": size,
            },
        )
        if not result["ok"]:
            return [TextContent(type="text", text=format_error(result["error"]))]
        return [TextContent(type="text", text=format_bundestag_vorgaenge(result["data"], page, size))]

    elif name == "bundestag_stats":
        result = await api_get(
            "/v1/bundestag/stats",
            params={"wp": arguments.get("wp")},
        )
        if not result["ok"]:
            return [TextContent(type="text", text=format_error(result["error"]))]
        return [TextContent(type="text", text=format_bundestag_stats(result["data"]))]

    return [TextContent(type="text", text=format_error(f"Unbekanntes Tool: {name}"))]
