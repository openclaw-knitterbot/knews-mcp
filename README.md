# knews-mcp

**MCP Server für die knews Datenplattform** — Zugriff auf Bundesanzeiger, Handelsregister, News, Bundestag, Insolvenzen, Parteispenden, Rechtsprechung, Zwangsversteigerungen, Blaulicht und mehr — direkt aus Claude, Cursor oder jedem MCP-kompatiblen KI-Assistenten.

[![Version](https://img.shields.io/badge/version-0.2.0-blue)](https://github.com/openclaw-knitterbot/knews-mcp/releases)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## Was ist knews-mcp?

[knews](https://knews.press) ist eine Datenplattform für deutsche Wirtschafts- und Verwaltungsdaten. `knews-mcp` macht diese Daten per [Model Context Protocol (MCP)](https://modelcontextprotocol.io) für KI-Assistenten verfügbar.

**~59 Tools über 17 Datenbereiche — alles aus Deutschland, alles in einem MCP-Server.**

**Datenquellen:**
- 🏦 **Bundesanzeiger** — Jahresabschlüsse, Bilanzen, GuV (Elasticsearch + MySQL)
- 🏢 **Handelsregister** — Unternehmen, Geschäftsführer, Prokuristen (aus dem deutschen HR)
- 📰 **News** — 2,8 Mio. Artikel aus 60+ deutschen und internationalen Medien
- 🏛 **Bundestag** — Drucksachen und Vorgänge, LLM-klassifiziert nach Themenfeldern
- 💼 **Jobs (SAP/VW)** — Stellenangebote der größten deutschen Arbeitgeber
- 📊 **Arbeitsmarkt** — BA-Jobbörse mit täglichen Statistiken und Facetten
- ⚡ **Energie** — SMARD Stromerzeugung/-verbrauch, MaStR Anlagenregister
- 💶 **Förderung** — BMWK-Förderdatenbank mit Förderprogrammen
- 📋 **Vergabe** — Öffentliche Ausschreibungen (DTVP)
- 🇪🇺 **TED** — EU-weite Vergabebekanntmachungen (Tenders Electronic Daily)
- 🌬 **Luftqualität** — UBA-Messstationen und Schadstoffmessungen
- 🚨 **Blaulicht** — Polizei-, Feuerwehr- und Rettungsdienstmeldungen (15.000+)
- ⚠️ **Insolvenzen** — Insolvenzbekanntmachungen (69.000+ Verfahren)
- 💰 **Parteispenden** — Bundestag-Transparenzdatenbank (Spenden > 35.000 €)
- ⚖️ **Rechtsprechung** — 64.000+ Urteile und Beschlüsse aus deutschen Gerichten
- 🏠 **Zwangsversteigerungen** — ZVG-Portal Daten aus deutschen Amtsgerichten (2.900+)

---

## Installation

### Option 1: pip von GitHub (empfohlen)

```bash
pip install git+https://github.com/openclaw-knitterbot/knews-mcp.git
```

### Option 2: uvx (kein Install nötig)

```bash
uvx --from git+https://github.com/openclaw-knitterbot/knews-mcp.git knews-mcp
```

---

## Konfiguration

Du benötigst einen **knews API Key**. Registriere dich unter [knews.press/portal](https://knews.press/portal).

Setze den API Key als Umgebungsvariable:

```bash
export KNEWS_API_KEY="kna_deinApiKeyHier"
```

---

## Verwendung mit Claude Desktop

Zuerst installieren: `pip install git+https://github.com/openclaw-knitterbot/knews-mcp.git`

Dann in deine Claude Desktop Konfiguration einfügen (`~/Library/Application Support/Claude/claude_desktop_config.json` auf macOS):

```json
{
  "mcpServers": {
    "knews": {
      "command": "knews-mcp",
      "env": {
        "KNEWS_API_KEY": "kna_deinApiKeyHier"
      }
    }
  }
}
```

---

## Verwendung mit Cursor / anderen MCP-Clients

Gleiche Konfiguration wie oben — ersetze `command` und `args` entsprechend deinem Client.

---

## Verfügbare Tools

### 🏦 Bundesanzeiger

| Tool | Beschreibung |
|------|-------------|
| `bundesanzeiger_search` | Volltextsuche in Jahresabschlüssen (Elasticsearch) |
| `bundesanzeiger_list_reports` | Geparste Berichte filtern (Unternehmen, Rechtsform, Jahr) |
| `bundesanzeiger_get_report` | Einzelbericht mit Bilanz- und GuV-Daten |

### 🏢 Handelsregister

| Tool | Beschreibung |
|------|-------------|
| `handelsregister_search_companies` | Unternehmen suchen (Name, Registerart, Bundesland) |
| `handelsregister_get_company` | Unternehmensdetail + alle eingetragenen Personen |
| `handelsregister_search_officers` | Personen suchen (Geschäftsführer, Prokuristen, Vorstände) |
| `handelsregister_stats` | Statistiken: Anzahl, Registerarten, Bundesländer |

### 📰 News

| Tool | Beschreibung |
|------|-------------|
| `news_list_feeds` | Alle verfügbaren Feeds (60+ Quellen) |
| `news_search_articles` | 2,8 Mio. Artikel durchsuchen (Titel, Teaser, Feed, Zeitraum) |

### 🏛 Bundestag

| Tool | Beschreibung |
|------|-------------|
| `bundestag_list_drucksachen` | Drucksachen (Anträge, Gesetzentwürfe) mit LLM-Klassifikation |
| `bundestag_get_drucksache` | Einzeldrucksache + Themen/Keywords |
| `bundestag_list_vorgaenge` | Parlamentarische Vorgänge |
| `bundestag_list_personen` | Abgeordnete und Parlamentarier |
| `bundestag_get_person` | Einzelperson mit Rollen und Wahlperioden |
| `bundestag_stats` | Statistiken nach Typ und Themenfeld |

### 💼 Jobs & Arbeitsmarkt

| Tool | Beschreibung |
|------|-------------|
| `jobs_list` | Stellenangebote von SAP und/oder VW |
| `arbeitsmarkt_jobs` | BA-Jobbörse durchsuchen (Beruf, Arbeitgeber, Region) |
| `arbeitsmarkt_stats` | Tägliche Arbeitsmarktstatistiken (bis 365 Tage) |
| `arbeitsmarkt_facets` | Top-Branchen, Berufsfelder, Regionen |

### ⚡ Energie

| Tool | Beschreibung |
|------|-------------|
| `energie_get_filters` | Verfügbare SMARD-Datenreihen (Strom, Preise) |
| `energie_timeseries` | SMARD Zeitreihendaten (Erzeugung, Verbrauch, Preise) |
| `energie_mastr_snapshot` | MaStR-Snapshot: Anlagen nach Energieträger und Bundesland |
| `energie_mastr_totals` | MaStR Gesamtzahlen im Zeitverlauf |

### 💶 Förderung

| Tool | Beschreibung |
|------|-------------|
| `foerderung_list_programme` | Förderprogramme (BMWK-Datenbank) |
| `foerderung_get_programm` | Programmdetail mit Volltext |

### 📋 Vergabe (National)

| Tool | Beschreibung |
|------|-------------|
| `vergabe_ausschreibungen` | Öffentliche Ausschreibungen (DTVP) |
| `vergabe_auftraggeber` | Top-Auftraggeber nach Aktivität |
| `vergabe_stats` | KPI-Übersicht (Typen, Vergaberecht, Fristen) |

### 🇪🇺 TED (EU-Vergabe)

| Tool | Beschreibung |
|------|-------------|
| `ted_notices` | EU-Vergabebekanntmachungen (TED) |
| `ted_stats` | TED-Statistiken (Typen, CPV, Volumen) |
| `ted_top_buyers` | Top-Auftraggeber in der EU |

### 🌬 Luftqualität

| Tool | Beschreibung |
|------|-------------|
| `luftqualitaet_stationen` | UBA-Messstationen (nach Stadt, Netz) |
| `luftqualitaet_messungen` | Schadstoffmesswerte (PM10, NO2, O3...) |
| `luftqualitaet_ueberschreitungen` | Grenzwertüberschreitungen nach Station und Jahr |

### 🚨 Blaulicht *(neu in v0.2.0)*

| Tool | Beschreibung |
|------|-------------|
| `blaulicht_suche` | Volltextsuche in Blaulicht-Meldungen (Elasticsearch) |
| `blaulicht_meldungen` | Aktuelle Polizei-/Feuerwehr-/Rettungsmeldungen (SQL) |

### ⚠️ Insolvenzen *(neu in v0.2.0)*

| Tool | Beschreibung |
|------|-------------|
| `insolvenzen_suche` | Volltextsuche in Insolvenzbekanntmachungen (ES) |
| `insolvenzen_liste` | Insolvenzbekanntmachungen (SQL, nach Region/Gericht) |
| `insolvenzen_stats` | Statistiken: Eröffnungen, Abweisungen, Firmensachen |

### 💰 Parteispenden *(neu in v0.2.0)*

| Tool | Beschreibung |
|------|-------------|
| `parteispenden_suche` | Spenden nach Spender, Partei, Jahr, Betrag filtern |
| `parteispenden_stats` | Gesamtstatistiken nach Partei |
| `parteispenden_parteien` | Alle Parteien mit Spendenzahlen |

### ⚖️ Rechtsprechung *(neu in v0.2.0)*

| Tool | Beschreibung |
|------|-------------|
| `rechtsprechung_suche` | Urteile und Beschlüsse suchen (Gerichtsbarkeit, Ebene, Typ) |
| `rechtsprechung_stats` | Statistiken: nach Gerichtsbarkeit, Ebene, Entscheidungstyp |
| `rechtsprechung_jurisdictions` | Alle Gerichtsbarkeiten mit Fallzahlen |

### 🏠 Zwangsversteigerungen *(neu in v0.2.0)*

| Tool | Beschreibung |
|------|-------------|
| `zvg_stats` | Überblick: Gesamtzahl, nach Bundesland, Verkehrswerte, Termine |
| `zvg_liste` | Versteigerungstermine (Bundesland, Datum, Wert, Gericht) |
| `zvg_suche` | Volltextsuche in ZVG-Objekten (Elasticsearch) |

---

## 🔭 Composite-Tools (Cross-Domain Intelligence)

Der eigentliche USP von knews-mcp: **Ein API-Call, mehrere Datenquellen kombiniert.**

| Tool | Kombiniert |
|------|-----------|
| `company_360` | HR + Bundesanzeiger + News + **Insolvenz-Check** + **ZVG-Check** + Jobs-Signal |
| `person_profil` | HR-Mandate + Firmen + News + **Parteispenden-Check** |
| `markt_radar` | Arbeitsmarkt + Vergabe für ein Berufsfeld |
| `region_dashboard` | Energie + Luftqualität + Arbeitsmarkt + Vergabe |
| `foerder_match` | Passende Förderprogramme matchen |
| `energie_trend` | SMARD-Erzeugung + MaStR-Zubau im Zeitverlauf |
| `arbeitsmarkt_trend` | Zeitreihenanalyse Stellenmarkt |
| `vergabe_trend` | Ausschreibungsvolumen im Zeitverlauf |
| `insolvenz_radar` *(neu)* | Insolvenz + HR + Bundesanzeiger + ZVG → Risiko-Assessment |
| `wirtschafts_vernetzung` *(neu)* | HR-Mandate + Parteispenden + Bundesanzeiger → Vernetzungsmap |
| `region_radar` *(neu)* | Blaulicht + Insolvenzen + ZVG + Arbeitsmarkt → Lageübersicht |

---

## Beispiel-Queries

Frage deinen KI-Assistenten zum Beispiel:

- *„Suche den Jahresabschluss von BMW aus 2022 im Bundesanzeiger."*
- *„Wer ist Geschäftsführer der Wirecard AG laut Handelsregister?"*
- *„Gibt es laufende Insolvenzverfahren gegen die Mustermann GmbH?"*
- *„Welche Parteispenden hat Herr Friedrich Merz getätigt?"*
- *„Zeig mir aktuelle Zwangsversteigerungen in Bayern unter 200.000 €."*
- *„Erstelle ein Risiko-Assessment für die Signa Holding."* → `insolvenz_radar`
- *„Wer ist Friedrich Merz wirtschaftlich vernetzt?"* → `wirtschafts_vernetzung`
- *„Was passiert gerade in Sachsen-Anhalt?"* → `region_radar`
- *„Zeig mir alle Drucksachen zum Thema Klimaschutz aus der aktuellen Wahlperiode."*
- *„Wie hat sich die Solarstromproduktion in Deutschland in den letzten 30 Tagen entwickelt?"*
- *„Welche KMU-Förderprogramme des Bundes gibt es für Digitalisierung?"*
- *„Wie ist die Luftqualität (NO2) in München aktuell?"*

---

## API Scopes

Abhängig von deinem Abonnement auf [knews.press](https://knews.press/portal) stehen unterschiedliche Datenbereiche zur Verfügung:

| Scope | Daten |
|-------|-------|
| `bundesanzeiger:read` | Bundesanzeiger |
| `handelsregister:read` | Handelsregister |
| `news:read` | News-Feeds und Artikel |
| `bundestag:read` | Bundestag Drucksachen/Vorgänge |
| `jobs:read` | SAP/VW Stellenangebote |
| `arbeitsmarkt:read` | BA-Jobbörse |
| `energie:read` | SMARD + MaStR |
| `foerderung:read` | Förderprogramme |
| `vergabe:read` | Nationale Ausschreibungen |
| `ted:read` | EU-Vergabe (TED) |
| `luftqualitaet:read` | UBA Luftqualität |
| `blaulicht:read` | Polizei/Feuerwehr/Rettung |
| `insolvenzen:read` | Insolvenzbekanntmachungen |
| `parteispenden:read` | Parteispenden-Transparenz |
| `rechtsprechung:read` | Gerichtsurteile und Beschlüsse |
| `zwangsversteigerungen:read` | ZVG-Daten |
| `all` | Vollzugriff |

Tools ohne den passenden Scope geben eine 403-Fehlermeldung zurück.

---

## Entwicklung

```bash
git clone https://github.com/openclaw-knitterbot/knews-mcp.git
cd knews-mcp
pip install -e ".[dev]"
export KNEWS_API_KEY="kna_..."
knews-mcp
```

---

## Changelog

### v0.2.0 (2026-03-04)
- **Neu:** 5 neue Datenbereiche — Blaulicht, Insolvenzen, Parteispenden, Rechtsprechung, Zwangsversteigerungen
- **Neu:** 3 neue Composite-Tools — `insolvenz_radar`, `wirtschafts_vernetzung`, `region_radar`
- **Erweitert:** `company_360` mit Insolvenz-Check + ZVG-Check + Jobs-Signal
- **Erweitert:** `person_profil` mit Parteispenden-Check
- ~59 Tools total (vorher 29)

### v0.1.5
- TED EU-Vergabe Tools
- Composite Tools (company_360, person_profil, markt_radar etc.)

---

## Lizenz

MIT — siehe [LICENSE](LICENSE)

---

## Links

- 🌐 [knews.press](https://knews.press) — Hauptseite
- 🔑 [knews.press/portal](https://knews.press/portal) — API Key holen
- 📖 [knews.press/portal](https://knews.press/portal) — API Dokumentation (Login erforderlich)
- 💬 [GitHub Issues](https://github.com/openclaw-knitterbot/knews-mcp/issues) — Bugs & Feature Requests
