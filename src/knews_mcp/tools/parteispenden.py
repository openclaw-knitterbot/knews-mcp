"""
MCP Tools für Parteispenden (Bundestagspräsidium-Veröffentlichungen).

Scope required: parteispenden:read
"""

from mcp.types import TextContent, Tool

from ..client import api_get
from ..formatting import format_error

PARTEISPENDEN_TOOLS = [
    Tool(
        name="parteispenden_suche",
        description=(
            "Sucht in Parteispenden-Bekanntmachungen des Bundestages (765+ Einträge, Spenden > 35.000 €). "
            "Filtert nach Spender, Partei, Jahr und Mindestbetrag. "
            "Nützlich für: Parteispendenrecherche, Unternehmens-Politik-Verflechtung, "
            "Transparenzanalyse, investigativer Journalismus.\n\n"
            "Search German party donation announcements (Bundestag transparency, donations >35,000 EUR)."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "spender": {
                    "type": "string",
                    "description": "Name des Spenders (Person oder Unternehmen, z.B. 'BMW AG', 'Klaus Muster')",
                },
                "partei": {
                    "type": "string",
                    "description": "Partei (z.B. 'CDU', 'SPD', 'FDP', 'Grünen', 'CSU', 'AfD')",
                },
                "jahr": {
                    "type": "integer",
                    "description": "Spendenjahr (z.B. 2024, 2025, 2026)",
                },
                "betrag_min": {
                    "type": "number",
                    "description": "Mindestbetrag in EUR (Standard: 35.000)",
                },
                "date_from": {
                    "type": "string",
                    "description": "Anzeige-Datum ab (YYYY-MM-DD)",
                    "pattern": "^\\d{4}-\\d{2}-\\d{2}$",
                },
                "date_to": {
                    "type": "string",
                    "description": "Anzeige-Datum bis (YYYY-MM-DD)",
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
        name="parteispenden_stats",
        description=(
            "Gesamtstatistiken zu Parteispenden: Summe und Anzahl nach Partei, "
            "Gesamtvolumen aller erfassten Spenden. "
            "Nützlich für: Welche Partei erhält am meisten Spenden? "
            "Vergleich Parteienfinanzierung, politische Analyse.\n\n"
            "Party donation statistics: totals by party, overall donation volume."
        ),
        inputSchema={
            "type": "object",
            "properties": {},
        },
    ),
    Tool(
        name="parteispenden_parteien",
        description=(
            "Liste aller Parteien mit Spendenzahlen (Anzahl + Summe). "
            "Nützlich für: Übersicht welche Parteien in der Datenbank vertreten sind, "
            "Auswahl für gezielte Abfragen.\n\n"
            "List all parties with donation counts and sums from the database."
        ),
        inputSchema={
            "type": "object",
            "properties": {},
        },
    ),
]


async def handle_parteispenden(name: str, arguments: dict) -> list[TextContent]:
    if name == "parteispenden_suche":
        result = await api_get(
            "/v1/parteispenden/spenden",
            params={
                "spender": arguments.get("spender"),
                "partei": arguments.get("partei"),
                "jahr": arguments.get("jahr"),
                "betrag_min": arguments.get("betrag_min"),
                "date_from": arguments.get("date_from"),
                "date_to": arguments.get("date_to"),
                "size": arguments.get("size", 20),
            },
        )
        if not result["ok"]:
            return [TextContent(type="text", text=format_error(result["error"]))]
        return [TextContent(type="text", text=_format_parteispenden_suche(result["data"]))]

    elif name == "parteispenden_stats":
        result = await api_get("/v1/parteispenden/stats")
        if not result["ok"]:
            return [TextContent(type="text", text=format_error(result["error"]))]
        return [TextContent(type="text", text=_format_parteispenden_stats(result["data"]))]

    elif name == "parteispenden_parteien":
        result = await api_get("/v1/parteispenden/parteien")
        if not result["ok"]:
            return [TextContent(type="text", text=format_error(result["error"]))]
        return [TextContent(type="text", text=_format_parteispenden_parteien(result["data"]))]

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


_PARTEI_ICON = {
    "CDU": "⬛", "CSU": "⬛", "SPD": "🟥", "FDP": "🟨",
    "Grünen": "🟩", "AfD": "🟦", "BSW": "🟪", "Linke/PDS": "🟥",
}


def _partei_icon(partei: str) -> str:
    for key, icon in _PARTEI_ICON.items():
        if key.lower() in str(partei).lower():
            return icon
    return "🎗"


def _format_parteispenden_suche(data: dict) -> str:
    total = data.get("total", 0)
    results = data.get("results", [])
    page = data.get("page", 0)
    size = data.get("size", 20)
    lines = [f"💰 Parteispenden-Suche — {total} Treffer (Seite {page + 1})\n"]
    for r in results:
        icon = _partei_icon(r.get("partei", ""))
        betrag = r.get("betrag")
        betrag_str = f"{betrag:,.0f} €" if betrag is not None else "–"
        lines.append(f"{icon} **{_none(r.get('spender_name'))}** → {_none(r.get('partei'))}")
        lines.append(f"   💶 {betrag_str} | 📅 Spende: {_none(r.get('datum_spende'))} | "
                     f"Anzeige: {_none(r.get('datum_anzeige'))}")
        lines.append(f"   📍 {_trunc(r.get('spender_adresse'), 100)}")
        if r.get("drucksache"):
            lines.append(f"   📄 Drucksache: {_none(r.get('drucksache'))}")
        lines.append("")
    if total == 0:
        lines.append("Keine Parteispenden gefunden.")
    return "\n".join(lines)


def _format_parteispenden_stats(data: dict) -> str:
    summe = data.get("summe", 0)
    total = data.get("total", 0)
    lines = [
        "📊 Parteispenden-Statistiken\n",
        f"Spenden gesamt: {total:,}",
        f"Gesamtvolumen: {summe:,.2f} €\n",
        "**Nach Partei:**",
    ]
    for p in data.get("by_partei", []):
        icon = _partei_icon(p.get("partei", ""))
        s = p.get("summe", 0) or 0
        n = p.get("anzahl", 0)
        lines.append(
            f"  {icon} {_none(p.get('partei'))}: {n:,} Spenden | {s:,.0f} €"
        )
    return "\n".join(lines)


def _format_parteispenden_parteien(data: dict) -> str:
    results = data.get("results", [])
    count = data.get("count", len(results))
    lines = [f"🎗 Parteien in der Spendendatenbank — {count} Einträge\n"]
    for p in results:
        icon = _partei_icon(p.get("partei", ""))
        s = p.get("summe", 0) or 0
        n = p.get("anzahl", 0)
        lines.append(
            f"  {icon} **{_none(p.get('partei'))}**: {n:,} Spenden | {s:,.0f} €"
        )
    return "\n".join(lines)
