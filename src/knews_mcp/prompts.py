"""
MCP Prompts für die knews Datenplattform.

Stellt vorgefertigte, parametrisierte Analyse-Templates bereit:
- unternehmenscheck   — 360°-Unternehmenscheck
- branchenanalyse     — Branchenüberblick: Arbeitsmarkt, Förderung, Vergabe
- politikfeld_briefing — Politikfeld: Bundestag, Vergabe, Förderung
- standort_profil     — Standort: Energie, Luftqualität, Arbeitsmarkt
- foerder_finder      — Passende Förderprogramme finden

Registrierung: register_prompts(server) in server.py aufrufen.
"""

from mcp.server import Server
from mcp.types import (
    GetPromptResult,
    Prompt,
    PromptArgument,
    PromptMessage,
    TextContent,
)


# ---------------------------------------------------------------------------
# Prompt-Definitionen
# ---------------------------------------------------------------------------

ALL_PROMPTS: list[Prompt] = [
    Prompt(
        name="unternehmenscheck",
        description="360°-Check eines Unternehmens: Handelsregister, Bundesanzeiger, News",
        arguments=[
            PromptArgument(
                name="company_name",
                description="Name des Unternehmens (z.B. 'Siemens AG' oder 'Volkswagen')",
                required=True,
            )
        ],
    ),
    Prompt(
        name="branchenanalyse",
        description="Branchenanalyse: Arbeitsmarkt, Förderung, Vergabe",
        arguments=[
            PromptArgument(
                name="branche",
                description="Branche oder Berufsfeld (z.B. 'Automobilindustrie', 'Software', 'Pflege')",
                required=True,
            )
        ],
    ),
    Prompt(
        name="politikfeld_briefing",
        description="Politikfeld-Briefing: Bundestag-Aktivität, Vergabe, Förderung",
        arguments=[
            PromptArgument(
                name="thema",
                description="Politikfeld oder Thema (z.B. 'Klimaschutz', 'Digitalisierung', 'Rente')",
                required=True,
            )
        ],
    ),
    Prompt(
        name="standort_profil",
        description="Standortprofil: Energie, Luftqualität, Arbeitsmarkt für ein Bundesland",
        arguments=[
            PromptArgument(
                name="bundesland",
                description="Bundesland (z.B. 'Bayern', 'NRW', 'Brandenburg')",
                required=True,
            )
        ],
    ),
    Prompt(
        name="foerder_finder",
        description="Passende Förderprogramme für ein Vorhaben finden",
        arguments=[
            PromptArgument(
                name="beschreibung",
                description="Kurzbeschreibung des Vorhabens oder Unternehmens (z.B. 'Startup im Bereich erneuerbare Energien, Bayern, 5 Mitarbeiter')",
                required=True,
            )
        ],
    ),
]


# ---------------------------------------------------------------------------
# Prompt-Inhalte
# ---------------------------------------------------------------------------

def _prompt_unternehmenscheck(company_name: str) -> GetPromptResult:
    """
    360°-Check: Handelsregister + Bundesanzeiger + News kombinieren.
    """
    text = f"""Du bist ein Wirtschaftsanalyst. Erstelle einen umfassenden 360°-Check für das Unternehmen **{company_name}**.

Führe dazu folgende Schritte nacheinander aus:

1. **Handelsregister-Suche**: Rufe `handelsregister_search_companies` mit dem Suchbegriff "{company_name}" auf.
   - Notiere Rechtsform, Sitz, Registernummer und Status (aktiv/gelöscht)
   - Wenn ein Treffer gefunden, rufe `handelsregister_company_officers` mit der company_number auf, um Geschäftsführer und Aufsichtsräte zu sehen

2. **Bundesanzeiger-Recherche**: Rufe `bundesanzeiger_search` mit "{company_name}" auf.
   - Suche nach Jahresabschlüssen und Bilanzdaten
   - Falls eine ID verfügbar, rufe `bundesanzeiger_get_report` auf für Bilanz und GuV

3. **News-Recherche**: Rufe `news_search_articles` mit "{company_name}" auf.
   - Sammle aktuelle Berichte, Meldungen und Ereignisse
   - Achte auf Datum und Quelle der Artikel

4. **Gesamtbild erstellen**: Fasse alle Erkenntnisse zusammen in folgender Struktur:
   - **Unternehmensprofil**: Rechtsform, Sitz, Register, Status
   - **Führungsebene**: Aktuelle Geschäftsführer/Vorstände
   - **Finanzlage**: Letzte verfügbare Bilanzdaten (Bilanzsumme, Umsatz, Eigenkapital)
   - **Aktuelle Nachrichten**: Wichtigste Meldungen der letzten Zeit
   - **Bewertung**: Kurze Einschätzung der Unternehmenssituation

Starte jetzt mit Schritt 1."""
    return GetPromptResult(
        description=f"360°-Unternehmenscheck für: {company_name}",
        messages=[
            PromptMessage(
                role="user",
                content=TextContent(type="text", text=text),
            )
        ],
    )


def _prompt_branchenanalyse(branche: str) -> GetPromptResult:
    """
    Branchenanalyse: Arbeitsmarkt + Förderung + Vergabe.
    """
    text = f"""Du bist ein Wirtschafts- und Arbeitsmarktanalyst. Erstelle eine Branchenanalyse für **{branche}**.

Führe dazu folgende Schritte nacheinander aus:

1. **Aktuelle Stellenangebote**: Rufe `arbeitsmarkt_jobs` mit dem Suchbegriff "{branche}" auf.
   - Wie viele offene Stellen gibt es?
   - Welche Qualifikationen und Berufsbilder sind gefragt?
   - In welchen Regionen konzentrieren sich die Stellen?

2. **Arbeitsmarkt-Facetten**: Rufe `arbeitsmarkt_facets` mit "{branche}" auf (falls Branchenfilter möglich).
   - Analyse nach Regionen, Berufsgruppen und Arbeitgebertypen

3. **Fördermöglichkeiten**: Rufe `foerderung_list_programme` mit dem Suchbegriff "{branche}" auf.
   - Welche staatlichen Förderprogramme gibt es für diese Branche?
   - Wer ist förderberechtigt (KMU, Startups, Forschungseinrichtungen)?

4. **Öffentliche Vergabe**: Rufe `vergabe_ausschreibungen` mit "{branche}" als Suchbegriff auf.
   - Welche öffentlichen Aufträge werden ausgeschrieben?
   - Wie groß ist das Auftragsvolumen im öffentlichen Bereich?

5. **Branchenreport**: Fasse alle Erkenntnisse zusammen:
   - **Arbeitsmarktsituation**: Nachfrage, Schwerpunkte, regionale Verteilung
   - **Qualifikationsbedarf**: Gefragte Fähigkeiten und Berufsbilder
   - **Öffentliche Förderung**: Relevante Programme und Konditionen
   - **Öffentliche Aufträge**: Ausschreibungsvolumen und Auftraggeber
   - **Gesamteinschätzung**: Branchentrends und Perspektiven

Starte jetzt mit Schritt 1."""
    return GetPromptResult(
        description=f"Branchenanalyse für: {branche}",
        messages=[
            PromptMessage(
                role="user",
                content=TextContent(type="text", text=text),
            )
        ],
    )


def _prompt_politikfeld_briefing(thema: str) -> GetPromptResult:
    """
    Politikfeld-Briefing: Bundestag + Vergabe + Förderung.
    """
    text = f"""Du bist ein politischer Analyst. Erstelle ein Politikfeld-Briefing zum Thema **{thema}**.

Führe dazu folgende Schritte nacheinander aus:

1. **Bundestag-Aktivität**: Rufe `bundestag_list_drucksachen` auf mit "{thema}" als Suchbegriff.
   - Welche Anfragen, Anträge und Gesetzentwürfe gibt es?
   - Von welchen Fraktionen/Parteien kommen die Initiativen?
   - Was sind die aktuellsten parlamentarischen Aktivitäten?

2. **Öffentliche Vergabe**: Rufe `vergabe_ausschreibungen` mit "{thema}" auf.
   - Welche öffentlichen Aufträge werden im Bereich {thema} vergeben?
   - Welche Behörden und Ministerien schreiben aus?
   - Was sagen die Ausschreibungen über politische Prioritäten aus?

3. **Förderpolitik**: Rufe `foerderung_list_programme` mit "{thema}" auf.
   - Welche staatlichen Förderprogramme gibt es für dieses Politikfeld?
   - Welche Fördersummen und Zielgruppen gibt es?

4. **Politikfeld-Briefing**: Erstelle eine strukturierte Zusammenfassung:
   - **Parlamentarische Lage**: Aktuelle Initiativen, Anträge, Debatten
   - **Regierungshandeln**: Ausschreibungen und Mittelverwendung
   - **Förderinstrumente**: Bestehende Programme und Zielgruppen
   - **Politische Prioritäten**: Was lässt sich aus den Daten ableiten?
   - **Ausblick**: Zu erwartende Entwicklungen und offene Fragen

Starte jetzt mit Schritt 1."""
    return GetPromptResult(
        description=f"Politikfeld-Briefing zu: {thema}",
        messages=[
            PromptMessage(
                role="user",
                content=TextContent(type="text", text=text),
            )
        ],
    )


def _prompt_standort_profil(bundesland: str) -> GetPromptResult:
    """
    Standortprofil: Energie + Luftqualität + Arbeitsmarkt für ein Bundesland.
    """
    text = f"""Du bist ein Regionalanalyst. Erstelle ein Standortprofil für das Bundesland **{bundesland}**.

Führe dazu folgende Schritte nacheinander aus:

1. **Energieinfrastruktur**: Rufe `energie_mastr_snapshot` auf mit "{bundesland}" als Bundesland-Filter (falls verfügbar).
   - Welche Energieanlagen gibt es (Wind, Solar, Biomasse, ...)?
   - Wie groß ist die installierte Kapazität?
   - Wie ist die Energieversorgung strukturiert?

2. **Luftqualität**: Rufe `luftqualitaet_stationen` auf mit "{bundesland}" als Filter.
   - Welche Messstationen gibt es?
   - Falls Messstationen gefunden: Hole aktuelle Messwerte über `luftqualitaet_messungen`
   - Wie ist die Luftqualität im Bundesland?

3. **Arbeitsmarkt**: Rufe `arbeitsmarkt_facets` auf und filtere nach dem Bundesland "{bundesland}".
   - Wie ist die Arbeitsmarktsituation?
   - Welche Branchen und Berufsgruppen dominieren?

4. **Standortprofil**: Erstelle eine strukturierte Zusammenfassung:
   - **Energieprofil**: Installierte Kapazitäten, Energiemix, Zukunftspotenzial
   - **Umweltqualität**: Luftwerte, Belastungen, Trends
   - **Arbeitsmarkt**: Beschäftigung, Branchen, Qualifikationsnachfrage
   - **Standortfaktoren**: Stärken und Schwächen für Investoren und Unternehmen
   - **Gesamteinschätzung**: Standortattraktivität und Entwicklungsperspektiven

Starte jetzt mit Schritt 1."""
    return GetPromptResult(
        description=f"Standortprofil für: {bundesland}",
        messages=[
            PromptMessage(
                role="user",
                content=TextContent(type="text", text=text),
            )
        ],
    )


def _prompt_foerder_finder(beschreibung: str) -> GetPromptResult:
    """
    Passende Förderprogramme für ein Vorhaben finden und nach Relevanz bewerten.
    """
    text = f"""Du bist ein Förderexperte. Finde passende Förderprogramme für folgendes Vorhaben:

**Vorhaben:** {beschreibung}

Führe dazu folgende Schritte nacheinander aus:

1. **Schlüsselwörter ableiten**: Analysiere die Beschreibung "{beschreibung}" und identifiziere:
   - Branche/Sektor des Vorhabens
   - Unternehmensgröße (wenn erwähnt)
   - Technologie oder Innovationsfeld
   - Geografischer Fokus (wenn erwähnt)
   - Zielgruppe (Startup, KMU, Forschungseinrichtung, ...)

2. **Förderprogramme suchen**: Rufe `foerderung_list_programme` mehrfach mit verschiedenen Suchbegriffen auf:
   - Suche nach dem Hauptthema des Vorhabens
   - Suche nach der Branche
   - Suche nach dem Technologiefeld (wenn relevant)

3. **Relevanzprüfung**: Für jedes gefundene Programm prüfe:
   - Passt der Förderbereich zum Vorhaben?
   - Ist das Unternehmen in der Zielgruppe (Förderberechtigung)?
   - Ist das Programm aktuell aktiv?
   - Welche Förderart (Zuschuss, Darlehen, Bürgschaft)?

4. **Empfehlungsliste**: Erstelle eine priorisierte Liste der besten Förderprogramme:
   - **Sehr geeignet** (direkt relevant, Vorhaben passt genau)
   - **Geeignet** (teilweise relevant, Anpassung des Antrags nötig)
   - **Prüfen** (möglicherweise relevant, weitere Klärung nötig)

   Für jedes empfohlene Programm angeben:
   - Name und Fördergeber
   - Warum es zum Vorhaben passt
   - Förderart und Zielgruppe
   - Nächste Schritte (Link zur Antragstellung)

5. **Handlungsempfehlung**: Welche 1-3 Programme sollten zuerst angegangen werden und warum?

Starte jetzt mit Schritt 1."""
    return GetPromptResult(
        description=f"Förder-Finder für: {beschreibung[:80]}{'…' if len(beschreibung) > 80 else ''}",
        messages=[
            PromptMessage(
                role="user",
                content=TextContent(type="text", text=text),
            )
        ],
    )


# ---------------------------------------------------------------------------
# Haupt-Dispatch: get_prompt
# ---------------------------------------------------------------------------

async def handle_get_prompt(name: str, arguments: dict | None) -> GetPromptResult:
    """
    Dispatcht get_prompt-Aufrufe an die zuständigen Handler-Funktionen.
    """
    args = arguments or {}

    if name == "unternehmenscheck":
        company_name = args.get("company_name", "").strip()
        if not company_name:
            company_name = "[Unternehmensname nicht angegeben]"
        return _prompt_unternehmenscheck(company_name)

    if name == "branchenanalyse":
        branche = args.get("branche", "").strip()
        if not branche:
            branche = "[Branche nicht angegeben]"
        return _prompt_branchenanalyse(branche)

    if name == "politikfeld_briefing":
        thema = args.get("thema", "").strip()
        if not thema:
            thema = "[Thema nicht angegeben]"
        return _prompt_politikfeld_briefing(thema)

    if name == "standort_profil":
        bundesland = args.get("bundesland", "").strip()
        if not bundesland:
            bundesland = "[Bundesland nicht angegeben]"
        return _prompt_standort_profil(bundesland)

    if name == "foerder_finder":
        beschreibung = args.get("beschreibung", "").strip()
        if not beschreibung:
            beschreibung = "[Vorhaben nicht beschrieben]"
        return _prompt_foerder_finder(beschreibung)

    # Unbekannter Prompt
    available = ", ".join(p.name for p in ALL_PROMPTS)
    return GetPromptResult(
        description="Fehler",
        messages=[
            PromptMessage(
                role="user",
                content=TextContent(
                    type="text",
                    text=f"❌ Unbekannter Prompt: '{name}'\n\nVerfügbare Prompts: {available}",
                ),
            )
        ],
    )


# ---------------------------------------------------------------------------
# Registrierung am MCP-Server
# ---------------------------------------------------------------------------

def register_prompts(server: Server) -> None:
    """
    Registriert alle Prompt-Handler am übergebenen MCP-Server.
    Wird einmalig aus server.py aufgerufen.
    """

    @server.list_prompts()
    async def list_prompts() -> list[Prompt]:
        """Gibt alle verfügbaren knews Prompts zurück."""
        return ALL_PROMPTS

    @server.get_prompt()
    async def get_prompt(name: str, arguments: dict | None = None) -> GetPromptResult:
        """Gibt den Inhalt eines knews Prompts zurück."""
        return await handle_get_prompt(name, arguments)
