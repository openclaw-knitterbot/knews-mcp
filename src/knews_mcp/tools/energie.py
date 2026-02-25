"""
MCP Tools für Energie-Daten (SMARD Strommarkt, MaStR Anlagenregister).

Scope required: energie:read
"""

from mcp.types import TextContent, Tool

from ..client import api_get
from ..formatting import (
    format_energie_filters,
    format_energie_mastr_snapshot,
    format_energie_mastr_totals,
    format_energie_timeseries,
    format_error,
)

ENERGIE_TOOLS = [
    Tool(
        name="energie_get_filters",
        description=(
            "Listet verfügbare SMARD-Datenreihen für den deutschen Strommarkt. "
            "Gibt Filter-IDs für Stromerzeugung (Solar, Wind, Kohle...), Verbrauch und Preise zurück. "
            "Nutze die filter_id für energie_timeseries.\n\n"
            "List available SMARD data series for the German electricity market "
            "(production by source, consumption, prices). Use filter_id for energie_timeseries."
        ),
        inputSchema={
            "type": "object",
            "properties": {},
        },
    ),
    Tool(
        name="energie_timeseries",
        description=(
            "Ruft SMARD Zeitreihendaten für den deutschen Strommarkt ab: "
            "Erzeugung (Solar, Wind, Kohle, Gas...), Verbrauch, Preise. "
            "Filtert nach Datenreihe (filter_id), Zeitraum und Datenpunkt-Limit. "
            "Nützlich für: Energiewende-Analyse, Strompreis-Recherche, erneuerbare Energien.\n\n"
            "Fetch SMARD electricity timeseries data (generation, consumption, prices) for Germany."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "filter_id": {
                    "type": "integer",
                    "description": "SMARD Filter-ID (aus energie_get_filters, z.B. 1004066 für Solar)",
                },
                "date_from": {
                    "type": "string",
                    "description": "Von (YYYY-MM-DD)",
                    "pattern": "^\\d{4}-\\d{2}-\\d{2}$",
                },
                "date_to": {
                    "type": "string",
                    "description": "Bis (YYYY-MM-DD)",
                    "pattern": "^\\d{4}-\\d{2}-\\d{2}$",
                },
                "limit": {
                    "type": "integer",
                    "description": "Max. Datenpunkte (Standard: 100, max: 10.000)",
                    "default": 100,
                    "minimum": 1,
                    "maximum": 10000,
                },
            },
        },
    ),
    Tool(
        name="energie_mastr_snapshot",
        description=(
            "MaStR (Marktstammdatenregister) Snapshot: "
            "Anzahl und Kapazität aller registrierten Energieanlagen nach Energieträger und Bundesland. "
            "Nützlich für: Ausbau erneuerbarer Energien, regionale Energiestruktur.\n\n"
            "MaStR snapshot: count and capacity of registered energy installations by energy carrier and state."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "energietraeger": {
                    "type": "string",
                    "description": "Energieträger (Teilsuche, z.B. 'Solar', 'Wind', 'Biomasse', 'Speicher')",
                },
                "bundesland": {
                    "type": "string",
                    "description": "Bundesland (Teilsuche, z.B. 'Bayern', 'Brandenburg')",
                },
                "date": {
                    "type": "string",
                    "description": "Snapshot-Datum (YYYY-MM-DD), Standard: letzter verfügbarer",
                    "pattern": "^\\d{4}-\\d{2}-\\d{2}$",
                },
            },
        },
    ),
    Tool(
        name="energie_mastr_totals",
        description=(
            "MaStR Gesamtzahlen im Zeitverlauf: "
            "Gesamtanzahl registrierter Energieanlagen und Balkonkraftwerke über die Zeit. "
            "Nützlich für: Wachstumstrends im Energiesektor, Balkonkraftwerk-Boom.\n\n"
            "MaStR total counts over time: all registered energy installations and balcony PV systems."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "days": {
                    "type": "integer",
                    "description": "Anzahl Tage (Standard: 90, max: 730)",
                    "default": 90,
                    "minimum": 1,
                    "maximum": 730,
                },
            },
        },
    ),
]


async def handle_energie(name: str, arguments: dict) -> list[TextContent]:
    if name == "energie_get_filters":
        result = await api_get("/v1/energie/filter")
        if not result["ok"]:
            return [TextContent(type="text", text=format_error(result["error"]))]
        return [TextContent(type="text", text=format_energie_filters(result["data"]))]

    elif name == "energie_timeseries":
        result = await api_get(
            "/v1/energie/timeseries",
            params={
                "filter_id": arguments.get("filter_id"),
                "date_from": arguments.get("date_from"),
                "date_to": arguments.get("date_to"),
                "limit": arguments.get("limit", 100),
            },
        )
        if not result["ok"]:
            return [TextContent(type="text", text=format_error(result["error"]))]
        return [TextContent(type="text", text=format_energie_timeseries(result["data"]))]

    elif name == "energie_mastr_snapshot":
        result = await api_get(
            "/v1/energie/mastr/snapshot",
            params={
                "energietraeger": arguments.get("energietraeger"),
                "bundesland": arguments.get("bundesland"),
                "date": arguments.get("date"),
            },
        )
        if not result["ok"]:
            return [TextContent(type="text", text=format_error(result["error"]))]
        return [TextContent(type="text", text=format_energie_mastr_snapshot(result["data"]))]

    elif name == "energie_mastr_totals":
        result = await api_get(
            "/v1/energie/mastr/totals",
            params={"days": arguments.get("days", 90)},
        )
        if not result["ok"]:
            return [TextContent(type="text", text=format_error(result["error"]))]
        return [TextContent(type="text", text=format_energie_mastr_totals(result["data"]))]

    return [TextContent(type="text", text=format_error(f"Unbekanntes Tool: {name}"))]
