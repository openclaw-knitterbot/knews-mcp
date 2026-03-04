"""
MCP Tools für Insolvenzbekanntmachungen (Insolvenzgerichte via insolvenzbekanntmachungen.de).

Scope required: insolvenzen:read
"""

from mcp.types import TextContent, Tool

from ..client import api_get
from ..formatting import format_error

INSOLVENZEN_TOOLS = [
    Tool(
        name="insolvenzen_suche",
        description=(
            "Volltextsuche in Insolvenzbekanntmachungen (Elasticsearch, 69.000+ Einträge). "
            "Filtert nach Verfahrensgegenstand, Registerart, Datum. "
            "Mit nur_firmen=true: nur Unternehmensinsolvenzen (HRB/HRA-Einträge). "
            "Nützlich für: Insolvenz-Check für eine Firma, Gläubiger-Recherche, "
            "wirtschaftliche Risikoprüfung, investigativer Journalismus.\n\n"
            "Full-text search in German insolvency announcements (company and personal insolvencies)."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "q": {
                    "type": "string",
                    "description": "Suchbegriff (Firmenname, Personenname, Aktenzeichen, Sitz)",
                },
                "gegenstand": {
                    "type": "string",
                    "description": (
                        "Verfahrensgegenstand (z.B. 'Eröffnungen', 'Abweisungen mangels Masse', "
                        "'Sicherungsmaßnahmen', 'Restschuldbefreiungsverfahren')"
                    ),
                },
                "register_art": {
                    "type": "string",
                    "description": "Registerart: 'HRB' (GmbH/AG), 'HRA' (Personengesellschaft), 'VR' (Verein)",
                },
                "nur_firmen": {
                    "type": "boolean",
                    "description": "Nur Unternehmensinsolvenzen (mit HR-Eintrag), keine Privatinsolvenzen",
                    "default": False,
                },
                "date_from": {
                    "type": "string",
                    "description": "Veröffentlicht ab (YYYY-MM-DD)",
                    "pattern": "^\\d{4}-\\d{2}-\\d{2}$",
                },
                "date_to": {
                    "type": "string",
                    "description": "Veröffentlicht bis (YYYY-MM-DD)",
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
        name="insolvenzen_liste",
        description=(
            "Listet Insolvenzbekanntmachungen (SQL, nach Datum sortiert). "
            "Filtert nach Gericht, Sitz, Verfahrensgegenstand, Registerart und Zeitraum. "
            "Nützlich für: Überblick über aktuelle Insolvenzen in einer Region, "
            "Gericht-spezifische Analyse, Volumenmessung.\n\n"
            "List insolvency announcements sorted by date. Filter by court, location, type."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "gegenstand": {
                    "type": "string",
                    "description": "Verfahrensgegenstand (z.B. 'Eröffnungen', 'Abweisungen mangels Masse')",
                },
                "register_art": {
                    "type": "string",
                    "description": "Registerart: 'HRB', 'HRA', 'VR'",
                },
                "gericht": {
                    "type": "string",
                    "description": "Insolvenzgericht (Teilsuche, z.B. 'München', 'Charlottenburg')",
                },
                "sitz": {
                    "type": "string",
                    "description": "Sitz des Schuldners (Stadt, z.B. 'Berlin', 'Hamburg')",
                },
                "nur_firmen": {
                    "type": "boolean",
                    "description": "Nur Unternehmensinsolvenzen (mit HR-Eintrag)",
                    "default": False,
                },
                "date_from": {
                    "type": "string",
                    "description": "Veröffentlicht ab (YYYY-MM-DD)",
                    "pattern": "^\\d{4}-\\d{2}-\\d{2}$",
                },
                "date_to": {
                    "type": "string",
                    "description": "Veröffentlicht bis (YYYY-MM-DD)",
                    "pattern": "^\\d{4}-\\d{2}-\\d{2}$",
                },
                "limit": {
                    "type": "integer",
                    "description": "Anzahl Ergebnisse (Standard: 20, max: 200)",
                    "default": 20,
                    "minimum": 1,
                    "maximum": 200,
                },
            },
        },
    ),
    Tool(
        name="insolvenzen_stats",
        description=(
            "Statistiken zu Insolvenzbekanntmachungen: Gesamtzahlen, Eröffnungen, Abweisungen, "
            "Firmensachen, Verteilung nach Verfahrensgegenstand, Erfassungszeitraum. "
            "Nützlich für: Wirtschaftsklima-Indikator, Insolvenzentwicklung beobachten, "
            "Marktforschung, Konjunkturanalyse.\n\n"
            "Statistics on German insolvency announcements: totals, openings, rejections, by type."
        ),
        inputSchema={
            "type": "object",
            "properties": {},
        },
    ),
]


async def handle_insolvenzen(name: str, arguments: dict) -> list[TextContent]:
    if name == "insolvenzen_suche":
        result = await api_get(
            "/v1/insolvenzen/search",
            params={
                "q": arguments["q"],
                "gegenstand": arguments.get("gegenstand"),
                "register_art": arguments.get("register_art"),
                "nur_firmen": arguments.get("nur_firmen", False),
                "date_from": arguments.get("date_from"),
                "date_to": arguments.get("date_to"),
                "size": arguments.get("size", 20),
            },
        )
        if not result["ok"]:
            return [TextContent(type="text", text=format_error(result["error"]))]
        return [TextContent(type="text", text=_format_insolvenzen_search(result["data"]))]

    elif name == "insolvenzen_liste":
        result = await api_get(
            "/v1/insolvenzen/bekanntmachungen",
            params={
                "gegenstand": arguments.get("gegenstand"),
                "register_art": arguments.get("register_art"),
                "gericht": arguments.get("gericht"),
                "sitz": arguments.get("sitz"),
                "nur_firmen": arguments.get("nur_firmen", False),
                "date_from": arguments.get("date_from"),
                "date_to": arguments.get("date_to"),
                "limit": arguments.get("limit", 20),
            },
        )
        if not result["ok"]:
            return [TextContent(type="text", text=format_error(result["error"]))]
        return [TextContent(type="text", text=_format_insolvenzen_liste(result["data"]))]

    elif name == "insolvenzen_stats":
        result = await api_get("/v1/insolvenzen/stats")
        if not result["ok"]:
            return [TextContent(type="text", text=format_error(result["error"]))]
        return [TextContent(type="text", text=_format_insolvenzen_stats(result["data"]))]

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


def _format_insolvenz_row(r: dict) -> list[str]:
    """Formatiert eine Insolvenz-Zeile (gemeinsam für Liste und Suche)."""
    lines = []
    is_firma = bool(r.get("register_art"))
    icon = "🏢" if is_firma else "👤"
    name = r.get("schuldner_name", "")
    vorname = r.get("schuldner_vorname", "")
    vollname = f"{vorname} {name}".strip() if vorname else name
    lines.append(f"{icon} **{vollname}**")
    lines.append(
        f"   📍 {_none(r.get('sitz'))} | ⚖️ {_none(r.get('gericht'))} | "
        f"📅 {_none(r.get('veroeffentlicht_am'))}"
    )
    lines.append(
        f"   📋 {_none(r.get('gegenstand'))} | Az: {_none(r.get('aktenzeichen'))}"
    )
    if r.get("register_art"):
        lines.append(
            f"   🗃 Register: {_none(r.get('register_art'))} {_none(r.get('register_nr'))} "
            f"({_none(r.get('register_gericht'))})"
        )
    return lines


def _format_insolvenzen_search(data: dict) -> str:
    total = data.get("total", 0)
    results = data.get("results", [])
    page = data.get("page", 0)
    size = data.get("size", 20)
    lines = [f"🔍 Insolvenz-Suche — {total} Treffer (Seite {page + 1})\n"]
    for r in results:
        lines.extend(_format_insolvenz_row(r))
        hl = r.get("highlights", {})
        for field_highlights in hl.values():
            if field_highlights:
                snippet = field_highlights[0].replace("<mark>", "«").replace("</mark>", "»")
                lines.append(f"   💬 {_trunc(snippet, 200)}")
                break
        lines.append("")
    return "\n".join(lines)


def _format_insolvenzen_liste(data: dict) -> str:
    total = data.get("total", 0)
    results = data.get("results", [])
    lines = [f"📋 Insolvenzbekanntmachungen — {total} gesamt\n"]
    for r in results:
        lines.extend(_format_insolvenz_row(r))
        lines.append("")
    return "\n".join(lines)


def _format_insolvenzen_stats(data: dict) -> str:
    lines = [
        "📊 Insolvenz-Statistiken\n",
        f"Bekanntmachungen gesamt: {data.get('total', 0):,}",
        f"  davon Eröffnungen: {data.get('eroeffnungen', 0):,}",
        f"  davon Abweisungen m.M.: {data.get('abweisungen', 0):,}",
        f"  Sicherungsmaßnahmen: {data.get('sicherungsmasnahmen', 0):,}",
        f"  Firmensachen (HR-Eintrag): {data.get('firmensachen', 0):,}",
        f"",
        f"Erfassungszeitraum: {_none(data.get('erster_tag'))} – {_none(data.get('letzter_tag'))}",
        f"  Tage erfasst: {data.get('tage_erfasst', 0)}",
        f"  Letzter Scrape: {_none(data.get('letzter_scrape'))}",
        "",
        "**Nach Verfahrensgegenstand:**",
    ]
    for item in data.get("by_gegenstand", []):
        lines.append(f"  {_none(item.get('label'))}: {item.get('anzahl', 0):,}")
    return "\n".join(lines)
