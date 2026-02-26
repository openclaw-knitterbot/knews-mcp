"""
MCP Tools für EU-Ausschreibungen (TED — Tenders Electronic Daily).

Scope required: ted:read
"""

from mcp.types import TextContent, Tool

from ..client import api_get
from ..formatting import (
    format_error,
    format_ted_buyer,
    format_ted_notices,
    format_ted_stats,
)

TED_TOOLS = [
    Tool(
        name="ted_notices",
        description=(
            "Sucht EU-Ausschreibungen aus dem TED (Tenders Electronic Daily), "
            "dem offiziellen EU-Amtsblatt für öffentliche Aufträge. "
            "Filtert nach Auftraggeber, Auftragnehmer, Bekanntmachungstyp, CPV-Code, "
            "Vertragsart und Zeitraum. "
            "Nützlich für: EU-Vergaberecherche, Auftragsmonitoring, Lieferantenanalyse.\n\n"
            "Search EU procurement notices from TED (Tenders Electronic Daily). "
            "Filter by buyer, winner, notice type, CPV code, contract nature and date range."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "q": {
                    "type": "string",
                    "description": "Suche im Auftraggeber-Namen (buyer_name)",
                },
                "buyer": {
                    "type": "string",
                    "description": "Auftraggeber (Teilsuche, z.B. 'Stadt München', 'Bundeswehr')",
                },
                "winner": {
                    "type": "string",
                    "description": "Auftragnehmer/Gewinner (Teilsuche, z.B. 'Siemens', 'SAP')",
                },
                "notice_type": {
                    "type": "string",
                    "description": "Bekanntmachungstyp: CN (Contract Notice), CAN (Contract Award Notice), PIN (Prior Information Notice)",
                    "enum": ["CN", "CAN", "PIN"],
                },
                "cpv": {
                    "type": "string",
                    "description": "CPV-Hauptcode (begins-with), z.B. '72' für IT-Dienstleistungen, '45' für Bauarbeiten",
                },
                "contract_nature": {
                    "type": "string",
                    "description": "Vertragsart: services, supplies, works",
                    "enum": ["services", "supplies", "works"],
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
        name="ted_stats",
        description=(
            "KPI-Übersicht zur EU-Vergabe aus TED: "
            "Gesamtzahl, Verteilung nach Bekanntmachungstyp und Vertragsart, "
            "Top-CPV-Codes sowie Gesamtvolumen und Durchschnittswert in EUR.\n\n"
            "KPI overview for EU procurement: totals, breakdown by notice type and contract nature, "
            "top CPV codes, total and average contract value in EUR."
        ),
        inputSchema={
            "type": "object",
            "properties": {},
        },
    ),
    Tool(
        name="ted_buyer",
        description=(
            "Top-Auftraggeber in der EU (TED-Datenbank) nach Anzahl der Ausschreibungen. "
            "Zeigt auch das vergebene Gesamtvolumen in EUR. "
            "Nützlich für: Wer schreibt am meisten EU-weit aus? Welche Behörden/Länder sind aktiv?\n\n"
            "Top contracting authorities in the EU (TED) by number of notices, including total contract value in EUR."
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
]


async def handle_ted(name: str, arguments: dict) -> list[TextContent]:
    if name == "ted_notices":
        page = arguments.get("page", 0)
        size = arguments.get("size", 20)
        result = await api_get(
            "/v1/ted/notices",
            params={
                "q": arguments.get("q"),
                "buyer": arguments.get("buyer"),
                "winner": arguments.get("winner"),
                "notice_type": arguments.get("notice_type"),
                "cpv": arguments.get("cpv"),
                "contract_nature": arguments.get("contract_nature"),
                "date_from": arguments.get("date_from"),
                "date_to": arguments.get("date_to"),
                "page": page,
                "size": size,
            },
        )
        if not result["ok"]:
            return [TextContent(type="text", text=format_error(result["error"]))]
        return [TextContent(type="text", text=format_ted_notices(result["data"], page, size))]

    elif name == "ted_stats":
        result = await api_get("/v1/ted/stats")
        if not result["ok"]:
            return [TextContent(type="text", text=format_error(result["error"]))]
        return [TextContent(type="text", text=format_ted_stats(result["data"]))]

    elif name == "ted_buyer":
        result = await api_get(
            "/v1/ted/buyer",
            params={"limit": arguments.get("limit", 50)},
        )
        if not result["ok"]:
            return [TextContent(type="text", text=format_error(result["error"]))]
        return [TextContent(type="text", text=format_ted_buyer(result["data"]))]

    return [TextContent(type="text", text=format_error(f"Unbekanntes Tool: {name}"))]
