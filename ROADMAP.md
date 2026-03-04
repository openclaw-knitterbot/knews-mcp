# ROADMAP.md — knews-mcp Ausbaukonzept

## Status Quo (v0.2.0)

- ~59 Tools über 17 Datenbereiche
- Neue Datenbereiche: Blaulicht, Insolvenzen, Parteispenden, Rechtsprechung, Zwangsversteigerungen
- Neue Composite-Tools: insolvenz_radar, wirtschafts_vernetzung, region_radar
- MCP `tools` + `resources` + `prompts`
- Nur `stdio`-Transport (lokaler Betrieb)
- Read-only GET-Requests via httpx

---

## Phase 0: API-Lücken schließen ✅ ERLEDIGT

**Ziel:** Alles was in den DBs steckt, auch über die API + MCP zugänglich machen.

- [x] Gap-Analyse: DB-Tabellen vs. API-Endpunkte
- [x] Fehlende Endpunkte in knews-data-api nachziehen
- [x] Blaulicht-Tools (`blaulicht_suche`, `blaulicht_meldungen`)
- [x] Insolvenzen-Tools (`insolvenzen_suche`, `insolvenzen_liste`, `insolvenzen_stats`)
- [x] Parteispenden-Tools (`parteispenden_suche`, `parteispenden_stats`, `parteispenden_parteien`)
- [x] Rechtsprechung-Tools (`rechtsprechung_suche`, `rechtsprechung_stats`, `rechtsprechung_jurisdictions`)
- [x] Zwangsversteigerungen-Tools (`zvg_stats`, `zvg_liste`, `zvg_suche`)
- [x] knews-user-portal Doku aktualisieren

---

## Phase 1: MCP-Protokoll voll ausnutzen ✅ ERLEDIGT

**Ziel:** Resources und Prompts nutzen — bringt den größten Hebel bei geringstem Aufwand.

### Resources (browsbare Datenquellen)

- [x] `knews://company/{id}` — Handelsregister-Unternehmensprofil
- [x] `knews://bundesanzeiger/report/{id}` — Jahresabschluss mit Bilanz/GuV
- [x] `knews://bundestag/drucksache/{id}` — Drucksache mit Klassifikation
- [ ] `knews://news/feed/{id}` — Feed-Profil mit letzten Artikeln (ausstehend: API-Endpunkt fehlt)
- [x] `knews://energie/filter/{id}` — SMARD-Datenreihe (letzte 7 Tage)
- [x] `knews://foerderung/programm/{id}` — Förderprogramm-Detail
- [x] Resource Templates für dynamische URIs (`src/knews_mcp/resources.py`)
- [x] Statische Resources: `knews://feeds`, `knews://energie/filters`

### Prompts (vorgefertigte Analysevorlagen)

- [x] `unternehmenscheck` — Komplettbild: HR + Bundesanzeiger + News + Personen
- [x] `branchenanalyse` — Arbeitsmarkt + Förderung + Vergabe für eine Branche
- [x] `politikfeld_briefing` — Bundestag + Vergabe + Förderung zu einem Thema
- [x] `standort_profil` — Energie + Luftqualität + Arbeitsmarkt für eine Region
- [x] `foerder_finder` — Passende Förderprogramme für ein Unternehmensprofil

---

## Phase 2: Cross-Domain Intelligence ✅ ERLEDIGT

**Ziel:** Die Datenbereiche intelligent verknüpfen.

### Composite Tools (ein Call, mehrere Quellen)

- [x] `company_360` — HR + Bundesanzeiger + News + Insolvenz-Check + ZVG-Check + Jobs-Signal
- [x] `markt_radar` — Arbeitsmarkt + Jobs + Vergabe für ein Berufsfeld
- [x] `region_dashboard` — Energie + Luft + Arbeitsmarkt + Vergabe für ein Bundesland
- [x] `foerder_match` — Förderprogramme matchen auf Firmenprofil
- [x] `person_profil` — HR-Person: alle Mandate + Firmen + News + Parteispenden-Check

### Trend-Tools (Zeitreihen kombinieren)

- [x] `energie_trend` — SMARD-Erzeugung + MaStR-Zubau kombiniert
- [x] `arbeitsmarkt_trend` — Zeitreihe + Facetten-Vergleich über Monate
- [x] `vergabe_trend` — Ausschreibungsvolumen nach Branche/Region im Zeitverlauf

### Neue Composite-Tools (v0.2.0)

- [x] `insolvenz_radar` — Insolvenz + HR + Bundesanzeiger + ZVG → Risiko-Assessment
- [x] `wirtschafts_vernetzung` — HR-Mandate + Parteispenden + Bundesanzeiger → Vernetzungsmap
- [x] `region_radar` — Blaulicht + Insolvenzen + ZVG + Arbeitsmarkt → Lageübersicht

---

## Phase 3: SSE-Transport + Performance

**Ziel:** Remote-Nutzung und bessere Performance für große Datenmengen.

- [ ] **SSE-Transport** — Web-Clients, Remote-Nutzung, Multi-User
- [ ] **Response-Caching** — httpx-Cache oder Redis für häufige Abfragen
- [ ] **Streaming** — Große Resultsets (Bundesanzeiger 10k+ Treffer) streamen statt komplett laden
- [ ] **Connection Pooling** — Persistent httpx.AsyncClient statt pro-Request

---

## Phase 4: Distribution & Monetarisierung

**Ziel:** Externe Nutzer, Sichtbarkeit, ggf. Einnahmen.

- [ ] **PyPI-Publish** (Workflow ist vorbereitet, nur Tag pushen)
- [ ] **Docker-Image** für Self-Hosting (`ghcr.io/openclaw-knitterbot/knews-mcp`)
- [ ] **Docs-Site** (GitHub Pages oder knews.press/mcp)
- [ ] **Claude Desktop Marketplace** / Cursor Listing
- [ ] **Tiered API Keys** — Free (100 req/Tag), Pro (unlimitiert)
- [ ] **Usage Analytics** — Welche Tools werden wie oft genutzt?

---

## Phase 5: Write-Operations & Alerts (langfristig)

**Ziel:** Vom Read-only-Tool zum interaktiven Daten-Assistenten.

- [ ] **Watchlists** — Unternehmen/Themen/Regionen beobachten
- [ ] **Alerts** — "Benachrichtige mich bei neuem Jahresabschluss von X"
- [ ] **Annotations** — User-Notizen an Datensätze anhängen
- [ ] **Export** — CSV/Excel-Download über MCP
- [ ] **Vergleiche** — Zwei Unternehmen/Regionen/Zeiträume nebeneinander

---

## Priorisierung

| Phase | Aufwand | Impact | Priorität |
|-------|---------|--------|-----------|
| 0 — API-Lücken | Mittel | Hoch (Grundlage) | ✅ Erledigt |
| 1 — Resources + Prompts | Gering | Hoch (UX-Sprung) | ✅ Erledigt |
| 2 — Cross-Domain | Mittel | Sehr hoch (USP) | ✅ Erledigt |
| 3 — SSE + Performance | Mittel | Mittel | 🟢 Wenn externe Nutzer |
| 4 — Distribution | Gering–Mittel | Hoch (Reichweite) | 🟡 Nächster Sprint |
| 5 — Write-Ops | Hoch | Mittel–Hoch | 🟢 Langfristig |

---

_Zuletzt aktualisiert: 2026-03-04 — v0.2.0: 5 neue Datenbereiche + erweiterte Composite-Tools_
