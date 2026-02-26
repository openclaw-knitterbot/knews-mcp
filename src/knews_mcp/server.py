"""
knews MCP Server

Stellt alle knews-Datenplattform-Tools als MCP Server bereit:
- Bundesanzeiger (Jahresabschlüsse, Bilanzen)
- Handelsregister (Unternehmen, Personen)
- News (2,8 Mio. Artikel, 60+ Feeds)
- Bundestag (Drucksachen, Vorgänge, LLM-Klassifikation)
- Jobs (SAP, VW Stellenangebote)
- Arbeitsmarkt (BA-Jobbörse, Statistiken)
- Energie (SMARD Strommarkt, MaStR Anlagenregister)
- Förderung (BMWK-Förderdatenbank)
- Vergabe (öffentliche Ausschreibungen)
- Luftqualität (UBA-Messstationen)

Konfiguration:
  KNEWS_API_KEY  Umgebungsvariable mit dem API Key (https://knews.press/portal)
"""

import asyncio
import logging
import os

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool

from .tools import ALL_TOOLS, TOOL_HANDLERS
from .resources import register_resources
from .prompts import register_prompts

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger("knews-mcp")

server = Server("knews-mcp")

# Resources und Prompts registrieren
register_resources(server)
register_prompts(server)


@server.list_tools()
async def list_tools() -> list[Tool]:
    """Gibt alle verfügbaren knews MCP Tools zurück."""
    return ALL_TOOLS


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """
    Dispatcht Tool-Aufrufe an die zuständigen Handler.
    Gibt bei unbekannten Tools eine hilfreiche Fehlermeldung zurück.
    """
    handler = TOOL_HANDLERS.get(name)
    if handler is None:
        available = ", ".join(t.name for t in ALL_TOOLS)
        return [
            TextContent(
                type="text",
                text=f"❌ Unbekanntes Tool: '{name}'\n\nVerfügbare Tools:\n{available}",
            )
        ]

    try:
        return await handler(name, arguments)
    except Exception as exc:
        logger.exception("Fehler beim Ausführen von Tool '%s': %s", name, exc)
        return [
            TextContent(
                type="text",
                text=f"❌ Interner Fehler beim Ausführen von '{name}': {type(exc).__name__}: {exc}",
            )
        ]


def main() -> None:
    """Einstiegspunkt für den knews MCP Server (stdio-Modus)."""
    api_key = os.environ.get("KNEWS_API_KEY")
    if not api_key:
        logger.warning(
            "WARNUNG: KNEWS_API_KEY nicht gesetzt. "
            "Alle API-Aufrufe werden mit einem Konfigurationsfehler beantwortet. "
            "Einen API Key erhältst du unter https://knews.press/portal"
        )

    from .resources import STATIC_RESOURCES, RESOURCE_TEMPLATES
    from .prompts import ALL_PROMPTS
    logger.info(
        "knews MCP Server startet (%d Tools, %d Resources, %d Resource Templates, %d Prompts)…",
        len(ALL_TOOLS),
        len(STATIC_RESOURCES),
        len(RESOURCE_TEMPLATES),
        len(ALL_PROMPTS),
    )

    async def _run() -> None:
        async with stdio_server() as (read_stream, write_stream):
            await server.run(
                read_stream,
                write_stream,
                server.create_initialization_options(),
            )

    asyncio.run(_run())


if __name__ == "__main__":
    main()
