# knews-mcp

**MCP Server für die knews Datenplattform** — Zugriff auf Bundesanzeiger, Handelsregister, News, Bundestag, Arbeitsmarkt, Energie, Förderung, Vergabe und Luftqualitätsdaten — direkt aus Claude, Cursor oder jedem MCP-kompatiblen KI-Assistenten.

[![GitHub](https://img.shields.io/github/v/release/openclaw-knitterbot/knews-mcp)](https://github.com/openclaw-knitterbot/knews-mcp/releases)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## Was ist knews-mcp?

[knews](https://knews.press) ist eine Datenplattform für deutsche Wirtschafts- und Verwaltungsdaten. `knews-mcp` macht diese Daten per [Model Context Protocol (MCP)](https://modelcontextprotocol.io) für KI-Assistenten verfügbar.

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
- 🌬 **Luftqualität** — UBA-Messstationen und Schadstoffmessungen

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

### 📋 Vergabe

| Tool | Beschreibung |
|------|-------------|
| `vergabe_ausschreibungen` | Öffentliche Ausschreibungen (DTVP) |
| `vergabe_auftraggeber` | Top-Auftraggeber nach Aktivität |
| `vergabe_stats` | KPI-Übersicht (Typen, Vergaberecht, Fristen) |

### 🌬 Luftqualität

| Tool | Beschreibung |
|------|-------------|
| `luftqualitaet_stationen` | UBA-Messstationen (nach Stadt, Netz) |
| `luftqualitaet_messungen` | Schadstoffmesswerte (PM10, NO2, O3...) |
| `luftqualitaet_ueberschreitungen` | Grenzwertüberschreitungen nach Station und Jahr |

---

## Beispiel-Queries

Frage deinen KI-Assistenten zum Beispiel:

- *„Suche den Jahresabschluss von BMW aus 2022 im Bundesanzeiger."*
- *„Wer ist Geschäftsführer der Wirecard AG laut Handelsregister?"*
- *„Zeig mir alle Drucksachen zum Thema Klimaschutz aus der aktuellen Wahlperiode."*
- *„Wie hat sich die Solarstromproduktion in Deutschland in den letzten 30 Tagen entwickelt?"*
- *„Welche KMU-Förderprogramme des Bundes gibt es für Digitalisierung?"*
- *„Zeig mir aktuelle Ausschreibungen im Bereich IT-Infrastruktur."*
- *„Wie ist die Luftqualität (NO2) in München aktuell?"*
- *„Wie viele offene Stellen gibt es gerade bei SAP?"*

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
| `vergabe:read` | Ausschreibungen |
| `luftqualitaet:read` | UBA Luftqualität |
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

## Lizenz

MIT — siehe [LICENSE](LICENSE)

---

## Links

- 🌐 [knews.press](https://knews.press) — Hauptseite
- 🔑 [knews.press/portal](https://knews.press/portal) — API Key holen
- 📖 [api.knews.press/docs](https://api.knews.press/docs) — API Dokumentation
- 💬 [GitHub Issues](https://github.com/openclaw-knitterbot/knews-mcp/issues) — Bugs & Feature Requests
