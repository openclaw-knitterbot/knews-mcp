"""
MCP Tools für öffentliche Vergabe (Ausschreibungen, Auftraggeber).

Scope required: vergabe:read
"""

from mcp.types import TextContent, Tool

from ..client import api_get
from ..formatting import (
    format_error,
    format_vergabe_auftraggeber,
    format_vergabe_ausschreibungen,
    format_vergabe_stats,
)

VERGABE_TOOLS = [
    Tool(
        name="vergabe_ausschreibungen",
        description=(
            "Listet öffentliche Ausschreibungen (DTVP-Vergabeplattform). "
            "Filtert nach Vergaberecht, Bekanntmachungstyp, Auftraggeber, Titel und Zeitraum. "
            "Nützlich für: Auftragsrecherche, Ausschreibungsmonitoring, öffentliche Beschaffung.\n\n"
            "List public procurement announcements (DTVP platform). "
            "Filter by contracting rules, type, contracting authority, title, date range."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "q": {
                    "type": "string",
                    "description": "Suche im Ausschreibungstitel",
                },
                "rule": {
                    "type": "string",
                    "description": "Vergaberecht (z.B. 'VgV', 'VOB/A', 'UVgO', 'SektVO', 'VSVgV')",
                },
                "typ": {
                    "type": "string",
                    "description": "Bekanntmachungstyp (z.B. 'Tender', 'Ausschreibung', 'ExPost', 'ExAnte')",
                },
                "org": {
                    "type": "string",
                    "description": "Auftraggeber (Teilsuche, z.B. 'Stadt München', 'Bundeswehr')",
                },
                "date_from": {
                    "type": "string",
                    "description": "Veröffentlicht ab (YYYY-MM-DD)",
                    "pattern": "^\\d{4}-\\d{2}-\\d{2}$",
                },
                "date_to": {
                    "type": "string",
                    "description": "Veröffentlicht bis (YYYY-MM-DD)",
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
        name="vergabe_auftraggeber",
        description=(
            "Top-Auftraggeber im deutschen Vergaberecht nach Anzahl aktiver Ausschreibungen. "
            "Nützlich für: Wer schreibt am meisten aus? Welche Behörden sind aktiv?\n\n"
            "Top contracting authorities by number of active procurement announcements."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "limit": {
                    "type": "integer",
                    "description": "Anzahl Ergebnisse (Standard: 50, max: 200)",
                    "default": 50,
                    "minimum": 1,
                    "maximum": 200,
                },
            },
        },
    ),
    Tool(
        name="vergabe_stats",
        description=(
            "KPI-Übersicht zur öffentlichen Vergabe: "
            "Gesamt- und Aktivzahlen, durchschnittliche Fristlänge, Verteilung nach Typ und Vergaberecht.\n\n"
            "KPI overview for public procurement: totals, active count, avg deadline, breakdown by type and rules."
        ),
        inputSchema={
            "type": "object",
            "properties": {},
        },
    ),
]


async def handle_vergabe(name: str, arguments: dict) -> list[TextContent]:
    if name == "vergabe_ausschreibungen":
        page = arguments.get("page", 0)
        size = arguments.get("size", 20)
        result = await api_get(
            "/v1/vergabe/ausschreibungen",
            params={
                "q": arguments.get("q"),
                "rule": arguments.get("rule"),
                "typ": arguments.get("typ"),
                "org": arguments.get("org"),
                "date_from": arguments.get("date_from"),
                "date_to": arguments.get("date_to"),
                "page": page,
                "size": size,
            },
        )
        if not result["ok"]:
            return [TextContent(type="text", text=format_error(result["error"]))]
        return [TextContent(type="text", text=format_vergabe_ausschreibungen(result["data"], page, size))]

    elif name == "vergabe_auftraggeber":
        result = await api_get(
            "/v1/vergabe/auftraggeber",
            params={"limit": arguments.get("limit", 50)},
        )
        if not result["ok"]:
            return [TextContent(type="text", text=format_error(result["error"]))]
        return [TextContent(type="text", text=format_vergabe_auftraggeber(result["data"]))]

    elif name == "vergabe_stats":
        result = await api_get("/v1/vergabe/stats")
        if not result["ok"]:
            return [TextContent(type="text", text=format_error(result["error"]))]
        return [TextContent(type="text", text=format_vergabe_stats(result["data"]))]

    return [TextContent(type="text", text=format_error(f"Unbekanntes Tool: {name}"))]
