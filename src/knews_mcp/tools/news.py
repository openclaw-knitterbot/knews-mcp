"""
MCP Tools für News (2,8 Mio. Artikel, 60+ Feeds).

Scope required: news:read
"""

from mcp.types import TextContent, Tool

from ..client import api_get
from ..formatting import format_error, format_news_articles, format_news_feeds

NEWS_TOOLS = [
    Tool(
        name="news_list_feeds",
        description=(
            "Listet alle verfügbaren News-Feeds im knews-System (60+ Quellen). "
            "Gibt Name, URL und Sprache jedes Feeds zurück. "
            "Nützlich als Vorbereitung für news_search_articles, um Feed-Namen zu ermitteln.\n\n"
            "List all available news feeds (60+ sources). Returns name, URL and language of each feed."
        ),
        inputSchema={
            "type": "object",
            "properties": {},
        },
    ),
    Tool(
        name="news_search_articles",
        description=(
            "Durchsucht den knews-Newsartikel-Pool (2,8 Mio. Artikel). "
            "Filtert nach Suchbegriff (Titel/Teaser), Feed, Zeitraum. "
            "Nützlich für: Nachrichtenrecherche, Medienmonitoring, aktuelle Berichte zu einem Thema.\n\n"
            "Search 2.8M news articles by keyword, feed, or date range."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "q": {
                    "type": "string",
                    "description": "Suchbegriff (sucht in Titel und Teaser)",
                },
                "feed": {
                    "type": "string",
                    "description": "Feed-Name (exakter Treffer, z.B. 'Spiegel Online', 'FAZ'). Nutze news_list_feeds für verfügbare Namen.",
                },
                "from": {
                    "type": "string",
                    "description": "Artikel ab diesem Datum (YYYY-MM-DD)",
                    "pattern": "^\\d{4}-\\d{2}-\\d{2}$",
                },
                "to": {
                    "type": "string",
                    "description": "Artikel bis zu diesem Datum (YYYY-MM-DD)",
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
]


async def handle_news(name: str, arguments: dict) -> list[TextContent]:
    if name == "news_list_feeds":
        result = await api_get("/v1/news/feeds")
        if not result["ok"]:
            return [TextContent(type="text", text=format_error(result["error"]))]
        return [TextContent(type="text", text=format_news_feeds(result["data"]))]

    elif name == "news_search_articles":
        page = arguments.get("page", 0)
        size = arguments.get("size", 20)
        result = await api_get(
            "/v1/news/articles",
            params={
                "q": arguments.get("q"),
                "feed": arguments.get("feed"),
                "from": arguments.get("from"),
                "to": arguments.get("to"),
                "page": page,
                "size": size,
            },
        )
        if not result["ok"]:
            return [TextContent(type="text", text=format_error(result["error"]))]
        return [TextContent(type="text", text=format_news_articles(result["data"], page, size))]

    return [TextContent(type="text", text=format_error(f"Unbekanntes Tool: {name}"))]
