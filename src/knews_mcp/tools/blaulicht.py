"""
MCP Tools für Blaulicht-Meldungen (Polizei, Feuerwehr, Rettungsdienst).

Scope required: blaulicht:read
"""

from mcp.types import TextContent, Tool

from ..client import api_get
from ..formatting import format_error

BLAULICHT_TOOLS = [
    Tool(
        name="blaulicht_suche",
        description=(
            "Volltextsuche in Blaulicht-Meldungen von Polizei, Feuerwehr und Rettungsdienst "
            "(Elasticsearch, ca. 15.000+ Meldungen). "
            "Filtert nach Bundesland, Kategorie und Zeitraum. "
            "Nützlich für: Ermittlung von Einsatzhäufigkeiten, investigative Recherche, "
            "Sicherheitslage in einer Region analysieren.\n\n"
            "Full-text search in German emergency services press releases (police, fire, rescue)."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "q": {
                    "type": "string",
                    "description": "Suchbegriff (z.B. 'Brand', 'Unfall', 'Einbruch', 'Vermisst')",
                },
                "bundesland": {
                    "type": "string",
                    "description": "Bundesland filtern (z.B. 'Bayern', 'Nordrhein-Westfalen', 'Berlin')",
                },
                "category": {
                    "type": "string",
                    "description": "Kategorie: 'polizei', 'feuerwehr', 'rettungsdienst'",
                    "enum": ["polizei", "feuerwehr", "rettungsdienst"],
                },
                "date_from": {
                    "type": "string",
                    "description": "Meldungen ab (YYYY-MM-DD)",
                    "pattern": "^\\d{4}-\\d{2}-\\d{2}$",
                },
                "date_to": {
                    "type": "string",
                    "description": "Meldungen bis (YYYY-MM-DD)",
                    "pattern": "^\\d{4}-\\d{2}-\\d{2}$",
                },
                "size": {
                    "type": "integer",
                    "description": "Anzahl Ergebnisse (Standard: 20, max: 100)",
                    "default": 20,
                    "minimum": 1,
                    "maximum": 100,
                },
            },
            "required": ["q"],
        },
    ),
    Tool(
        name="blaulicht_meldungen",
        description=(
            "Listet aktuelle Blaulicht-Meldungen (SQL, nach Datum sortiert). "
            "Filtert nach Bundesland, Kategorie und optionalem Suchbegriff. "
            "Nützlich für: Aktuelle Einsätze in einer Region, Lageübersicht, "
            "tägliches Monitoring der Sicherheitslage.\n\n"
            "List latest emergency services press releases, sorted by date (police, fire, rescue)."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "bundesland": {
                    "type": "string",
                    "description": "Bundesland (z.B. 'Bayern', 'Hamburg', 'Sachsen')",
                },
                "category": {
                    "type": "string",
                    "description": "Kategorie: 'polizei', 'feuerwehr', 'rettungsdienst'",
                    "enum": ["polizei", "feuerwehr", "rettungsdienst"],
                },
                "q": {
                    "type": "string",
                    "description": "Suchbegriff im Titel (optional)",
                },
                "limit": {
                    "type": "integer",
                    "description": "Anzahl Ergebnisse (Standard: 20, max: 100)",
                    "default": 20,
                    "minimum": 1,
                    "maximum": 100,
                },
            },
        },
    ),
]


async def handle_blaulicht(name: str, arguments: dict) -> list[TextContent]:
    if name == "blaulicht_suche":
        result = await api_get(
            "/v1/blaulicht/search",
            params={
                "q": arguments["q"],
                "bundesland": arguments.get("bundesland"),
                "category": arguments.get("category"),
                "date_from": arguments.get("date_from"),
                "date_to": arguments.get("date_to"),
                "size": arguments.get("size", 20),
            },
        )
        if not result["ok"]:
            return [TextContent(type="text", text=format_error(result["error"]))]
        return [TextContent(type="text", text=_format_blaulicht_search(result["data"]))]

    elif name == "blaulicht_meldungen":
        result = await api_get(
            "/v1/blaulicht/meldungen",
            params={
                "bundesland": arguments.get("bundesland"),
                "category": arguments.get("category"),
                "q": arguments.get("q"),
                "limit": arguments.get("limit", 20),
            },
        )
        if not result["ok"]:
            return [TextContent(type="text", text=format_error(result["error"]))]
        return [TextContent(type="text", text=_format_blaulicht_meldungen(result["data"]))]

    return [TextContent(type="text", text=format_error(f"Unbekanntes Tool: {name}"))]


# ---------------------------------------------------------------------------
# Formatting
# ---------------------------------------------------------------------------

def _trunc(s, maxlen=200):
    if not s:
        return ""
    s = str(s).strip()
    return s[:maxlen] + "…" if len(s) > maxlen else s


def _none(v, fallback="–"):
    if v is None or v == "":
        return fallback
    return str(v)


def _format_blaulicht_search(data: dict) -> str:
    total = data.get("total", 0)
    results = data.get("results", [])
    page = data.get("page", 0)
    size = data.get("size", 20)
    lines = [f"🚨 Blaulicht-Suche — {total} Treffer (Seite {page + 1})\n"]
    for r in results:
        cat_icon = {"polizei": "👮", "feuerwehr": "🚒", "rettungsdienst": "🚑"}.get(
            r.get("category", ""), "🔵"
        )
        lines.append(f"{cat_icon} **{_trunc(r.get('title'), 120)}**")
        lines.append(
            f"   📍 {_none(r.get('location'))} | 🗺 {_none(r.get('bundesland'))} | "
            f"📅 {_none(r.get('published_at', ''))[:16]}"
        )
        lines.append(f"   🏢 {_none(r.get('org_name'))}")
        hl = r.get("highlights", {})
        if hl:
            for field_highlights in hl.values():
                if field_highlights:
                    snippet = field_highlights[0].replace("<mark>", "«").replace("</mark>", "»")
                    lines.append(f"   💬 {_trunc(snippet, 200)}")
                    break
        if r.get("url"):
            lines.append(f"   🔗 {r['url']}")
        lines.append("")
    return "\n".join(lines)


def _format_blaulicht_meldungen(data: dict) -> str:
    total = data.get("total", 0)
    results = data.get("results", [])
    lines = [f"🚨 Aktuelle Blaulicht-Meldungen — {total} gesamt\n"]
    for r in results:
        cat_icon = {"polizei": "👮", "feuerwehr": "🚒", "rettungsdienst": "🚑"}.get(
            r.get("category", ""), "🔵"
        )
        lines.append(f"{cat_icon} **{_trunc(r.get('title'), 120)}**")
        lines.append(
            f"   📍 {_none(r.get('location'))} | 🗺 {_none(r.get('bundesland'))} | "
            f"📅 {_none(r.get('published_at', ''))[:16]}"
        )
        lines.append(f"   🏢 {_none(r.get('org_name'))}")
        if r.get("url"):
            lines.append(f"   🔗 {r['url']}")
        lines.append("")
    return "\n".join(lines)
