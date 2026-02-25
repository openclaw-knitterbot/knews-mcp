"""
MCP Tools für das Handelsregister (Unternehmen, Gesellschafter, Geschäftsführer).

Scope required: handelsregister:read
"""

from mcp.types import TextContent, Tool

from ..client import api_get
from ..formatting import (
    format_error,
    format_handelsregister_companies,
    format_handelsregister_company,
    format_handelsregister_officers,
    format_handelsregister_stats,
)

HANDELSREGISTER_TOOLS = [
    Tool(
        name="handelsregister_search_companies",
        description=(
            "Sucht Unternehmen im deutschen Handelsregister. "
            "Filtert nach Name (Volltext), Registerart (HRB/HRA), Bundesland, Registergericht und Status. "
            "Nützlich für: Unternehmensrecherche, Firmenstatus prüfen, Registerauszüge.\n\n"
            "Search German commercial register (Handelsregister) companies by name, register type, state, etc."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "q": {
                    "type": "string",
                    "description": "Unternehmensname (Volltext-Boolean-Suche, z.B. 'Volkswagen')",
                },
                "register_type": {
                    "type": "string",
                    "description": "Registerart: HRB (GmbH/AG), HRA (Personengesellschaft), VR (Verein), GnR, PR",
                    "enum": ["HRB", "HRA", "VR", "GnR", "PR"],
                },
                "federal_state": {
                    "type": "string",
                    "description": "Bundesland (z.B. 'Bayern', 'NRW', 'Berlin')",
                },
                "registrar": {
                    "type": "string",
                    "description": "Registergericht (Teilsuche, z.B. 'Amtsgericht München')",
                },
                "status": {
                    "type": "string",
                    "description": "Status des Unternehmens",
                    "enum": ["currently registered", "removed"],
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
        name="handelsregister_get_company",
        description=(
            "Ruft Detailinformationen zu einem Handelsregister-Unternehmen ab, "
            "inkl. aller eingetragenen Personen (Geschäftsführer, Prokuristen, etc.). "
            "Benötigt die company_number aus handelsregister_search_companies.\n\n"
            "Fetch company details and all officers (directors, proxies, etc.) by company_number."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "company_number": {
                    "type": "string",
                    "description": "Company-Nummer aus handelsregister_search_companies (z.B. 'K1010R_HRB12345')",
                },
            },
            "required": ["company_number"],
        },
    ),
    Tool(
        name="handelsregister_search_officers",
        description=(
            "Sucht Personen im Handelsregister (Geschäftsführer, Prokuristen, Vorstände). "
            "Findet alle Ämter einer Person und die zugehörigen Unternehmen. "
            "Nützlich für: Personenrecherche, Verflechtungsanalyse, Amtsinhaber prüfen.\n\n"
            "Search officers/directors in the German commercial register. Find all company roles for a person."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "q": {
                    "type": "string",
                    "description": "Name der Person (Volltext-Boolean-Suche, z.B. 'Müller')",
                },
                "position": {
                    "type": "string",
                    "description": "Position (Teilsuche, z.B. 'Geschäftsführer', 'Vorstand', 'Prokurist')",
                },
                "city": {
                    "type": "string",
                    "description": "Wohnort (Teilsuche)",
                },
                "dismissed": {
                    "type": "boolean",
                    "description": "Nur abberufene/ausgeschiedene Personen (true) oder nur aktive (false)",
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
        name="handelsregister_stats",
        description=(
            "Gibt Übersichtsstatistiken zum Handelsregister-Datensatz zurück: "
            "Anzahl Unternehmen, Verteilung nach Registerart und Bundesland.\n\n"
            "Returns overview statistics for the Handelsregister dataset."
        ),
        inputSchema={
            "type": "object",
            "properties": {},
        },
    ),
]


async def handle_handelsregister(name: str, arguments: dict) -> list[TextContent]:
    if name == "handelsregister_search_companies":
        page = arguments.get("page", 0)
        size = arguments.get("size", 20)
        result = await api_get(
            "/v1/handelsregister/companies",
            params={
                "q": arguments.get("q"),
                "register_type": arguments.get("register_type"),
                "federal_state": arguments.get("federal_state"),
                "registrar": arguments.get("registrar"),
                "status": arguments.get("status"),
                "page": page,
                "size": size,
            },
        )
        if not result["ok"]:
            return [TextContent(type="text", text=format_error(result["error"]))]
        return [TextContent(type="text", text=format_handelsregister_companies(result["data"], page, size))]

    elif name == "handelsregister_get_company":
        company_number = arguments["company_number"]
        result = await api_get(f"/v1/handelsregister/companies/{company_number}")
        if not result["ok"]:
            return [TextContent(type="text", text=format_error(result["error"]))]
        return [TextContent(type="text", text=format_handelsregister_company(result["data"]))]

    elif name == "handelsregister_search_officers":
        page = arguments.get("page", 0)
        size = arguments.get("size", 20)
        result = await api_get(
            "/v1/handelsregister/officers",
            params={
                "q": arguments.get("q"),
                "position": arguments.get("position"),
                "city": arguments.get("city"),
                "dismissed": arguments.get("dismissed"),
                "page": page,
                "size": size,
            },
        )
        if not result["ok"]:
            return [TextContent(type="text", text=format_error(result["error"]))]
        return [TextContent(type="text", text=format_handelsregister_officers(result["data"], page, size))]

    elif name == "handelsregister_stats":
        result = await api_get("/v1/handelsregister/stats")
        if not result["ok"]:
            return [TextContent(type="text", text=format_error(result["error"]))]
        return [TextContent(type="text", text=format_handelsregister_stats(result["data"]))]

    return [TextContent(type="text", text=format_error(f"Unbekanntes Tool: {name}"))]
