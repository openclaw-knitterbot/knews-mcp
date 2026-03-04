"""
MCP Tools für Rechtsprechung (Gerichtsurteile und Beschlüsse aus deutschen Gerichten).

Scope required: rechtsprechung:read
"""

from mcp.types import TextContent, Tool

from ..client import api_get
from ..formatting import format_error

RECHTSPRECHUNG_TOOLS = [
    Tool(
        name="rechtsprechung_suche",
        description=(
            "Sucht Gerichtsurteile und Beschlüsse (64.000+ Entscheidungen aus deutschen Gerichten). "
            "Filtert nach Gerichtsbarkeit, Gerichtsebene, Gericht, Entscheidungstyp und Datum. "
            "Nützlich für: Rechtsprechungsrecherche, Fallanalyse, Präzedenzfälle finden, "
            "Compliance-Prüfung, Medienrecht, Arbeitsrecht, Verwaltungsrecht.\n\n"
            "Search German court decisions (judgments and orders) across all jurisdictions."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "q": {
                    "type": "string",
                    "description": "Volltext-Suchbegriff (z.B. Aktenzeichen, Rechtsbegriff, Parteiname)",
                },
                "jurisdiction": {
                    "type": "string",
                    "description": (
                        "Gerichtsbarkeit: 'Verwaltungsgerichtsbarkeit', 'Ordentliche Gerichtsbarkeit', "
                        "'Sozialgerichtsbarkeit', 'Arbeitsgerichtsbarkeit', 'Finanzgerichtsbarkeit', "
                        "'Verfassungsgerichtsbarkeit'"
                    ),
                },
                "court_level": {
                    "type": "string",
                    "description": (
                        "Gerichtsebene: 'Bundesgericht', 'Oberlandesgericht', "
                        "'Landgericht', 'Amtsgericht'"
                    ),
                },
                "court_name": {
                    "type": "string",
                    "description": "Name des Gerichts (Teilsuche, z.B. 'Bundesgerichtshof', 'LG München')",
                },
                "type": {
                    "type": "string",
                    "description": "Entscheidungstyp: 'Urteil', 'Beschluss', 'Endurteil', 'Teilurteil'",
                },
                "date_from": {
                    "type": "string",
                    "description": "Entschieden ab (YYYY-MM-DD)",
                    "pattern": "^\\d{4}-\\d{2}-\\d{2}$",
                },
                "date_to": {
                    "type": "string",
                    "description": "Entschieden bis (YYYY-MM-DD)",
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
        },
    ),
    Tool(
        name="rechtsprechung_stats",
        description=(
            "Statistiken zur Rechtsprechungsdatenbank: Gesamtzahl, Verteilung nach "
            "Gerichtsbarkeit, Gerichtsebene und Entscheidungstyp. "
            "Nützlich für: Überblick über abgedeckte Gerichte und Entscheidungstypen, "
            "Analyse der Datenbankabdeckung.\n\n"
            "Statistics on court decisions database: totals by jurisdiction, court level, decision type."
        ),
        inputSchema={
            "type": "object",
            "properties": {},
        },
    ),
    Tool(
        name="rechtsprechung_jurisdictions",
        description=(
            "Listet alle Gerichtsbarkeiten mit Anzahl der Entscheidungen. "
            "Nützlich für: Auswahl der richtigen Gerichtsbarkeit für eine Suchanfrage, "
            "Überblick über Datenbankabdeckung.\n\n"
            "List all jurisdictions (Gerichtsbarkeiten) with case counts."
        ),
        inputSchema={
            "type": "object",
            "properties": {},
        },
    ),
]


async def handle_rechtsprechung(name: str, arguments: dict) -> list[TextContent]:
    if name == "rechtsprechung_suche":
        result = await api_get(
            "/v1/rechtsprechung/cases",
            params={
                "q": arguments.get("q"),
                "jurisdiction": arguments.get("jurisdiction"),
                "court_level": arguments.get("court_level"),
                "court_name": arguments.get("court_name"),
                "type": arguments.get("type"),
                "date_from": arguments.get("date_from"),
                "date_to": arguments.get("date_to"),
                "size": arguments.get("size", 20),
            },
        )
        if not result["ok"]:
            return [TextContent(type="text", text=format_error(result["error"]))]
        return [TextContent(type="text", text=_format_rechtsprechung_cases(result["data"]))]

    elif name == "rechtsprechung_stats":
        result = await api_get("/v1/rechtsprechung/stats")
        if not result["ok"]:
            return [TextContent(type="text", text=format_error(result["error"]))]
        return [TextContent(type="text", text=_format_rechtsprechung_stats(result["data"]))]

    elif name == "rechtsprechung_jurisdictions":
        result = await api_get("/v1/rechtsprechung/jurisdictions")
        if not result["ok"]:
            return [TextContent(type="text", text=format_error(result["error"]))]
        return [TextContent(type="text", text=_format_rechtsprechung_jurisdictions(result["data"]))]

    return [TextContent(type="text", text=format_error(f"Unbekanntes Tool: {name}"))]


# ---------------------------------------------------------------------------
# Formatting
# ---------------------------------------------------------------------------

def _none(v, fallback="–"):
    if v is None or v == "":
        return fallback
    return str(v)


_JURISDICTION_ICON = {
    "Ordentliche Gerichtsbarkeit": "⚖️",
    "Verwaltungsgerichtsbarkeit": "🏛",
    "Sozialgerichtsbarkeit": "🏥",
    "Arbeitsgerichtsbarkeit": "💼",
    "Finanzgerichtsbarkeit": "💶",
    "Verfassungsgerichtsbarkeit": "📜",
}


def _format_rechtsprechung_cases(data: dict) -> str:
    total = data.get("total", 0)
    results = data.get("results", [])
    page = data.get("page", 0)
    size = data.get("size", 20)
    pages = (total + size - 1) // size if size > 0 else 1
    lines = [f"⚖️ Rechtsprechung-Suche — {total} Treffer (Seite {page + 1}/{pages})\n"]
    for r in results:
        jur = r.get("court_jurisdiction", "")
        icon = _JURISDICTION_ICON.get(jur, "⚖️")
        type_str = _none(r.get("type"))
        lines.append(f"{icon} **{_none(r.get('court_name'))}** — {type_str}")
        lines.append(
            f"   📋 Az: {_none(r.get('file_number'))} | 📅 {_none(r.get('date'))}"
        )
        lines.append(
            f"   🏛 {_none(r.get('court_jurisdiction'))} | Ebene: {_none(r.get('court_level'))}"
        )
        if r.get("ecli"):
            lines.append(f"   🔖 ECLI: {_none(r.get('ecli'))}")
        lines.append("")
    return "\n".join(lines)


def _format_rechtsprechung_stats(data: dict) -> str:
    lines = [
        f"📊 Rechtsprechung-Statistiken — {data.get('total', 0):,} Entscheidungen gesamt\n",
        "**Nach Gerichtsbarkeit:**",
    ]
    for item in data.get("by_jurisdiction", []):
        icon = _JURISDICTION_ICON.get(item.get("jurisdiction", ""), "⚖️")
        lines.append(f"  {icon} {_none(item.get('jurisdiction'))}: {item.get('count', 0):,}")
    lines.append("")
    lines.append("**Nach Gerichtsebene:**")
    for item in data.get("by_court_level", []):
        lines.append(f"  {_none(item.get('court_level'))}: {item.get('count', 0):,}")
    lines.append("")
    lines.append("**Nach Entscheidungstyp:**")
    for item in data.get("by_type", [])[:10]:
        lines.append(f"  {_none(item.get('type'))}: {item.get('count', 0):,}")
    return "\n".join(lines)


def _format_rechtsprechung_jurisdictions(data: dict) -> str:
    results = data.get("results", [])
    count = data.get("count", len(results))
    lines = [f"🏛 Gerichtsbarkeiten — {count} Einträge\n"]
    for item in results:
        icon = _JURISDICTION_ICON.get(item.get("jurisdiction", ""), "⚖️")
        lines.append(
            f"  {icon} **{_none(item.get('jurisdiction'))}**: {item.get('count', 0):,} Entscheidungen"
        )
    return "\n".join(lines)
