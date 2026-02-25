"""
MCP Tools für Luftqualitätsdaten (UBA-Messnetz).

Scope required: luftqualitaet:read
"""

from mcp.types import TextContent, Tool

from ..client import api_get
from ..formatting import (
    format_error,
    format_luftqualitaet_messungen,
    format_luftqualitaet_stationen,
    format_luftqualitaet_ueberschreitungen,
)

LUFTQUALITAET_TOOLS = [
    Tool(
        name="luftqualitaet_stationen",
        description=(
            "Listet Luftqualitäts-Messstationen des Umweltbundesamts (UBA). "
            "Filtert nach Stadt, Messnetz und Aktivitätsstatus. "
            "Stations-IDs werden für luftqualitaet_messungen benötigt.\n\n"
            "List air quality monitoring stations (German Environment Agency / UBA). "
            "Filter by city, network, active status. Station IDs needed for luftqualitaet_messungen."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "city": {
                    "type": "string",
                    "description": "Stadt (Teilsuche, z.B. 'Berlin', 'München', 'Hamburg')",
                },
                "network": {
                    "type": "string",
                    "description": "Netzname (Teilsuche, z.B. 'Bayern', 'NRW', 'UBA')",
                },
                "active_only": {
                    "type": "boolean",
                    "description": "Nur aktive Stationen (Standard: true)",
                    "default": True,
                },
            },
        },
    ),
    Tool(
        name="luftqualitaet_messungen",
        description=(
            "Ruft Schadstoffmesswerte von UBA-Stationen ab. "
            "Schadstoffe: PM10 (ID 1), NO2 (ID 2), O3 (ID 5), PM2.5, SO2, CO. "
            "Filtert nach Station, Schadstoff und Zeitraum. "
            "Nützlich für: Luftqualitätsanalyse, Umweltmonitoring.\n\n"
            "Fetch air pollutant measurements from UBA stations. "
            "Pollutants: PM10 (ID 1), NO2 (ID 2), O3 (ID 5), PM2.5, SO2, CO."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "station_id": {
                    "type": "integer",
                    "description": "Stations-ID (aus luftqualitaet_stationen)",
                },
                "component_id": {
                    "type": "integer",
                    "description": "Schadstoff-ID: 1=PM10, 2=NO2, 3=O3, 4=SO2, 5=CO, 9=PM2.5",
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
                "page": {
                    "type": "integer",
                    "description": "Seite (0-basiert)",
                    "default": 0,
                    "minimum": 0,
                },
                "size": {
                    "type": "integer",
                    "description": "Ergebnisse pro Seite (Standard: 100, max: 1000)",
                    "default": 100,
                    "minimum": 1,
                    "maximum": 1000,
                },
            },
        },
    ),
    Tool(
        name="luftqualitaet_ueberschreitungen",
        description=(
            "Grenzwertüberschreitungen nach Station, Jahr und Schadstoff. "
            "Zeigt monatliche Verteilung der Überschreitungen. "
            "Nützlich für: Umweltbelastungsanalyse, Jahresberichte Luftqualität.\n\n"
            "Air quality limit value exceedances by station, year and pollutant. "
            "Shows monthly distribution."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "year": {
                    "type": "integer",
                    "description": "Jahr (z.B. 2023)",
                },
                "station_id": {
                    "type": "integer",
                    "description": "Stations-ID (aus luftqualitaet_stationen)",
                },
                "component_id": {
                    "type": "integer",
                    "description": "Schadstoff-ID: 1=PM10, 2=NO2, 3=O3",
                },
                "min_count": {
                    "type": "integer",
                    "description": "Mindestanzahl Überschreitungen (Standard: 1)",
                    "default": 1,
                    "minimum": 0,
                },
            },
        },
    ),
]


async def handle_luftqualitaet(name: str, arguments: dict) -> list[TextContent]:
    if name == "luftqualitaet_stationen":
        result = await api_get(
            "/v1/luftqualitaet/stationen",
            params={
                "city": arguments.get("city"),
                "network": arguments.get("network"),
                "active_only": arguments.get("active_only", True),
            },
        )
        if not result["ok"]:
            return [TextContent(type="text", text=format_error(result["error"]))]
        return [TextContent(type="text", text=format_luftqualitaet_stationen(result["data"]))]

    elif name == "luftqualitaet_messungen":
        page = arguments.get("page", 0)
        size = arguments.get("size", 100)
        result = await api_get(
            "/v1/luftqualitaet/messungen",
            params={
                "station_id": arguments.get("station_id"),
                "component_id": arguments.get("component_id"),
                "date_from": arguments.get("date_from"),
                "date_to": arguments.get("date_to"),
                "page": page,
                "size": size,
            },
        )
        if not result["ok"]:
            return [TextContent(type="text", text=format_error(result["error"]))]
        return [TextContent(type="text", text=format_luftqualitaet_messungen(result["data"], page, size))]

    elif name == "luftqualitaet_ueberschreitungen":
        result = await api_get(
            "/v1/luftqualitaet/ueberschreitungen",
            params={
                "year": arguments.get("year"),
                "station_id": arguments.get("station_id"),
                "component_id": arguments.get("component_id"),
                "min_count": arguments.get("min_count", 1),
            },
        )
        if not result["ok"]:
            return [TextContent(type="text", text=format_error(result["error"]))]
        return [TextContent(type="text", text=format_luftqualitaet_ueberschreitungen(result["data"]))]

    return [TextContent(type="text", text=format_error(f"Unbekanntes Tool: {name}"))]
