"""
Cross-Domain Composite Tools für die knews Datenplattform.

Diese Tools kombinieren mehrere API-Endpunkte parallel via asyncio.gather()
und liefern ein integriertes Gesamtbild — der eigentliche USP von knews-mcp.

Enthaltene Tools:
  - company_360       : HR + Bundesanzeiger + News + Insolvenz-Check + ZVG-Check + Jobs-Signal
  - markt_radar       : Arbeitsmarkt + Jobs + Vergabe für ein Berufsfeld
  - region_dashboard  : Energie + Luft + Arbeitsmarkt + Vergabe für ein Bundesland
  - foerder_match     : Passende Förderprogramme für ein Projekt
  - person_profil     : Mandate + verbundene Firmen + News + Parteispenden-Check

  - energie_trend     : SMARD-Erzeugung + MaStR-Zubau kombiniert
  - arbeitsmarkt_trend: Zeitreihe Arbeitsmarkt mit Highlights
  - vergabe_trend     : Ausschreibungsvolumen im Zeitverlauf

  - insolvenz_radar   : Insolvenz + HR + Bundesanzeiger + ZVG für eine Firma
  - wirtschafts_vernetzung : HR-Mandate + Parteispenden + Bundesanzeiger für eine Person
  - region_radar      : Blaulicht + Insolvenzen + ZVG + Arbeitsmarkt für ein Bundesland
"""

import asyncio

from mcp.types import TextContent, Tool

from ..client import api_get
from ..formatting import (
    format_error,
    format_composite_company_360,
    format_composite_markt_radar,
    format_composite_region_dashboard,
    format_composite_foerder_match,
    format_composite_person_profil,
    format_composite_energie_trend,
    format_composite_arbeitsmarkt_trend,
    format_composite_vergabe_trend,
)

# ---------------------------------------------------------------------------
# Bekannte Jobs-Quellen (DAX / große deutsche Arbeitgeber)
# ---------------------------------------------------------------------------

# Mapping: Schlüsselwörter im Firmennamen (lowercase) → jobs source-Parameter
_JOBS_SOURCES: dict[str, str] = {
    "sap": "sap",
    "volkswagen": "vw",
    " vw ": "vw",
    "vw ag": "vw",
    "vw konzern": "vw",
}


def _detect_jobs_source(company_name: str) -> str | None:
    """Erkennt bekannte DAX-Scraper-Quellen anhand des Firmennamens."""
    name_lower = f" {company_name.lower()} "
    for keyword, source in _JOBS_SOURCES.items():
        if keyword in name_lower:
            return source
    return None


# ---------------------------------------------------------------------------
# Tool-Definitionen
# ---------------------------------------------------------------------------

COMPOSITE_TOOLS = [
    Tool(
        name="company_360",
        description=(
            "360°-Unternehmensprofil: Kombiniert Handelsregister, Bundesanzeiger-Jahresabschlüsse, "
            "aktuelle Nachrichten, Insolvenz-Check und Zwangsversteigerungscheck zu einer Firma. "
            "Bei bekannten DAX-Unternehmen (SAP, VW) auch Stellenanzahl als Vitalitäts-Indikator. "
            "Nützlich für: Due Diligence, Unternehmensanalyse, Journalismus-Recherche.\n\n"
            "360° company profile: Handelsregister + Bundesanzeiger + news + insolvency check + ZVG check."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": "Firmenname (Volltext, z.B. 'Volkswagen AG')",
                },
                "city": {
                    "type": "string",
                    "description": "Stadt/Ort zur Einschränkung (optional, z.B. 'München')",
                },
            },
            "required": ["name"],
        },
    ),
    Tool(
        name="markt_radar",
        description=(
            "Marktüberblick für ein Berufsfeld/eine Branche: Kombiniert Stellenangebote (BA-Jobbörse), "
            "Arbeitsmarkt-Facetten und aktuelle öffentliche Ausschreibungen. "
            "Nützlich für: Berufsfeld-Analyse, Marktforschung, Karriereplanung.\n\n"
            "Market radar: Combines job postings, labor market facets, and public procurement for a sector."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "beruf": {
                    "type": "string",
                    "description": "Berufsfeld oder Branche (z.B. 'Softwareentwickler', 'Pflege', 'Logistik')",
                },
                "region": {
                    "type": "string",
                    "description": "Region oder Bundesland zur Einschränkung (optional, z.B. 'Bayern')",
                },
            },
            "required": ["beruf"],
        },
    ),
    Tool(
        name="region_dashboard",
        description=(
            "Standortprofil für ein Bundesland: Kombiniert Energie-Infrastruktur (MaStR), "
            "Luftqualitätsmessstationen, Arbeitsmarktdaten und Vergabe-Aktivität. "
            "Nützlich für: Investitionsentscheidungen, Standortvergleiche, ESG-Analyse.\n\n"
            "Regional dashboard: Combines energy infrastructure, air quality, labor market, and procurement."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "bundesland": {
                    "type": "string",
                    "description": "Name des Bundeslandes (z.B. 'Bayern', 'NRW', 'Brandenburg')",
                },
            },
            "required": ["bundesland"],
        },
    ),
    Tool(
        name="foerder_match",
        description=(
            "Förderprogramm-Matching: Sucht passende Förderprogramme für ein Projekt. "
            "Gibt Relevanz-Hinweise zu Fördergeber, Zielgruppe und Förderbedingungen. "
            "Nützlich für: Antragsvorbereitung, Finanzierungsrecherche, Gründer-Beratung.\n\n"
            "Funding match: Find relevant German public funding programs for a project description."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "beschreibung": {
                    "type": "string",
                    "description": "Kurze Projektbeschreibung oder Schlagwörter (z.B. 'KI-Startup Energieeffizienz')",
                },
                "rechtsform": {
                    "type": "string",
                    "description": "Rechtsform des Unternehmens (optional, z.B. 'GmbH', 'Einzelunternehmen')",
                },
                "unternehmensgroesse": {
                    "type": "string",
                    "description": "Unternehmensgröße (optional, z.B. 'KMU', 'Startup', 'Großunternehmen')",
                },
            },
            "required": ["beschreibung"],
        },
    ),
    Tool(
        name="person_profil",
        description=(
            "Personenprofil: Recherchiert alle Handelsregister-Mandate einer Person, "
            "verknüpft sie mit Firmendaten, aktuellen Nachrichtenartikeln "
            "und prüft auf Parteispenden-Einträge. "
            "Nützlich für: Verflechtungsanalyse, Hintergrundrecherche, Compliance-Prüfung.\n\n"
            "Person profile: Company mandates, firms, news, and party donation check."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": "Name der Person (Vor- und/oder Nachname, z.B. 'Elon Musk')",
                },
            },
            "required": ["name"],
        },
    ),
    Tool(
        name="energie_trend",
        description=(
            "Energie-Trend: Kombiniert SMARD-Stromerzeugungsdaten mit MaStR-Zubau-Statistiken. "
            "Zeigt Erzeugungsmengen und Ausbau erneuerbarer Energien im Zeitverlauf. "
            "Nützlich für: Energiemarkt-Analyse, Nachhaltigkeitsberichte, Investitionsplanung.\n\n"
            "Energy trend: Combines SMARD generation data and MaStR capacity additions over time."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "days": {
                    "type": "integer",
                    "description": "Zeitraum in Tagen (Standard: 30, max: 365)",
                    "default": 30,
                    "minimum": 1,
                    "maximum": 365,
                },
            },
        },
    ),
    Tool(
        name="arbeitsmarkt_trend",
        description=(
            "Arbeitsmarkt-Trend: Zeitreihenanalyse der BA-Jobbörse mit Highlights. "
            "Zeigt Maximum, Minimum und Durchschnitt der Stellenanzahl im Zeitverlauf. "
            "Nützlich für: Wirtschaftsanalyse, HR-Planung, Konjunkturbeobachtung.\n\n"
            "Labor market trend: Time-series analysis of job postings with highlights (max, min, avg)."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "days": {
                    "type": "integer",
                    "description": "Zeitraum in Tagen (Standard: 90)",
                    "default": 90,
                    "minimum": 7,
                    "maximum": 365,
                },
            },
        },
    ),
    Tool(
        name="vergabe_trend",
        description=(
            "Vergabe-Trend: Überblick über die öffentliche Ausschreibungsaktivität. "
            "Kombiniert aktuelle Ausschreibungen mit aggregierten Statistiken. "
            "Nützlich für: Marktbeobachtung, Angebotsvorbereitung, Vergabe-Monitoring.\n\n"
            "Procurement trend: Overview of public procurement activity with statistics and recent announcements."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "days": {
                    "type": "integer",
                    "description": "Zeitraum in Tagen (Standard: 30)",
                    "default": 30,
                    "minimum": 7,
                    "maximum": 180,
                },
                "q": {
                    "type": "string",
                    "description": "Suchbegriff zur Einschränkung (optional, z.B. 'IT', 'Bau', 'Reinigung')",
                },
            },
        },
    ),
    # --- Neue Composite-Tools (v0.2.0) ---
    Tool(
        name="insolvenz_radar",
        description=(
            "Insolvenz-Radar für eine Firma: Kombiniert laufende Insolvenzverfahren, "
            "Handelsregister-Profil, Bundesanzeiger-Jahresabschlüsse und "
            "Zwangsversteigerungen zu einem Risiko-Assessment. "
            "Nützlich für: Lieferanten-Check, Kreditwürdigkeitsprüfung, "
            "M&A Due Diligence, investigative Recherche.\n\n"
            "Insolvency radar: Combines insolvency proceedings, HR profile, "
            "Bundesanzeiger reports, and ZVG for a risk assessment."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "firma_name": {
                    "type": "string",
                    "description": "Firmenname (z.B. 'Wirecard AG', 'Mustermann GmbH')",
                },
            },
            "required": ["firma_name"],
        },
    ),
    Tool(
        name="wirtschafts_vernetzung",
        description=(
            "Wirtschaftliche Vernetzungsanalyse für eine Person: Kombiniert alle "
            "Handelsregister-Mandate, politische Spendenhistorie (Parteispenden) und "
            "Unternehmensverbindungen via Bundesanzeiger. "
            "Nützlich für: Lobbying-Recherche, Compliance, politische Verflechtungsanalyse, "
            "Hintergrundrecherche über Wirtschaftsakteure.\n\n"
            "Economic network analysis: HR mandates + party donations + Bundesanzeiger links for a person."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": "Name der Person (z.B. 'Friedrich Merz', 'Klaus Muster')",
                },
            },
            "required": ["name"],
        },
    ),
    Tool(
        name="region_radar",
        description=(
            "Regionales Lageradar für ein Bundesland: Kombiniert aktuelle Blaulicht-Meldungen "
            "(Sicherheitslage), Insolvenzbekanntmachungen (Wirtschaftslage), "
            "Zwangsversteigerungen (Immobilienmarkt) und Arbeitsmarktdaten. "
            "Nützlich für: Investigative Regionalrecherche, Risikoanalyse für Investitionen, "
            "Journalismus, politische Lageeinschätzung.\n\n"
            "Regional situation overview: safety (Blaulicht) + insolvencies + ZVG + labor market."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "bundesland": {
                    "type": "string",
                    "description": (
                        "Bundesland (z.B. 'Bayern', 'Nordrhein-Westfalen', 'Berlin'). "
                        "Für ZVG-Abfrage auch Kürzel möglich: 'by', 'nw', 'be', 'bw', 'he', "
                        "'ni', 'rp', 'sn', 'st', 'th', 'sl', 'sh', 'hb', 'hh', 'mv'"
                    ),
                },
            },
            "required": ["bundesland"],
        },
    ),
]

# ---------------------------------------------------------------------------
# Handler
# ---------------------------------------------------------------------------


async def handle_composite(name: str, arguments: dict) -> list[TextContent]:
    """Haupt-Dispatcher für alle Composite-Tools."""

    if name == "company_360":
        return await _company_360(arguments)
    elif name == "markt_radar":
        return await _markt_radar(arguments)
    elif name == "region_dashboard":
        return await _region_dashboard(arguments)
    elif name == "foerder_match":
        return await _foerder_match(arguments)
    elif name == "person_profil":
        return await _person_profil(arguments)
    elif name == "energie_trend":
        return await _energie_trend(arguments)
    elif name == "arbeitsmarkt_trend":
        return await _arbeitsmarkt_trend(arguments)
    elif name == "vergabe_trend":
        return await _vergabe_trend(arguments)
    elif name == "insolvenz_radar":
        return await _insolvenz_radar(arguments)
    elif name == "wirtschafts_vernetzung":
        return await _wirtschafts_vernetzung(arguments)
    elif name == "region_radar":
        return await _region_radar(arguments)

    return [TextContent(type="text", text=format_error(f"Unbekanntes Composite-Tool: {name}"))]


# ---------------------------------------------------------------------------
# Hilfsfunktionen
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


def _section(icon: str, title: str) -> str:
    return f"\n{icon} **{title}**\n{'─' * 40}"


# Bundesland-Name → ZVG-Kürzel
_BL_TO_ZVG: dict[str, str] = {
    "nordrhein-westfalen": "nw", "nrw": "nw",
    "bayern": "by",
    "baden-württemberg": "bw", "bw": "bw",
    "hessen": "he",
    "niedersachsen": "ni",
    "berlin": "be",
    "rheinland-pfalz": "rp",
    "sachsen": "sn",
    "sachsen-anhalt": "st",
    "thüringen": "th",
    "saarland": "sl",
    "schleswig-holstein": "sh",
    "hamburg": "hh",
    "bremen": "hb",
    "mecklenburg-vorpommern": "mv",
    "brandenburg": "br",
}


def _bundesland_to_zvg_abk(bundesland: str) -> str | None:
    """Konvertiert Bundesland-Namen in ZVG-Kürzel."""
    bl_lower = bundesland.lower().strip()
    # Direktes Kürzel?
    if bl_lower in _BL_TO_ZVG.values():
        return bl_lower
    return _BL_TO_ZVG.get(bl_lower)


# ---------------------------------------------------------------------------
# Implementierungen
# ---------------------------------------------------------------------------


async def _company_360(arguments: dict) -> list[TextContent]:
    """360°-Unternehmensprofil mit Insolvenz-Check, ZVG-Check und Jobs-Signal."""
    name = arguments["name"]
    city = arguments.get("city")

    hr_params = {"q": name, "size": 3}
    if city:
        hr_params["registered_office"] = city

    # Parallele Calls: HR + Bundesanzeiger + News + Insolvenz + ZVG
    jobs_source = _detect_jobs_source(name)
    tasks = [
        api_get("/v1/handelsregister/companies", params=hr_params),
        api_get("/v1/bundesanzeiger/search", params={"q": name, "size": 3}),
        api_get("/v1/news/articles", params={"q": name, "size": 5}),
        api_get("/v1/insolvenzen/search", params={"q": name, "nur_firmen": True, "size": 5}),
        api_get("/v1/zwangsversteigerungen/search", params={"q": name, "size": 5}),
    ]
    if jobs_source:
        tasks.append(api_get("/v1/jobs", params={"source": jobs_source, "size": 1}))

    results = await asyncio.gather(*tasks)
    hr_result, ba_result, news_result, insolvenz_result, zvg_result = results[:5]
    jobs_result = results[5] if jobs_source else None

    text = _format_company_360(
        name=name,
        hr=hr_result,
        ba=ba_result,
        news=news_result,
        insolvenz=insolvenz_result,
        zvg=zvg_result,
        jobs=jobs_result,
        jobs_source=jobs_source,
    )
    return [TextContent(type="text", text=text)]


def _format_company_360(
    name: str,
    hr: dict,
    ba: dict,
    news: dict,
    insolvenz: dict,
    zvg: dict,
    jobs: dict | None,
    jobs_source: str | None,
) -> str:
    lines = [f"🔭 **360° Unternehmensprofil: {name}**\n"]

    # --- Risiko-Signale (oben anzeigen wenn vorhanden) ---
    risk_lines: list[str] = []
    if insolvenz.get("ok"):
        insolvenz_total = insolvenz["data"].get("total", 0)
        if insolvenz_total > 0:
            risk_lines.append(f"  ⚠️ **Insolvenz-Verfahren gefunden** ({insolvenz_total} Einträge)")
    if zvg.get("ok"):
        zvg_total = zvg["data"].get("total", 0)
        if zvg_total > 0:
            risk_lines.append(f"  🏠 **Zwangsversteigerung gefunden** ({zvg_total} Objekte)")
    if jobs and jobs.get("ok"):
        jobs_count = jobs["data"].get("count", 0)
        if jobs_count > 0:
            src_label = (jobs_source or "").upper()
            risk_lines.append(f"  💼 **{jobs_count} aktuelle Stellen** ({src_label} Karriereseite)")

    if risk_lines:
        lines.append("🚦 **Signale:**")
        lines.extend(risk_lines)
        lines.append("")

    # --- Handelsregister ---
    lines.append(_section("🏢", "Handelsregister"))
    if not hr.get("ok"):
        lines.append(f"  ❌ {hr.get('error', 'Fehler')}")
    else:
        data = hr["data"]
        results = data.get("results", [])
        total = data.get("total", 0)
        if not results:
            lines.append("  Keine Einträge gefunden.")
        else:
            lines.append(f"  {total} Treffer:\n")
            for r in results:
                status = "✅" if r.get("current_status") == "currently registered" else "❌"
                lines.append(
                    f"  {status} **{_none(r.get('name'))}**\n"
                    f"     {_none(r.get('register_type'))} {_none(r.get('register_number'))} | "
                    f"{_none(r.get('registrar'))} | {_none(r.get('federal_state'))}\n"
                    f"     Sitz: {_none(r.get('registered_office'))} | Nr: {_none(r.get('company_number'))}"
                )

    # --- Bundesanzeiger ---
    lines.append(_section("📰", "Bundesanzeiger (Jahresabschlüsse)"))
    if not ba.get("ok"):
        lines.append(f"  ❌ {ba.get('error', 'Fehler')}")
    else:
        data = ba["data"]
        results = data.get("results", [])
        total = data.get("total", 0)
        if not results:
            lines.append("  Keine Jahresabschlüsse gefunden.")
        else:
            lines.append(f"  {total} Veröffentlichungen:\n")
            for r in results:
                fy = f"{_none(r.get('fiscal_year_start'))} – {_none(r.get('fiscal_year_end'))}"
                lines.append(
                    f"  • **{_none(r.get('company'))}** [{_none(r.get('legal_form'))}]\n"
                    f"    GJ {fy} | Veröffentlicht: {_none(r.get('publication_date'))} | ID: {_none(r.get('id'))}"
                )
                highlights = r.get("highlights", [])
                if highlights:
                    snippet = highlights[0].replace("<mark>", "«").replace("</mark>", "»")
                    lines.append(f"    💬 {_trunc(snippet, 200)}")

    # --- Insolvenz ---
    lines.append(_section("⚠️", "Insolvenz-Check"))
    if not insolvenz.get("ok"):
        lines.append(f"  ❌ {insolvenz.get('error', 'Fehler')}")
    else:
        data = insolvenz["data"]
        results = data.get("results", [])
        total = data.get("total", 0)
        if total == 0:
            lines.append("  ✅ Keine Insolvenzverfahren gefunden.")
        else:
            lines.append(f"  ⚠️ {total} Insolvenzverfahren gefunden:\n")
            for r in results[:3]:
                vollname = r.get("schuldner_name", "")
                lines.append(
                    f"  • **{vollname}** | {_none(r.get('gegenstand'))}\n"
                    f"    ⚖️ {_none(r.get('gericht'))} | Az: {_none(r.get('aktenzeichen'))} | "
                    f"📅 {_none(r.get('veroeffentlicht_am'))}"
                )

    # --- ZVG ---
    lines.append(_section("🏠", "Zwangsversteigerungen"))
    if not zvg.get("ok"):
        lines.append(f"  ❌ {zvg.get('error', 'Fehler')}")
    else:
        data = zvg["data"]
        results = data.get("results", [])
        total = data.get("total", 0)
        if total == 0:
            lines.append("  ✅ Keine Zwangsversteigerungen gefunden.")
        else:
            lines.append(f"  🏠 {total} Zwangsversteigerungen gefunden:\n")
            for r in results[:3]:
                vkw = r.get("verkehrswert")
                vkw_str = f"{vkw:,.0f} €" if vkw is not None else "k.A."
                lines.append(
                    f"  • **{_trunc(r.get('objekt_lage'), 80)}**\n"
                    f"    💶 {vkw_str} | Termin: {_none(r.get('termin_datum'))}"
                )

    # --- News ---
    lines.append(_section("📡", "Aktuelle Nachrichten"))
    if not news.get("ok"):
        lines.append(f"  ❌ {news.get('error', 'Fehler')}")
    else:
        data = news["data"]
        results = data.get("results", [])
        if not results:
            lines.append("  Keine aktuellen Nachrichten gefunden.")
        else:
            for r in results:
                lines.append(
                    f"  • **{_trunc(r.get('title'), 100)}**\n"
                    f"    🗞 {_none(r.get('feed'))} | {_none(r.get('pubtime'))}\n"
                    f"    🔗 {_none(r.get('url'))}"
                )

    return "\n".join(lines)


async def _markt_radar(arguments: dict) -> list[TextContent]:
    """Marktüberblick: Arbeitsmarkt + Facetten + Vergabe parallel."""
    beruf = arguments["beruf"]
    region = arguments.get("region")

    jobs_params = {"q": beruf, "size": 5}
    vergabe_params = {"q": beruf, "size": 5}
    if region:
        jobs_params["arbeitsort"] = region

    jobs_result, facets_result, vergabe_result = await asyncio.gather(
        api_get("/v1/arbeitsmarkt/jobs", params=jobs_params),
        api_get("/v1/arbeitsmarkt/facets"),
        api_get("/v1/vergabe/ausschreibungen", params=vergabe_params),
    )

    text = format_composite_markt_radar(
        beruf=beruf,
        region=region,
        jobs=jobs_result,
        facets=facets_result,
        vergabe=vergabe_result,
    )
    return [TextContent(type="text", text=text)]


async def _region_dashboard(arguments: dict) -> list[TextContent]:
    """Standortprofil: Energie + Luft + Arbeitsmarkt + Vergabe parallel."""
    bundesland = arguments["bundesland"]

    mastr_result, luft_result, am_result, vergabe_result = await asyncio.gather(
        api_get("/v1/energie/mastr/snapshot", params={"bundesland": bundesland}),
        api_get("/v1/luftqualitaet/stationen", params={"q": bundesland}),
        api_get("/v1/arbeitsmarkt/stats"),
        api_get("/v1/vergabe/stats"),
    )

    text = format_composite_region_dashboard(
        bundesland=bundesland,
        mastr=mastr_result,
        luft=luft_result,
        arbeitsmarkt=am_result,
        vergabe=vergabe_result,
    )
    return [TextContent(type="text", text=text)]


async def _foerder_match(arguments: dict) -> list[TextContent]:
    """Förderprogramm-Matching: Sucht passende Programme."""
    beschreibung = arguments["beschreibung"]
    rechtsform = arguments.get("rechtsform")
    unternehmensgroesse = arguments.get("unternehmensgroesse")

    params = {"q": beschreibung, "size": 10}

    result = await api_get("/v1/foerderung/programme", params=params)

    text = format_composite_foerder_match(
        beschreibung=beschreibung,
        rechtsform=rechtsform,
        unternehmensgroesse=unternehmensgroesse,
        foerderung=result,
    )
    return [TextContent(type="text", text=text)]


async def _person_profil(arguments: dict) -> list[TextContent]:
    """Personenprofil: Mandate + Firma-Details + News + Parteispenden."""
    name = arguments["name"]

    # Erster Call: Officers + Parteispenden parallel
    officers_result, parteispenden_result = await asyncio.gather(
        api_get("/v1/handelsregister/officers", params={"q": name, "size": 10}),
        api_get("/v1/parteispenden/spenden", params={"spender": name, "size": 5}),
    )

    # Parallel: Company-Details (max 3) + News
    company_tasks = []
    if officers_result["ok"]:
        officers = officers_result["data"].get("results", [])
        seen: set = set()
        for o in officers:
            cn = o.get("company_number")
            if cn and cn not in seen:
                seen.add(cn)
                company_tasks.append(api_get(f"/v1/handelsregister/companies/{cn}"))
                if len(company_tasks) >= 3:
                    break

    news_task = api_get("/v1/news/articles", params={"q": name, "size": 5})

    if company_tasks:
        results = await asyncio.gather(*company_tasks, news_task)
        companies = list(results[:-1])
        news_result = results[-1]
    else:
        news_result = await news_task
        companies = []

    text = _format_person_profil(
        name=name,
        officers=officers_result,
        companies=companies,
        news=news_result,
        parteispenden=parteispenden_result,
    )
    return [TextContent(type="text", text=text)]


def _format_person_profil(
    name: str,
    officers: dict,
    companies: list,
    news: dict,
    parteispenden: dict,
) -> str:
    lines = [f"🔍 **Personenprofil: {name}**\n"]

    # Parteispenden-Signal oben
    if parteispenden.get("ok"):
        ps_total = parteispenden["data"].get("total", 0)
        if ps_total > 0:
            lines.append(f"💰 **Parteispende gefunden** ({ps_total} Einträge)\n")

    # --- Mandate ---
    lines.append(_section("📋", "Handelsregister-Mandate"))
    if not officers.get("ok"):
        lines.append(f"  ❌ {officers.get('error', 'Fehler')}")
    else:
        data = officers["data"]
        results = data.get("results", [])
        total = data.get("total", 0)
        if not results:
            lines.append("  Keine Mandate im Handelsregister gefunden.")
        else:
            lines.append(f"  {total} Einträge:\n")
            for r in results[:10]:
                dismissed = " [abberufen]" if r.get("dismissed") else " [aktiv]"
                lines.append(
                    f"  • **{_none(r.get('name'))}** — {_none(r.get('position'))}{dismissed}\n"
                    f"    🏢 {_none(r.get('company_name'))} ({_none(r.get('company_number'))})\n"
                    f"    📅 {_none(r.get('start_date'))} – {_none(r.get('end_date'))}"
                )

    # --- Unternehmensprofil ---
    if companies:
        lines.append(_section("🏢", "Verknüpfte Unternehmen (Details)"))
        for i, co_result in enumerate(companies, 1):
            if not co_result.get("ok"):
                lines.append(f"  Firma {i}: ❌ {co_result.get('error', 'Fehler')}")
                continue
            c = co_result["data"].get("company", {}) or {}
            status = "✅" if c.get("current_status") == "currently registered" else "❌"
            lines.append(
                f"  {i}. {status} **{_none(c.get('name'))}**\n"
                f"     {_none(c.get('register_type'))} {_none(c.get('register_number'))} | "
                f"{_none(c.get('registrar'))} | Sitz: {_none(c.get('registered_office'))}"
            )

    # --- Parteispenden ---
    lines.append(_section("💰", "Parteispenden"))
    if not parteispenden.get("ok"):
        lines.append(f"  ❌ {parteispenden.get('error', 'Fehler')}")
    else:
        data = parteispenden["data"]
        results = data.get("results", [])
        total = data.get("total", 0)
        if total == 0:
            lines.append("  Keine Parteispenden gefunden.")
        else:
            lines.append(f"  {total} Spende(n) gefunden:\n")
            for r in results:
                betrag = r.get("betrag")
                betrag_str = f"{betrag:,.0f} €" if betrag is not None else "–"
                lines.append(
                    f"  • **{_none(r.get('spender_name'))}** → {_none(r.get('partei'))}\n"
                    f"    💶 {betrag_str} | 📅 {_none(r.get('datum_spende'))}"
                )

    # --- Nachrichten ---
    lines.append(_section("📡", "Aktuelle Nachrichten"))
    if not news.get("ok"):
        lines.append(f"  ❌ {news.get('error', 'Fehler')}")
    else:
        data = news["data"]
        results = data.get("results", [])
        if not results:
            lines.append("  Keine Nachrichten gefunden.")
        else:
            for r in results:
                lines.append(
                    f"  • **{_trunc(r.get('title'), 100)}**\n"
                    f"    🗞 {_none(r.get('feed'))} | {_none(r.get('pubtime'))}\n"
                    f"    🔗 {_none(r.get('url'))}"
                )

    return "\n".join(lines)


async def _energie_trend(arguments: dict) -> list[TextContent]:
    """Energie-Trend: SMARD + MaStR kombiniert."""
    days = arguments.get("days", 30)

    smard_result, mastr_result = await asyncio.gather(
        api_get(
            "/v1/energie/timeseries",
            params={"filter_id": 410100, "limit": min(days, 100)},
        ),
        api_get("/v1/energie/mastr/totals", params={"limit": min(days, 50)}),
    )

    text = format_composite_energie_trend(days=days, smard=smard_result, mastr=mastr_result)
    return [TextContent(type="text", text=text)]


async def _arbeitsmarkt_trend(arguments: dict) -> list[TextContent]:
    """Arbeitsmarkt-Trend mit Highlights."""
    days = arguments.get("days", 90)
    result = await api_get("/v1/arbeitsmarkt/stats", params={"days": days})
    text = format_composite_arbeitsmarkt_trend(days=days, stats=result)
    return [TextContent(type="text", text=text)]


async def _vergabe_trend(arguments: dict) -> list[TextContent]:
    """Vergabe-Trend: Ausschreibungen + Stats kombiniert."""
    days = arguments.get("days", 30)
    q = arguments.get("q")

    params: dict = {"size": 50}
    if q:
        params["q"] = q

    ausschreibungen_result, stats_result = await asyncio.gather(
        api_get("/v1/vergabe/ausschreibungen", params=params),
        api_get("/v1/vergabe/stats"),
    )

    text = format_composite_vergabe_trend(
        days=days, q=q, ausschreibungen=ausschreibungen_result, stats=stats_result
    )
    return [TextContent(type="text", text=text)]


# ---------------------------------------------------------------------------
# Neue Composite-Tools (v0.2.0)
# ---------------------------------------------------------------------------


async def _insolvenz_radar(arguments: dict) -> list[TextContent]:
    """Insolvenz-Radar: Insolvenz + HR + Bundesanzeiger + ZVG für Risiko-Assessment."""
    firma_name = arguments["firma_name"]

    insolvenz_result, hr_result, ba_result, zvg_result = await asyncio.gather(
        api_get("/v1/insolvenzen/search", params={"q": firma_name, "nur_firmen": True, "size": 10}),
        api_get("/v1/handelsregister/companies", params={"q": firma_name, "size": 3}),
        api_get("/v1/bundesanzeiger/search", params={"q": firma_name, "size": 3}),
        api_get("/v1/zwangsversteigerungen/search", params={"q": firma_name, "size": 5}),
    )

    lines = [f"🚨 **Insolvenz-Radar: {firma_name}**\n"]

    # --- Risiko-Assessment ---
    risiko_score = 0
    risiko_items: list[str] = []

    if insolvenz_result.get("ok"):
        total = insolvenz_result["data"].get("total", 0)
        if total > 0:
            risiko_score += 3
            risiko_items.append(f"⚠️ {total} Insolvenzverfahren gefunden (HOHES RISIKO)")
    if zvg_result.get("ok"):
        total = zvg_result["data"].get("total", 0)
        if total > 0:
            risiko_score += 2
            risiko_items.append(f"🏠 {total} Zwangsversteigerungen (MITTLERES RISIKO)")
    if hr_result.get("ok"):
        hr_results = hr_result["data"].get("results", [])
        deleted = [r for r in hr_results if r.get("current_status") != "currently registered"]
        if deleted:
            risiko_score += 1
            risiko_items.append(f"❌ {len(deleted)} gelöschte HR-Einträge gefunden")

    if risiko_score == 0:
        lines.append("✅ **Risiko-Assessment: UNAUFFÄLLIG**\nKeine Insolvenzverfahren oder ZVG-Treffer.\n")
    elif risiko_score <= 2:
        lines.append(f"🟡 **Risiko-Assessment: ERHÖHT** (Score: {risiko_score}/5)")
        for item in risiko_items:
            lines.append(f"  {item}")
        lines.append("")
    else:
        lines.append(f"🔴 **Risiko-Assessment: KRITISCH** (Score: {risiko_score}/5)")
        for item in risiko_items:
            lines.append(f"  {item}")
        lines.append("")

    # --- Insolvenzverfahren ---
    lines.append(_section("⚠️", "Insolvenzverfahren"))
    if not insolvenz_result.get("ok"):
        lines.append(f"  ❌ {insolvenz_result.get('error', 'Fehler')}")
    else:
        results = insolvenz_result["data"].get("results", [])
        total = insolvenz_result["data"].get("total", 0)
        if total == 0:
            lines.append("  Keine Verfahren gefunden.")
        else:
            for r in results:
                lines.append(
                    f"  • **{_none(r.get('schuldner_name'))}** — {_none(r.get('gegenstand'))}\n"
                    f"    ⚖️ {_none(r.get('gericht'))} | Az: {_none(r.get('aktenzeichen'))} | "
                    f"📅 {_none(r.get('veroeffentlicht_am'))}\n"
                    f"    Register: {_none(r.get('register_art'))} {_none(r.get('register_nr'))}"
                )

    # --- Handelsregister ---
    lines.append(_section("🏢", "Handelsregister"))
    if not hr_result.get("ok"):
        lines.append(f"  ❌ {hr_result.get('error', 'Fehler')}")
    else:
        results = hr_result["data"].get("results", [])
        if not results:
            lines.append("  Kein HR-Eintrag gefunden.")
        else:
            for r in results:
                status = "✅ aktiv" if r.get("current_status") == "currently registered" else "❌ gelöscht"
                lines.append(
                    f"  [{status}] **{_none(r.get('name'))}**\n"
                    f"    {_none(r.get('register_type'))} {_none(r.get('register_number'))} | "
                    f"{_none(r.get('registrar'))} | {_none(r.get('registered_office'))}"
                )

    # --- Bundesanzeiger ---
    lines.append(_section("📰", "Bundesanzeiger (Jahresabschlüsse)"))
    if not ba_result.get("ok"):
        lines.append(f"  ❌ {ba_result.get('error', 'Fehler')}")
    else:
        results = ba_result["data"].get("results", [])
        total = ba_result["data"].get("total", 0)
        if not results:
            lines.append("  Keine Jahresabschlüsse gefunden.")
        else:
            lines.append(f"  {total} Veröffentlichungen:")
            for r in results:
                lines.append(
                    f"  • {_none(r.get('company'))} | GJ: {_none(r.get('fiscal_year_end'))} | "
                    f"📅 {_none(r.get('publication_date'))}"
                )

    # --- ZVG ---
    lines.append(_section("🏠", "Zwangsversteigerungen"))
    if not zvg_result.get("ok"):
        lines.append(f"  ❌ {zvg_result.get('error', 'Fehler')}")
    else:
        results = zvg_result["data"].get("results", [])
        total = zvg_result["data"].get("total", 0)
        if total == 0:
            lines.append("  Keine Zwangsversteigerungen gefunden.")
        else:
            for r in results[:3]:
                vkw = r.get("verkehrswert")
                vkw_str = f"{vkw:,.0f} €" if vkw is not None else "k.A."
                lines.append(
                    f"  • {_trunc(r.get('objekt_lage'), 80)} | 💶 {vkw_str} | "
                    f"Termin: {_none(r.get('termin_datum'))}"
                )

    return [TextContent(type="text", text="\n".join(lines))]


async def _wirtschafts_vernetzung(arguments: dict) -> list[TextContent]:
    """Wirtschaftliche Vernetzung: HR-Mandate + Parteispenden + Bundesanzeiger."""
    name = arguments["name"]

    officers_result, parteispenden_result, ba_result = await asyncio.gather(
        api_get("/v1/handelsregister/officers", params={"q": name, "size": 20}),
        api_get("/v1/parteispenden/spenden", params={"spender": name, "size": 10}),
        api_get("/v1/bundesanzeiger/search", params={"q": name, "size": 5}),
    )

    lines = [f"🕸 **Wirtschaftliche Vernetzung: {name}**\n"]

    # --- Zusammenfassung ---
    mandats_count = 0
    spenden_summe = 0.0
    spenden_count = 0
    ba_count = 0

    if officers_result.get("ok"):
        mandats_count = officers_result["data"].get("total", 0)
    if parteispenden_result.get("ok"):
        ps_results = parteispenden_result["data"].get("results", [])
        spenden_count = parteispenden_result["data"].get("total", 0)
        spenden_summe = sum(r.get("betrag", 0) or 0 for r in ps_results)
    if ba_result.get("ok"):
        ba_count = ba_result["data"].get("total", 0)

    lines.append("📊 **Zusammenfassung:**")
    lines.append(f"  📋 HR-Mandate: {mandats_count}")
    lines.append(f"  💰 Parteispenden: {spenden_count} Einträge ({spenden_summe:,.0f} € gesamt)")
    lines.append(f"  📰 Bundesanzeiger: {ba_count} Treffer")
    lines.append("")

    # --- HR-Mandate ---
    lines.append(_section("📋", "Handelsregister-Mandate"))
    if not officers_result.get("ok"):
        lines.append(f"  ❌ {officers_result.get('error', 'Fehler')}")
    else:
        results = officers_result["data"].get("results", [])
        if not results:
            lines.append("  Keine Mandate gefunden.")
        else:
            aktiv = [r for r in results if not r.get("dismissed")]
            abberufen = [r for r in results if r.get("dismissed")]
            if aktiv:
                lines.append(f"  **Aktive Mandate ({len(aktiv)}):**")
                for r in aktiv:
                    lines.append(
                        f"  • {_none(r.get('position'))} @ **{_none(r.get('company_name'))}** "
                        f"({_none(r.get('company_number'))}) | ab {_none(r.get('start_date'))}"
                    )
            if abberufen:
                lines.append(f"\n  **Frühere Mandate ({len(abberufen)}):**")
                for r in abberufen[:5]:
                    lines.append(
                        f"  • {_none(r.get('position'))} @ {_none(r.get('company_name'))} "
                        f"({_none(r.get('start_date'))} – {_none(r.get('end_date'))})"
                    )

    # --- Parteispenden ---
    lines.append(_section("💰", "Politische Spendenhistorie"))
    if not parteispenden_result.get("ok"):
        lines.append(f"  ❌ {parteispenden_result.get('error', 'Fehler')}")
    else:
        results = parteispenden_result["data"].get("results", [])
        total = parteispenden_result["data"].get("total", 0)
        if total == 0:
            lines.append("  Keine Parteispenden gefunden.")
        else:
            lines.append(f"  {total} Spende(n):\n")
            for r in results:
                betrag = r.get("betrag")
                betrag_str = f"{betrag:,.0f} €" if betrag is not None else "–"
                lines.append(
                    f"  • {_none(r.get('datum_spende'))} | {_none(r.get('partei'))} | {betrag_str}"
                )

    # --- Bundesanzeiger ---
    lines.append(_section("📰", "Unternehmensverbindungen (Bundesanzeiger)"))
    if not ba_result.get("ok"):
        lines.append(f"  ❌ {ba_result.get('error', 'Fehler')}")
    else:
        results = ba_result["data"].get("results", [])
        total = ba_result["data"].get("total", 0)
        if not results:
            lines.append("  Keine Bundesanzeiger-Einträge gefunden.")
        else:
            lines.append(f"  {total} Veröffentlichungen:")
            for r in results:
                lines.append(
                    f"  • **{_none(r.get('company'))}** [{_none(r.get('legal_form'))}] | "
                    f"📍 {_none(r.get('city'))} | GJ-Ende: {_none(r.get('fiscal_year_end'))}"
                )

    return [TextContent(type="text", text="\n".join(lines))]


async def _region_radar(arguments: dict) -> list[TextContent]:
    """Regionaler Lageradar: Blaulicht + Insolvenzen + ZVG + Arbeitsmarkt."""
    bundesland = arguments["bundesland"]
    zvg_abk = _bundesland_to_zvg_abk(bundesland)

    blaulicht_result, insolvenz_result, am_result = await asyncio.gather(
        api_get("/v1/blaulicht/meldungen", params={"bundesland": bundesland, "limit": 10}),
        api_get("/v1/insolvenzen/bekanntmachungen", params={"gericht": bundesland, "limit": 10}),
        api_get("/v1/arbeitsmarkt/stats"),
    )

    zvg_result = await api_get(
        "/v1/zwangsversteigerungen/liste",
        params={"land_abk": zvg_abk, "limit": 10} if zvg_abk else {"limit": 0},
    )

    lines = [f"🗺 **Region-Radar: {bundesland}**\n"]

    # --- Blaulicht ---
    lines.append(_section("🚨", "Aktuelle Sicherheitslage (Blaulicht)"))
    if not blaulicht_result.get("ok"):
        lines.append(f"  ❌ {blaulicht_result.get('error', 'Fehler')}")
    else:
        results = blaulicht_result["data"].get("results", [])
        total = blaulicht_result["data"].get("total", 0)
        if not results:
            lines.append(f"  Keine aktuellen Meldungen für {bundesland}.")
        else:
            # Zähle nach Kategorie
            cats: dict[str, int] = {}
            for r in results:
                cat = r.get("category", "sonstige")
                cats[cat] = cats.get(cat, 0) + 1
            cat_summary = " | ".join(f"{k}: {v}" for k, v in cats.items())
            lines.append(f"  {total} Meldungen gesamt ({cat_summary}):\n")
            for r in results[:5]:
                cat_icon = {"polizei": "👮", "feuerwehr": "🚒", "rettungsdienst": "🚑"}.get(
                    r.get("category", ""), "🔵"
                )
                lines.append(
                    f"  {cat_icon} {_trunc(r.get('title'), 80)} "
                    f"[{_none(r.get('published_at', ''))[:16]}]"
                )

    # --- Insolvenzen ---
    lines.append(_section("⚠️", "Aktuelle Insolvenzen"))
    if not insolvenz_result.get("ok"):
        lines.append(f"  ❌ {insolvenz_result.get('error', 'Fehler')}")
    else:
        results = insolvenz_result["data"].get("results", [])
        total = insolvenz_result["data"].get("total", 0)
        if not results:
            lines.append(f"  Keine aktuellen Insolvenzen für {bundesland}.")
        else:
            lines.append(f"  {total} Bekanntmachungen:\n")
            for r in results[:5]:
                vollname = r.get("schuldner_name", "")
                is_firma = bool(r.get("register_art"))
                icon = "🏢" if is_firma else "👤"
                lines.append(
                    f"  {icon} **{vollname}** | {_none(r.get('gegenstand'))} | "
                    f"📅 {_none(r.get('veroeffentlicht_am'))}"
                )

    # --- ZVG ---
    lines.append(_section("🏠", "Zwangsversteigerungen"))
    if not zvg_result.get("ok"):
        if zvg_abk:
            lines.append(f"  ❌ {zvg_result.get('error', 'Fehler')}")
        else:
            lines.append(f"  ⚠️ Kein ZVG-Kürzel für '{bundesland}' bekannt.")
    else:
        results = zvg_result["data"].get("results", [])
        total = zvg_result["data"].get("total", 0)
        if not results:
            lines.append(f"  Keine ZVG-Termine für {bundesland}.")
        else:
            lines.append(f"  {total} Objekte (Kürzel: {zvg_abk}):\n")
            for r in results[:5]:
                vkw = r.get("verkehrswert")
                vkw_str = f"{vkw:,.0f} €" if vkw is not None else "k.A."
                lines.append(
                    f"  🏠 {_trunc(r.get('objekt_lage'), 70)} | 💶 {vkw_str} | "
                    f"Termin: {_none(r.get('termin_datum'))}"
                )

    # --- Arbeitsmarkt ---
    lines.append(_section("💼", "Arbeitsmarkt (bundesweit aktuell)"))
    if not am_result.get("ok"):
        lines.append(f"  ❌ {am_result.get('error', 'Fehler')}")
    else:
        timeline = am_result["data"].get("timeline", [])
        if timeline:
            latest = timeline[0]
            lines.append(
                f"  Stand: {_none(latest.get('snapshot_date'))}\n"
                f"  Stellenangebote gesamt: {latest.get('total_jobs', 0):,}\n"
                f"  Neu: +{latest.get('new_jobs', 0):,} | Entfernt: -{latest.get('removed_jobs', 0):,}"
            )
        else:
            lines.append("  Keine Arbeitsmarktdaten verfügbar.")

    lines.append(
        "\n\n💡 *Tipp: Für vertiefte Recherche: `blaulicht_suche`, `insolvenzen_suche`, `zvg_suche`*"
    )

    return [TextContent(type="text", text="\n".join(lines))]
