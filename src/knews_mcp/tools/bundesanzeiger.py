"""
MCP Tools für den Bundesanzeiger (Jahresabschlüsse / Geschäftsberichte).

Scope required: bundesanzeiger:read
"""

from mcp.types import TextContent, Tool

from ..client import api_get
from ..formatting import (
    format_bundesanzeiger_report,
    format_bundesanzeiger_reports,
    format_bundesanzeiger_search,
    format_error,
)

BUNDESANZEIGER_TOOLS = [
    Tool(
        name="bundesanzeiger_search",
        description=(
            "Durchsucht den Bundesanzeiger per Volltextsuche (Elasticsearch). "
            "Findet Jahresabschlüsse und Veröffentlichungen anhand von Freitext. "
            "Nützlich für: Unternehmensrecherche, Jahresabschlüsse, Bilanzen.\n\n"
            "Search the Bundesanzeiger (German Federal Gazette) full-text via Elasticsearch. "
            "Finds annual reports and publications by free-text query."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "q": {
                    "type": "string",
                    "description": "Suchbegriff (Volltextsuche im Jahresabschluss-Text)",
                },
                "page": {
                    "type": "integer",
                    "description": "Seite (0-basiert, Standard: 0)",
                    "default": 0,
                    "minimum": 0,
                },
                "size": {
                    "type": "integer",
                    "description": "Ergebnisse pro Seite (Standard: 10, max: 100)",
                    "default": 10,
                    "minimum": 1,
                    "maximum": 100,
                },
            },
            "required": ["q"],
        },
    ),
    Tool(
        name="bundesanzeiger_list_reports",
        description=(
            "Listet geparste Bundesanzeiger-Berichte aus der MySQL-Datenbank. "
            "Filterbar nach Unternehmen, Geschäftsjahr und Rechtsform. "
            "Nützlich für: Liste aller Jahresabschlüsse eines Unternehmens, Vergleiche nach Rechtsform.\n\n"
            "List parsed Bundesanzeiger reports from MySQL. Filterable by company, fiscal year, legal form."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "company": {
                    "type": "string",
                    "description": "Unternehmensname (Teilsuche, z.B. 'Siemens')",
                },
                "year": {
                    "type": "integer",
                    "description": "Geschäftsjahr-Ende (z.B. 2023)",
                },
                "legal_form": {
                    "type": "string",
                    "description": "Rechtsform (z.B. 'GmbH', 'AG', 'KG')",
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
        name="bundesanzeiger_get_report",
        description=(
            "Ruft einen einzelnen Bundesanzeiger-Bericht ab, inkl. Bilanz- und GuV-Daten. "
            "Benötigt die report_id aus bundesanzeiger_search oder bundesanzeiger_list_reports.\n\n"
            "Fetch a single Bundesanzeiger report by ID, including balance sheet (Bilanz) and P&L (GuV)."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "report_id": {
                    "type": "string",
                    "description": "Report-ID (aus bundesanzeiger_search oder bundesanzeiger_list_reports)",
                },
            },
            "required": ["report_id"],
        },
    ),
]


async def handle_bundesanzeiger(name: str, arguments: dict) -> list[TextContent]:
    if name == "bundesanzeiger_search":
        result = await api_get(
            "/v1/bundesanzeiger/search",
            params={
                "q": arguments["q"],
                "page": arguments.get("page", 0),
                "size": arguments.get("size", 10),
            },
        )
        if not result["ok"]:
            return [TextContent(type="text", text=format_error(result["error"]))]
        return [TextContent(type="text", text=format_bundesanzeiger_search(result["data"]))]

    elif name == "bundesanzeiger_list_reports":
        page = arguments.get("page", 0)
        size = arguments.get("size", 20)
        result = await api_get(
            "/v1/bundesanzeiger/reports",
            params={
                "company": arguments.get("company"),
                "year": arguments.get("year"),
                "legal_form": arguments.get("legal_form"),
                "page": page,
                "size": size,
            },
        )
        if not result["ok"]:
            return [TextContent(type="text", text=format_error(result["error"]))]
        return [TextContent(type="text", text=format_bundesanzeiger_reports(result["data"], page, size))]

    elif name == "bundesanzeiger_get_report":
        report_id = arguments["report_id"]
        result = await api_get(f"/v1/bundesanzeiger/report/{report_id}")
        if not result["ok"]:
            return [TextContent(type="text", text=format_error(result["error"]))]
        return [TextContent(type="text", text=format_bundesanzeiger_report(result["data"]))]

    return [TextContent(type="text", text=format_error(f"Unbekanntes Tool: {name}"))]
