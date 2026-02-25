"""
MCP Tools für Förderprogramme (BMWK-Förderdatenbank).

Scope required: foerderung:read
"""

from mcp.types import TextContent, Tool

from ..client import api_get
from ..formatting import format_error, format_foerderung_programm, format_foerderung_programme

FOERDERUNG_TOOLS = [
    Tool(
        name="foerderung_list_programme",
        description=(
            "Listet staatliche Förderprogramme aus der BMWK-Förderdatenbank. "
            "Filtert nach Suchbegriff, Förderbereich, Fördergeber (Bund/EU/Länder) und Förderberechtigten. "
            "Nützlich für: Fördermittelrecherche, KMU-Förderung, Innovations- und Investitionsförderung.\n\n"
            "List German government funding programs (BMWK database). "
            "Filter by keyword, funding area, grantor (federal/EU/state) and eligible recipients."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "q": {
                    "type": "string",
                    "description": "Suche in Titel und Kurztext",
                },
                "foerderbereich": {
                    "type": "string",
                    "description": "Förderbereich (Teilsuche, z.B. 'Innovation', 'Digitalisierung', 'Energie', 'Gründung')",
                },
                "foerdergeber": {
                    "type": "string",
                    "description": "Fördergeber (Teilsuche, z.B. 'Bund', 'EU', 'Bayern', 'NRW')",
                },
                "foerderberechtigte": {
                    "type": "string",
                    "description": "Förderberechtigte (z.B. 'KMU', 'Großunternehmen', 'Privatpersonen', 'Kommunen')",
                },
                "is_active": {
                    "type": "boolean",
                    "description": "Nur aktive Programme (Standard: true)",
                    "default": True,
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
        name="foerderung_get_programm",
        description=(
            "Ruft Detailinfos zu einem Förderprogramm ab, inkl. Volltext (Beschreibung, Konditionen). "
            "Benötigt die numerische ID aus foerderung_list_programme.\n\n"
            "Fetch full details of a funding program by ID, including description and conditions."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "program_id": {
                    "type": "integer",
                    "description": "Numerische ID des Förderprogramms (aus foerderung_list_programme)",
                },
            },
            "required": ["program_id"],
        },
    ),
]


async def handle_foerderung(name: str, arguments: dict) -> list[TextContent]:
    if name == "foerderung_list_programme":
        page = arguments.get("page", 0)
        size = arguments.get("size", 20)
        result = await api_get(
            "/v1/foerderung/programme",
            params={
                "q": arguments.get("q"),
                "foerderbereich": arguments.get("foerderbereich"),
                "foerdergeber": arguments.get("foerdergeber"),
                "foerderberechtigte": arguments.get("foerderberechtigte"),
                "is_active": arguments.get("is_active", True),
                "page": page,
                "size": size,
            },
        )
        if not result["ok"]:
            return [TextContent(type="text", text=format_error(result["error"]))]
        return [TextContent(type="text", text=format_foerderung_programme(result["data"], page, size))]

    elif name == "foerderung_get_programm":
        program_id = arguments["program_id"]
        result = await api_get(f"/v1/foerderung/programm/{program_id}")
        if not result["ok"]:
            return [TextContent(type="text", text=format_error(result["error"]))]
        return [TextContent(type="text", text=format_foerderung_programm(result["data"]))]

    return [TextContent(type="text", text=format_error(f"Unbekanntes Tool: {name}"))]
