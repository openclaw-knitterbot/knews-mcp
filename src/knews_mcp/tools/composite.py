"""
Cross-Domain Composite Tools für die knews Datenplattform.

Diese Tools kombinieren mehrere API-Endpunkte parallel via asyncio.gather()
und liefern ein integriertes Gesamtbild — der eigentliche USP von knews-mcp.

Enthaltene Tools:
  - company_360       : Handelsregister + Bundesanzeiger + News zu einer Firma
  - markt_radar       : Arbeitsmarkt + Jobs + Vergabe für ein Berufsfeld
  - region_dashboard  : Energie + Luft + Arbeitsmarkt + Vergabe für ein Bundesland
  - foerder_match     : Passende Förderprogramme für ein Projekt
  - person_profil     : Mandate + verbundene Firmen + News zu einer Person

  - energie_trend     : SMARD-Erzeugung + MaStR-Zubau kombiniert
  - arbeitsmarkt_trend: Zeitreihe Arbeitsmarkt mit Highlights
  - vergabe_trend     : Ausschreibungsvolumen im Zeitverlauf
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
# Tool-Definitionen
# ---------------------------------------------------------------------------

COMPOSITE_TOOLS = [
    Tool(
        name="company_360",
        description=(
            "360°-Unternehmensprofil: Kombiniert Handelsregister, Bundesanzeiger-Jahresabschlüsse "
            "und aktuelle Nachrichtenartikel zu einer Firma in einem einzigen Überblick. "
            "Nützlich für: Due Diligence, Unternehmensanalyse, Journalismus-Recherche.\n\n"
            "360° company profile: Combines Handelsregister, Bundesanzeiger reports, and news articles."
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
            "Personenprofil: Recherchiert alle Handelsregister-Mandate einer Person "
            "und verknüpft sie mit Firmendaten und aktuellen Nachrichtenartikeln. "
            "Nützlich für: Verflechtungsanalyse, Hintergrundrecherche, Compliance-Prüfung.\n\n"
            "Person profile: Find all company mandates, related firms, and news mentions for a person."
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

    return [TextContent(type="text", text=format_error(f"Unbekanntes Composite-Tool: {name}"))]


# ---------------------------------------------------------------------------
# Implementierungen
# ---------------------------------------------------------------------------


async def _company_360(arguments: dict) -> list[TextContent]:
    """360°-Unternehmensprofil via parallele API-Calls."""
    name = arguments["name"]
    city = arguments.get("city")

    hr_params = {"q": name, "size": 3}
    if city:
        hr_params["registered_office"] = city

    # Parallele Calls mit asyncio.gather
    hr_result, ba_result, news_result = await asyncio.gather(
        api_get("/v1/handelsregister/companies", params=hr_params),
        api_get("/v1/bundesanzeiger/search", params={"q": name, "size": 3}),
        api_get("/v1/news/articles", params={"q": name, "size": 5}),
    )

    text = format_composite_company_360(
        name=name,
        hr=hr_result,
        ba=ba_result,
        news=news_result,
    )
    return [TextContent(type="text", text=text)]


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
    """Personenprofil: Mandate + Firma-Details + News."""
    name = arguments["name"]

    # Erster Call: Officers suchen
    officers_result = await api_get(
        "/v1/handelsregister/officers",
        params={"q": name, "size": 10},
    )

    # Parallel: Company-Details (max 3) + News
    company_tasks = []
    if officers_result["ok"]:
        officers = officers_result["data"].get("results", [])
        # Eindeutige company_numbers sammeln (max 3)
        seen: set = set()
        for o in officers:
            cn = o.get("company_number")
            if cn and cn not in seen:
                seen.add(cn)
                company_tasks.append(
                    api_get(f"/v1/handelsregister/companies/{cn}")
                )
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

    text = format_composite_person_profil(
        name=name,
        officers=officers_result,
        companies=companies,
        news=news_result,
    )
    return [TextContent(type="text", text=text)]


async def _energie_trend(arguments: dict) -> list[TextContent]:
    """Energie-Trend: SMARD + MaStR kombiniert."""
    days = arguments.get("days", 30)

    # filter_id 410100 = Realisierte Erzeugung Gesamt (SMARD)
    smard_result, mastr_result = await asyncio.gather(
        api_get(
            "/v1/energie/timeseries",
            params={"filter_id": 410100, "limit": min(days, 100)},
        ),
        api_get("/v1/energie/mastr/totals", params={"limit": min(days, 50)}),
    )

    text = format_composite_energie_trend(
        days=days,
        smard=smard_result,
        mastr=mastr_result,
    )
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
        days=days,
        q=q,
        ausschreibungen=ausschreibungen_result,
        stats=stats_result,
    )
    return [TextContent(type="text", text=text)]
