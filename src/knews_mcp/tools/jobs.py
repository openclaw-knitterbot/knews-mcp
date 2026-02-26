"""
MCP Tools für Stellenangebote (SAP und VW Karriereseiten).

Scope required: jobs:read
"""

from mcp.types import TextContent, Tool

from ..client import api_get
from ..formatting import format_error, format_jobs

JOBS_TOOLS = [
    Tool(
        name="jobs_list",
        description=(
            "Listet Stellenangebote von SAP und/oder Volkswagen. "
            "Filtert nach Quelle, Suchbegriff (Bereich/Level) und Land. "
            "Nützlich für: Jobsuche bei SAP oder VW, Karrieremöglichkeiten erkunden.\n\n"
            "List job postings from SAP and/or Volkswagen. "
            "Filter by source, keyword (work area / career level), and country."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "source": {
                    "type": "string",
                    "description": "Datenquelle: 'sap' (SAP), 'vw' (Volkswagen) oder 'all' (beide)",
                    "enum": ["sap", "vw", "all"],
                    "default": "all",
                },
                "q": {
                    "type": "string",
                    "description": "Suche in Arbeitsbereich und Karrierestufe (z.B. 'Engineering', 'Marketing')",
                },
                "country": {
                    "type": "string",
                    "description": "Ländercode (z.B. 'DE', 'US', 'CN')",
                },
                "date_from": {
                    "type": "string",
                    "description": "Nur Jobs ab diesem Datum (YYYY-MM-DD)",
                },
                "date_to": {
                    "type": "string",
                    "description": "Nur Jobs bis zu diesem Datum (YYYY-MM-DD)",
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
]


async def handle_jobs(name: str, arguments: dict) -> list[TextContent]:
    if name == "jobs_list":
        page = arguments.get("page", 0)
        size = arguments.get("size", 20)
        result = await api_get(
            "/v1/jobs",
            params={
                "source": arguments.get("source", "all"),
                "q": arguments.get("q"),
                "country": arguments.get("country"),
                "date_from": arguments.get("date_from"),
                "date_to": arguments.get("date_to"),
                "page": page,
                "size": size,
            },
        )
        if not result["ok"]:
            return [TextContent(type="text", text=format_error(result["error"]))]
        return [TextContent(type="text", text=format_jobs(result["data"], page))]

    return [TextContent(type="text", text=format_error(f"Unbekanntes Tool: {name}"))]
