# ROADMAP.md — knews-mcp Ausbaukonzept

## Status Quo (v0.1.0)

- 29 Tools über 10 Datenbereiche (Bundesanzeiger, Handelsregister, News, Bundestag, Jobs, Arbeitsmarkt, Energie, Förderung, Vergabe, Luftqualität)
- Nur MCP `tools` — keine Resources, Prompts oder Sampling
- Nur `stdio`-Transport (lokaler Betrieb)
- Read-only GET-Requests via httpx
- Nicht auf PyPI publiziert

---

## Phase 0: API-Lücken schließen

**Ziel:** Alles was in den DBs steckt, auch über die API + MCP zugänglich machen.

- [ ] Gap-Analyse: DB-Tabellen vs. API-Endpunkte (Sub-Agent läuft)
- [ ] Fehlende Endpunkte in knews-data-api nachziehen
- [ ] Fehlende MCP-Tools für neue Endpunkte
- [ ] knews-user-portal Doku aktualisieren

---

## Phase 1: MCP-Protokoll voll ausnutzen

**Ziel:** Resources und Prompts nutzen — bringt den größten Hebel bei geringstem Aufwand.

### Resources (browsbare Datenquellen)

MCP Resources erlauben Clients, Daten zu browsen, cachen und als Kontext zu halten.

- [x] `knews://company/{id}` — Handelsregister-Unternehmensprofil
- [x] `knews://bundesanzeiger/report/{id}` — Jahresabschluss mit Bilanz/GuV
- [x] `knews://bundestag/drucksache/{id}` — Drucksache mit Klassifikation
- [ ] `knews://news/feed/{id}` — Feed-Profil mit letzten Artikeln (ausstehend: API-Endpunkt fehlt)
- [x] `knews://energie/filter/{id}` — SMARD-Datenreihe (letzte 7 Tage)
- [x] `knews://foerderung/programm/{id}` — Förderprogramm-Detail
- [x] Resource Templates für dynamische URIs (`src/knews_mcp/resources.py`)
- [x] Statische Resources: `knews://feeds`, `knews://energie/filters`

### Prompts (vorgefertigte Analysevorlagen)

Prompts sind vorgefertigte, parametrisierte Analyse-Templates, die der User im Client auswählen kann.

- [x] `unternehmenscheck` — Komplettbild: HR + Bundesanzeiger + News + Personen
- [x] `branchenanalyse` — Arbeitsmarkt + Förderung + Vergabe für eine Branche
- [x] `politikfeld_briefing` — Bundestag + Vergabe + Förderung zu einem Thema
- [x] `standort_profil` — Energie + Luftqualität + Arbeitsmarkt für eine Region
- [x] `foerder_finder` — Passende Förderprogramme für ein Unternehmensprofil

---

## Phase 2: Cross-Domain Intelligence

**Ziel:** Die 10 isolierten Datenbereiche intelligent verknüpfen. Das ist der echte USP — kein anderer MCP-Server kann 10 deutsche Datenquellen kreuzen.

### Composite Tools (ein Call, mehrere Quellen)

- [x] `company_360` — Handelsregister + Bundesanzeiger + News zu einer Firma
- [x] `markt_radar` — Arbeitsmarkt + Jobs + Vergabe für ein Berufsfeld
- [x] `region_dashboard` — Energie + Luft + Arbeitsmarkt + Vergabe für ein Bundesland
- [x] `foerder_match` — Förderprogramme matchen auf Firmenprofil (Rechtsform, Größe, Branche)
- [x] `person_profil` — Handelsregister-Person: alle Mandate, verbundene Firmen, Bundesanzeiger-Daten

### Trend-Tools (Zeitreihen kombinieren)

- [x] `energie_trend` — SMARD-Erzeugung + MaStR-Zubau kombiniert
- [x] `arbeitsmarkt_trend` — Zeitreihe + Facetten-Vergleich über Monate
- [x] `vergabe_trend` — Ausschreibungsvolumen nach Branche/Region im Zeitverlauf

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
| 0 — API-Lücken | Mittel | Hoch (Grundlage) | 🔴 Sofort |
| 1 — Resources + Prompts | Gering | Hoch (UX-Sprung) | 🔴 Sofort |
| 2 — Cross-Domain | Mittel | Sehr hoch (USP) | 🟡 Nächster Sprint |
| 3 — SSE + Performance | Mittel | Mittel | 🟢 Wenn externe Nutzer |
| 4 — Distribution | Gering–Mittel | Hoch (Reichweite) | 🟡 Nach Phase 1+2 |
| 5 — Write-Ops | Hoch | Mittel–Hoch | 🟢 Langfristig |

---

_Zuletzt aktualisiert: 2026-02-26 — Phase 2 (Cross-Domain Composite Tools + Bundestag Personen) implementiert_
