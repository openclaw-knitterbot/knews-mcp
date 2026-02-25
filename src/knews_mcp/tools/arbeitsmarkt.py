"""
MCP Tools für den deutschen Arbeitsmarkt (BA-Jobbörse).

Scope required: arbeitsmarkt:read
"""

from mcp.types import TextContent, Tool

from ..client import api_get
from ..formatting import (
    format_arbeitsmarkt_facets,
    format_arbeitsmarkt_jobs,
    format_arbeitsmarkt_stats,
    format_error,
)

ARBEITSMARKT_TOOLS = [
    Tool(
        name="arbeitsmarkt_jobs",
        description=(
            "Durchsucht Stellenangebote der Bundesagentur für Arbeit (BA-Jobbörse). "
            "Filtert nach Beruf, Arbeitgeber, Branche, Region und PLZ. "
            "Nützlich für: Jobsuche in Deutschland, regionale Arbeitsmarktanalyse.\n\n"
            "Search job offers from the German Federal Employment Agency (BA-Jobbörse). "
            "Filter by job title, employer, industry, region, postal code."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "q": {
                    "type": "string",
                    "description": "Suche in Berufsbezeichnung und Titel (z.B. 'Softwareentwickler', 'Pfleger')",
                },
                "arbeitgeber": {
                    "type": "string",
                    "description": "Arbeitgeber (Teilsuche, z.B. 'Bosch', 'Siemens')",
                },
                "branche": {
                    "type": "string",
                    "description": "Branche (Teilsuche, z.B. 'IT', 'Gesundheit', 'Handel')",
                },
                "region": {
                    "type": "string",
                    "description": "Region oder Bundesland (Teilsuche, z.B. 'Bayern', 'Berlin')",
                },
                "plz": {
                    "type": "string",
                    "description": "Postleitzahl-Präfix (z.B. '80' für München, '10' für Berlin)",
                },
                "removed": {
                    "type": "boolean",
                    "description": "Auch bereits abgelaufene Stellen einbeziehen (Standard: false)",
                    "default": False,
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
        name="arbeitsmarkt_stats",
        description=(
            "Tägliche Statistiken des deutschen Arbeitsmarkts: "
            "Gesamtanzahl Stellenangebote, Neu- und Abmeldungen im Zeitverlauf (bis 365 Tage). "
            "Nützlich für: Arbeitsmarkt-Trendanalyse, wirtschaftliche Lageeinschätzung.\n\n"
            "Daily German labor market statistics: total job count, new/removed jobs over time."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "days": {
                    "type": "integer",
                    "description": "Anzahl Tage (Standard: 90, max: 365)",
                    "default": 90,
                    "minimum": 1,
                    "maximum": 365,
                },
            },
        },
    ),
    Tool(
        name="arbeitsmarkt_facets",
        description=(
            "Facetten-Auswertung des deutschen Arbeitsmarkts: "
            "Top-Branchen, Berufsfelder und Regionen nach Anzahl Stellenangebote. "
            "Nützlich für: Branchen-Analyse, regionale Arbeitsmarktschwerpunkte.\n\n"
            "Facet analysis of the German labor market: top industries, job fields, regions."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "facet_type": {
                    "type": "string",
                    "description": "Facettentyp filtern (z.B. 'branche', 'berufsfeld', 'region')",
                },
                "date": {
                    "type": "string",
                    "description": "Snapshot-Datum (YYYY-MM-DD), Standard: letzter verfügbarer Tag",
                    "pattern": "^\\d{4}-\\d{2}-\\d{2}$",
                },
                "limit": {
                    "type": "integer",
                    "description": "Anzahl Ergebnisse pro Facette (Standard: 50, max: 200)",
                    "default": 50,
                    "minimum": 1,
                    "maximum": 200,
                },
            },
        },
    ),
]


async def handle_arbeitsmarkt(name: str, arguments: dict) -> list[TextContent]:
    if name == "arbeitsmarkt_jobs":
        page = arguments.get("page", 0)
        size = arguments.get("size", 20)
        result = await api_get(
            "/v1/arbeitsmarkt/jobs",
            params={
                "q": arguments.get("q"),
                "arbeitgeber": arguments.get("arbeitgeber"),
                "branche": arguments.get("branche"),
                "region": arguments.get("region"),
                "plz": arguments.get("plz"),
                "removed": arguments.get("removed", False),
                "page": page,
                "size": size,
            },
        )
        if not result["ok"]:
            return [TextContent(type="text", text=format_error(result["error"]))]
        return [TextContent(type="text", text=format_arbeitsmarkt_jobs(result["data"], page, size))]

    elif name == "arbeitsmarkt_stats":
        result = await api_get(
            "/v1/arbeitsmarkt/stats",
            params={"days": arguments.get("days", 90)},
        )
        if not result["ok"]:
            return [TextContent(type="text", text=format_error(result["error"]))]
        return [TextContent(type="text", text=format_arbeitsmarkt_stats(result["data"]))]

    elif name == "arbeitsmarkt_facets":
        result = await api_get(
            "/v1/arbeitsmarkt/facets",
            params={
                "facet_type": arguments.get("facet_type"),
                "date": arguments.get("date"),
                "limit": arguments.get("limit", 50),
            },
        )
        if not result["ok"]:
            return [TextContent(type="text", text=format_error(result["error"]))]
        return [TextContent(type="text", text=format_arbeitsmarkt_facets(result["data"]))]

    return [TextContent(type="text", text=format_error(f"Unbekanntes Tool: {name}"))]
