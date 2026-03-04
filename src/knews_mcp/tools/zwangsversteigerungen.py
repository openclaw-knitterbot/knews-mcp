"""
MCP Tools für Zwangsversteigerungen (ZVG-Portal Daten aus deutschen Amtsgerichten).

Scope required: zwangsversteigerungen:read
"""

from mcp.types import TextContent, Tool

from ..client import api_get
from ..formatting import format_error

ZWANGSVERSTEIGERUNGEN_TOOLS = [
    Tool(
        name="zvg_stats",
        description=(
            "Überblick über aktuelle Zwangsversteigerungen in Deutschland: "
            "Gesamtzahl, Verteilung nach Bundesland, Verkehrswert-Statistiken "
            "und Termine diese/nächste Woche. "
            "Nützlich für: Immobilienmarkt-Analyse, Investitionsentscheidungen, "
            "regionale Risikobeurteilung, wirtschaftliche Lageeinschätzung.\n\n"
            "Overview of German forced auction (Zwangsversteigerung) statistics: "
            "totals, by state, property values, upcoming dates."
        ),
        inputSchema={
            "type": "object",
            "properties": {},
        },
    ),
    Tool(
        name="zvg_liste",
        description=(
            "Listet aktuelle Zwangsversteigerungstermine (SQL, nach Termin sortiert). "
            "Filtert nach Bundesland, Termindatum, Verkehrswert und Gericht. "
            "Nützlich für: Schnäppchensuche, regionale Immobilien-Pipeline, "
            "Due Diligence vor Bietung, Marktpreisanalyse.\n\n"
            "List forced auction listings filtered by state, date, property value, court."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "land_abk": {
                    "type": "string",
                    "description": (
                        "Bundesland-Kürzel (z.B. 'nw' Nordrhein-Westfalen, 'by' Bayern, "
                        "'bw' Baden-Württemberg, 'he' Hessen, 'ni' Niedersachsen, "
                        "'be' Berlin, 'rp' Rheinland-Pfalz, 'sn' Sachsen, "
                        "'st' Sachsen-Anhalt, 'th' Thüringen, 'sl' Saarland, "
                        "'sh' Schleswig-Holstein, 'hb' Bremen, 'hh' Hamburg, 'mv' Mecklenburg-Vorpommern)"
                    ),
                },
                "termin_von": {
                    "type": "string",
                    "description": "Termin ab (YYYY-MM-DD)",
                    "pattern": "^\\d{4}-\\d{2}-\\d{2}$",
                },
                "termin_bis": {
                    "type": "string",
                    "description": "Termin bis (YYYY-MM-DD)",
                    "pattern": "^\\d{4}-\\d{2}-\\d{2}$",
                },
                "min_verkehrswert": {
                    "type": "number",
                    "description": "Mindest-Verkehrswert in EUR (z.B. 100000)",
                },
                "max_verkehrswert": {
                    "type": "number",
                    "description": "Maximal-Verkehrswert in EUR (z.B. 500000)",
                },
                "aufgehoben": {
                    "type": "boolean",
                    "description": "Auch aufgehobene Termine einschließen (Standard: false)",
                    "default": False,
                },
                "gericht": {
                    "type": "string",
                    "description": "Amtsgericht (Teilsuche, z.B. 'München', 'Köln')",
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
        name="zvg_suche",
        description=(
            "Volltextsuche in Zwangsversteigerungen (Elasticsearch). "
            "Durchsucht Objektbeschreibung, Lage und Ort. "
            "Nützlich für: Suche nach bestimmten Immobilientypen (z.B. 'Einfamilienhaus', 'Gewerbe'), "
            "Standortsuche (Straßenname, Stadt), Investitionsrecherche.\n\n"
            "Full-text search in forced auction listings (property description, location)."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "q": {
                    "type": "string",
                    "description": (
                        "Suchbegriff (z.B. 'Einfamilienhaus München', 'Gewerbe', "
                        "'Eigentumswohnung', 'Grundstück')"
                    ),
                },
                "land_abk": {
                    "type": "string",
                    "description": "Bundesland-Kürzel filtern (z.B. 'nw', 'by', 'bw')",
                },
                "termin_von": {
                    "type": "string",
                    "description": "Termin ab (YYYY-MM-DD)",
                    "pattern": "^\\d{4}-\\d{2}-\\d{2}$",
                },
                "termin_bis": {
                    "type": "string",
                    "description": "Termin bis (YYYY-MM-DD)",
                    "pattern": "^\\d{4}-\\d{2}-\\d{2}$",
                },
                "aufgehoben": {
                    "type": "boolean",
                    "description": "Auch aufgehobene Termine einschließen",
                    "default": False,
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
]


async def handle_zwangsversteigerungen(name: str, arguments: dict) -> list[TextContent]:
    if name == "zvg_stats":
        result = await api_get("/v1/zwangsversteigerungen/stats")
        if not result["ok"]:
            return [TextContent(type="text", text=format_error(result["error"]))]
        return [TextContent(type="text", text=_format_zvg_stats(result["data"]))]

    elif name == "zvg_liste":
        result = await api_get(
            "/v1/zwangsversteigerungen/liste",
            params={
                "land_abk": arguments.get("land_abk"),
                "termin_von": arguments.get("termin_von"),
                "termin_bis": arguments.get("termin_bis"),
                "min_verkehrswert": arguments.get("min_verkehrswert"),
                "max_verkehrswert": arguments.get("max_verkehrswert"),
                "aufgehoben": arguments.get("aufgehoben", False),
                "gericht": arguments.get("gericht"),
                "limit": arguments.get("limit", 20),
            },
        )
        if not result["ok"]:
            return [TextContent(type="text", text=format_error(result["error"]))]
        return [TextContent(type="text", text=_format_zvg_liste(result["data"]))]

    elif name == "zvg_suche":
        result = await api_get(
            "/v1/zwangsversteigerungen/search",
            params={
                "q": arguments["q"],
                "land_abk": arguments.get("land_abk"),
                "termin_von": arguments.get("termin_von"),
                "termin_bis": arguments.get("termin_bis"),
                "aufgehoben": arguments.get("aufgehoben", False),
                "size": arguments.get("size", 20),
            },
        )
        if not result["ok"]:
            return [TextContent(type="text", text=format_error(result["error"]))]
        return [TextContent(type="text", text=_format_zvg_search(result["data"]))]

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


def _format_zvg_row(r: dict) -> list[str]:
    """Formatiert eine ZVG-Zeile."""
    lines = []
    aufgehoben = r.get("termin_aufgehoben", False)
    status = "❌ aufgehoben" if aufgehoben else "✅ aktiv"
    vkw = r.get("verkehrswert")
    vkw_str = f"{vkw:,.0f} €" if vkw is not None else "k.A."
    termin = r.get("termin_datum")
    uhrzeit = r.get("termin_uhrzeit", "")
    termin_str = f"{_none(termin)} {str(uhrzeit)[:5]}".strip() if termin else "kein Termin"

    lines.append(f"🏠 **{_trunc(r.get('objekt_lage'), 100)}** [{status}]")
    lines.append(f"   💶 Verkehrswert: {vkw_str} | 📅 Termin: {termin_str}")
    lines.append(f"   ⚖️ {_none(r.get('gericht'))} | 🗺 {_none(r.get('land_name') or r.get('land_abk'))}")
    if r.get("art"):
        lines.append(f"   📋 {_trunc(r.get('art'), 80)}")
    if r.get("beschreibung"):
        lines.append(f"   📝 {_trunc(r.get('beschreibung'), 150)}")
    if r.get("ort_der_versteigerung"):
        lines.append(f"   📍 Versteigerungsort: {_trunc(r.get('ort_der_versteigerung'), 100)}")
    if r.get("pdf_url"):
        lines.append(f"   🔗 {r['pdf_url']}")
    return lines


def _format_zvg_stats(data: dict) -> str:
    vkw = data.get("verkehrswert", {})
    termine = data.get("termine", {})
    lines = [
        "🏠 Zwangsversteigerungen — Überblick\n",
        f"Objekte gesamt: {data.get('total', 0):,}",
        f"  Aktiv: {data.get('aktiv', 0):,} | Aufgehoben: {data.get('aufgehoben', 0):,}",
        f"  Bundesländer abgedeckt: {data.get('bundeslaender_anzahl', 0)}",
        f"",
        f"**Verkehrswerte:**",
        f"  Ø Verkehrswert: {vkw.get('durchschnitt', 0):,.0f} €",
        f"  Gesamtvolumen: {vkw.get('summe', 0) / 1_000_000:,.1f} Mio. €",
        f"  Mit Wertangabe: {vkw.get('mit_angabe', 0):,} Objekte",
        f"",
        f"**Termine:**",
        f"  Diese Woche: {termine.get('diese_woche', 0)}",
        f"  Nächste Woche: {termine.get('naechste_woche', 0)}",
        f"",
        f"**Nach Bundesland (Top 10):**",
    ]
    for bl in data.get("by_bundesland", [])[:10]:
        avg = bl.get("vkw_avg", 0) or 0
        lines.append(
            f"  {_none(bl.get('land_name'))} ({_none(bl.get('land_abk'))}): "
            f"{bl.get('anzahl', 0):,} | Ø {avg:,.0f} €"
        )

    vv = data.get("verkehrswert_verteilung", {})
    if vv:
        lines.append("")
        lines.append("**Wertverteilung:**")
        lines.append(f"  < 100k €: {vv.get('unter_100k', 0):,}")
        lines.append(f"  100k–250k €: {vv.get('100k_250k', 0):,}")
        lines.append(f"  250k–500k €: {vv.get('250k_500k', 0):,}")
        lines.append(f"  500k–1 Mio. €: {vv.get('500k_1m', 0):,}")
        lines.append(f"  > 1 Mio. €: {vv.get('ueber_1m', 0):,}")

    return "\n".join(lines)


def _format_zvg_liste(data: dict) -> str:
    total = data.get("total", 0)
    results = data.get("results", [])
    lines = [f"🏠 Zwangsversteigerungen — {total} Einträge\n"]
    for r in results:
        lines.extend(_format_zvg_row(r))
        lines.append("")
    return "\n".join(lines)


def _format_zvg_search(data: dict) -> str:
    total = data.get("total", 0)
    results = data.get("results", [])
    page = data.get("page", 0)
    size = data.get("size", 20)
    lines = [f"🔍 ZVG-Suche — {total} Treffer (Seite {page + 1})\n"]
    for r in results:
        lines.extend(_format_zvg_row(r))
        hl = r.get("highlights", {})
        for field_highlights in hl.values():
            if field_highlights:
                snippet = field_highlights[0].replace("<mark>", "«").replace("</mark>", "»")
                lines.append(f"   💬 {_trunc(snippet, 200)}")
                break
        lines.append("")
    return "\n".join(lines)
