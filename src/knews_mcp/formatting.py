"""
Response-Formatting: JSON → lesbarer Text.

Alle format_* Funktionen nehmen ein data-Dict (aus der API) und geben
einen Token-effizienten, gut lesbaren String zurück.
"""

from typing import Any


def _trunc(s: str | None, maxlen: int = 200) -> str:
    if not s:
        return ""
    s = str(s).strip()
    return s[:maxlen] + "…" if len(s) > maxlen else s


def _none(v: Any, fallback: str = "–") -> str:
    if v is None or v == "":
        return fallback
    return str(v)


def format_error(error_msg: str) -> str:
    return f"❌ Fehler: {error_msg}"


def format_pagination(total: Any, page: int, size: int) -> str:
    if total is not None:
        pages = (int(total) + size - 1) // size if size > 0 else 1
        return f"(Seite {page + 1}/{pages}, {total} Gesamt)"
    return f"(Seite {page + 1}, max {size} Ergebnisse)"


# ---------------------------------------------------------------------------
# Bundesanzeiger
# ---------------------------------------------------------------------------

def format_bundesanzeiger_search(data: dict) -> str:
    total = data.get("total", 0)
    results = data.get("results", [])
    lines = [f"🔍 Bundesanzeiger-Volltextsuche — {total} Treffer\n"]
    for i, r in enumerate(results, 1):
        lines.append(f"{i}. **{_none(r.get('company'))}** ({_none(r.get('legal_form'))})")
        lines.append(f"   📍 {_none(r.get('city'))} | Gericht: {_none(r.get('register_court'))} {_none(r.get('register_number'))}")
        fy_start = _none(r.get('fiscal_year_start'))
        fy_end = _none(r.get('fiscal_year_end'))
        lines.append(f"   📅 Geschäftsjahr: {fy_start} – {fy_end} | Veröffentlicht: {_none(r.get('publication_date'))}")
        lines.append(f"   🆔 ID: {_none(r.get('id'))}")
        highlights = r.get("highlights", [])
        if highlights:
            lines.append(f"   💬 Auszug: {_trunc(highlights[0].replace('<mark>', '«').replace('</mark>', '»'), 300)}")
        lines.append("")
    return "\n".join(lines)


def format_bundesanzeiger_reports(data: dict, page: int, size: int) -> str:
    total = data.get("total", 0)
    results = data.get("results", [])
    lines = [f"📊 Bundesanzeiger-Berichte — {format_pagination(total, page, size)}\n"]
    for r in results:
        lines.append(f"• **{_none(r.get('company'))}** [{_none(r.get('legal_form'))}]")
        lines.append(f"  📍 {_none(r.get('city'))} | {_none(r.get('register_court'))} {_none(r.get('register_number'))}")
        lines.append(f"  📅 GJ-Ende: {_none(r.get('fiscal_year_end'))} | ID: {_none(r.get('id'))}")
        lines.append("")
    return "\n".join(lines)


def format_bundesanzeiger_report(data: dict) -> str:
    r = data.get("report", {}) or {}
    b = data.get("bilanz", {}) or {}
    g = data.get("guv", {}) or {}
    lines = [
        f"📋 **{_none(r.get('company'))}** ({_none(r.get('legal_form'))})",
        f"📍 {_none(r.get('city'))} | {_none(r.get('register_court'))} {_none(r.get('register_number'))}",
        f"📅 Geschäftsjahr: {_none(r.get('fiscal_year_start'))} – {_none(r.get('fiscal_year_end'))}",
        f"📰 Veröffentlicht: {_none(r.get('publication_date'))}",
        "",
    ]
    if b:
        lines.append("**Bilanz:**")
        for k, v in b.items():
            if k not in ("id", "report_id") and v is not None:
                lines.append(f"  {k}: {v}")
        lines.append("")
    if g:
        lines.append("**GuV:**")
        for k, v in g.items():
            if k not in ("id", "report_id") and v is not None:
                lines.append(f"  {k}: {v}")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# News
# ---------------------------------------------------------------------------

def format_news_feeds(data: dict) -> str:
    feeds = data.get("feeds", [])
    lines = [f"📰 News-Feeds — {len(feeds)} verfügbar\n"]
    for f in feeds:
        lang = f.get("language_id", "")
        lines.append(f"• **{_none(f.get('name'))}** [{lang}] — {_none(f.get('url'))}")
    return "\n".join(lines)


def format_news_articles(data: dict, page: int, size: int) -> str:
    total = data.get("total")
    results = data.get("results", [])
    lines = [f"📰 Newsartikel — {format_pagination(total, page, size)}\n"]
    for r in results:
        lines.append(f"• **{_trunc(r.get('title'), 120)}**")
        lines.append(f"  🗞 {_none(r.get('feed'))} | 🕐 {_none(r.get('pubtime'))}")
        if r.get("teaser"):
            lines.append(f"  {_trunc(r.get('teaser'), 200)}")
        lines.append(f"  🔗 {_none(r.get('url'))}")
        lines.append("")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Bundestag
# ---------------------------------------------------------------------------

def format_bundestag_drucksachen(data: dict, page: int, size: int) -> str:
    total = data.get("total", 0)
    results = data.get("results", [])
    lines = [f"🏛 Bundestag Drucksachen — {format_pagination(total, page, size)}\n"]
    for r in results:
        lines.append(f"• **{_trunc(r.get('titel'), 120)}**")
        lines.append(
            f"  📄 {_none(r.get('drucksachetyp'))} | WP {_none(r.get('wahlperiode'))} | "
            f"📅 {_none(r.get('datum'))} | Nr: {_none(r.get('dokumentnummer'))}"
        )
        if r.get("urheber"):
            lines.append(f"  👤 Urheber: {_trunc(r.get('urheber'), 100)}")
        if r.get("pdf_url"):
            lines.append(f"  📄 PDF: {_none(r.get('pdf_url'))}")
        lines.append("")
    return "\n".join(lines)


def format_bundestag_drucksache(data: dict) -> str:
    d = data.get("drucksache", {}) or {}
    k = data.get("klassifikation", {}) or {}
    lines = [
        f"🏛 **{_trunc(d.get('titel'), 200)}**",
        f"📄 {_none(d.get('drucksachetyp'))} | WP {_none(d.get('wahlperiode'))} | 📅 {_none(d.get('datum'))}",
        f"📋 Nr: {_none(d.get('dokumentnummer'))} | ID: {_none(d.get('id'))}",
    ]
    if d.get("urheber"):
        lines.append(f"👤 Urheber: {_none(d.get('urheber'))}")
    if d.get("ressort"):
        lines.append(f"🏢 Ressort: {_none(d.get('ressort'))}")
    if d.get("pdf_url"):
        lines.append(f"📄 PDF: {_none(d.get('pdf_url'))}")
    if k:
        lines.append("")
        lines.append("**LLM-Klassifikation:**")
        if k.get("themen"):
            lines.append(f"  Themen: {_none(k.get('themen'))}")
        if k.get("keywords"):
            lines.append(f"  Keywords: {_trunc(k.get('keywords'), 200)}")
        if k.get("model"):
            lines.append(f"  Modell: {_none(k.get('model'))} | Klassifiziert: {_none(k.get('classified_at'))}")
    return "\n".join(lines)


def format_bundestag_vorgaenge(data: dict, page: int, size: int) -> str:
    total = data.get("total", 0)
    results = data.get("results", [])
    lines = [f"🏛 Bundestag Vorgänge — {format_pagination(total, page, size)}\n"]
    for r in results:
        lines.append(f"• **{_trunc(r.get('titel'), 120)}**")
        lines.append(
            f"  🔄 {_none(r.get('typ'))} | WP {_none(r.get('wahlperiode'))} | "
            f"📅 {_none(r.get('datum'))} | Stand: {_trunc(r.get('beratungsstand'), 60)}"
        )
        if r.get("abstract"):
            lines.append(f"  {_trunc(r.get('abstract'), 200)}")
        lines.append("")
    return "\n".join(lines)


def format_bundestag_personen(data: dict, page: int, size: int) -> str:
    """Formatiert die Liste der Bundestag-Personen."""
    total = data.get("total", 0)
    results = data.get("results", [])
    lines = [f"👤 Bundestag Personen — {format_pagination(total, page, size)}\n"]
    for r in results:
        funktion = r.get("funktion") or []
        if isinstance(funktion, str):
            import json
            try:
                funktion = json.loads(funktion)
            except Exception:
                funktion = [funktion]
        wahlperioden = r.get("wahlperiode") or []
        if isinstance(wahlperioden, str):
            import json
            try:
                wahlperioden = json.loads(wahlperioden)
            except Exception:
                wahlperioden = []
        wp_str = ", ".join(str(w) for w in wahlperioden) if wahlperioden else "–"
        fn_str = ", ".join(funktion) if funktion else "–"
        lines.append(
            f"• **{_none(r.get('vorname'))} {_none(r.get('nachname'))}** (ID: {_none(r.get('id'))})"
        )
        lines.append(f"  🏛 Funktion: {fn_str} | WP: {wp_str}")
        if r.get("aktualisiert"):
            lines.append(f"  📅 Aktualisiert: {str(r.get('aktualisiert'))[:10]}")
        lines.append("")
    return "\n".join(lines)


def format_bundestag_person(data: dict) -> str:
    """Formatiert eine einzelne Bundestag-Person mit allen Details."""
    import json as _json
    p = data.get("person", {}) or {}
    funktion = p.get("funktion") or []
    if isinstance(funktion, str):
        try:
            funktion = _json.loads(funktion)
        except Exception:
            funktion = [funktion]
    wahlperioden = p.get("wahlperiode") or []
    if isinstance(wahlperioden, str):
        try:
            wahlperioden = _json.loads(wahlperioden)
        except Exception:
            wahlperioden = []
    person_roles = p.get("person_roles")
    if isinstance(person_roles, str):
        try:
            person_roles = _json.loads(person_roles)
        except Exception:
            person_roles = None

    fn_str = ", ".join(funktion) if funktion else "–"
    wp_str = ", ".join(str(w) for w in wahlperioden) if wahlperioden else "–"

    lines = [
        f"👤 **{_none(p.get('vorname'))} {_none(p.get('nachname'))}**",
        f"🆔 DIP-ID: {_none(p.get('id'))}",
        f"🏛 Funktion: {fn_str}",
        f"📅 Wahlperioden: {wp_str}",
        f"🔄 Aktualisiert: {str(p.get('aktualisiert', '–'))[:10]}",
    ]
    if person_roles:
        lines.append("")
        lines.append("**Rollen:**")
        if isinstance(person_roles, list):
            for role in person_roles[:10]:
                if isinstance(role, dict):
                    lines.append(f"  • {role.get('funktion', '–')} @ {role.get('organ', '–')} ({role.get('von', '–')} – {role.get('bis', 'heute')})")
                else:
                    lines.append(f"  • {str(role)}")
        else:
            lines.append(f"  {str(person_roles)[:200]}")
    return "\n".join(lines)


def format_bundestag_stats(data: dict) -> str:
    total = data.get("total", 0)
    by_typ = data.get("by_typ", [])
    by_thema = data.get("by_thema", [])
    lines = [f"📊 Bundestag-Statistiken — {total} Drucksachen gesamt\n"]
    lines.append("**Nach Typ:**")
    for t in by_typ[:10]:
        lines.append(f"  {_none(t.get('drucksachetyp'))}: {t.get('count', 0):,}")
    lines.append("")
    lines.append("**Nach Thema (LLM-Klassifikation):**")
    for t in by_thema[:15]:
        lines.append(f"  {_none(t.get('themen'))}: {t.get('count', 0):,}")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Handelsregister
# ---------------------------------------------------------------------------

def format_handelsregister_companies(data: dict, page: int, size: int) -> str:
    total = data.get("total", 0)
    results = data.get("results", [])
    lines = [f"🏢 Handelsregister-Unternehmen — {format_pagination(total, page, size)}\n"]
    for r in results:
        status_icon = "✅" if r.get("current_status") == "currently registered" else "❌"
        lines.append(f"{status_icon} **{_none(r.get('name'))}**")
        lines.append(
            f"   {_none(r.get('register_type'))} {_none(r.get('register_number'))} | "
            f"{_none(r.get('registrar'))} | {_none(r.get('federal_state'))}"
        )
        lines.append(f"   📍 {_none(r.get('registered_office'))} | Nr: {_none(r.get('company_number'))}")
        lines.append("")
    return "\n".join(lines)


def format_handelsregister_company(data: dict) -> str:
    c = data.get("company", {}) or {}
    officers = data.get("officers", []) or []
    status_icon = "✅" if c.get("current_status") == "currently registered" else "❌"
    lines = [
        f"{status_icon} **{_none(c.get('name'))}**",
        f"📋 {_none(c.get('register_type'))} {_none(c.get('register_number'))} | Gericht: {_none(c.get('registrar'))}",
        f"📍 {_none(c.get('registered_office'))} | {_none(c.get('federal_state'))}",
        f"🆔 Company-Nr: {_none(c.get('company_number'))}",
        f"📅 Abgerufen: {_none(c.get('retrieved_at'))}",
    ]
    if officers:
        lines.append("")
        lines.append(f"**Personen ({len(officers)}):**")
        for o in officers:
            dismissed = " [abberufen]" if o.get("dismissed") else ""
            lines.append(
                f"  • {_none(o.get('name'))} — {_none(o.get('position'))}{dismissed}"
                f" ({_none(o.get('start_date'))} – {_none(o.get('end_date'))})"
            )
    return "\n".join(lines)


def format_handelsregister_officers(data: dict, page: int, size: int) -> str:
    total = data.get("total", 0)
    results = data.get("results", [])
    lines = [f"👤 Handelsregister-Personen — {format_pagination(total, page, size)}\n"]
    for r in results:
        dismissed = " [abberufen]" if r.get("dismissed") else ""
        lines.append(f"• **{_none(r.get('name'))}** — {_none(r.get('position'))}{dismissed}")
        lines.append(
            f"  🏢 {_none(r.get('company_name'))} ({_none(r.get('company_number'))}) | "
            f"📍 {_none(r.get('city'))}"
        )
        lines.append(f"  📅 {_none(r.get('start_date'))} – {_none(r.get('end_date'))}")
        lines.append("")
    return "\n".join(lines)


def format_handelsregister_stats(data: dict) -> str:
    lines = [
        "📊 Handelsregister-Statistiken\n",
        f"Unternehmen gesamt: {data.get('total_companies', 0):,}",
        f"  Aktiv: {data.get('active_companies', 0):,}",
        f"  Gelöscht: {data.get('removed_companies', 0):,}",
        f"Personen gesamt: {data.get('total_officers', 0):,}",
        "",
        "**Nach Registerart:**",
    ]
    for r in data.get("by_register_type", []):
        lines.append(f"  {_none(r.get('type'))}: {r.get('count', 0):,}")
    lines.append("")
    lines.append("**Nach Bundesland:**")
    for r in data.get("by_federal_state", []):
        lines.append(f"  {_none(r.get('state'))}: {r.get('count', 0):,}")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Jobs (SAP/VW Stellenmarkt)
# ---------------------------------------------------------------------------

def format_jobs(data: dict, page: int) -> str:
    count = data.get("count", 0)
    results = data.get("results", [])
    lines = [f"💼 Stellenangebote (SAP/VW) — {count} auf dieser Seite\n"]
    for r in results:
        lines.append(
            f"• **{_none(r.get('work_area'))}** [{_none(r.get('employment_type'))}]"
        )
        lines.append(
            f"  🏢 Quelle: {_none(r.get('source')).upper()} | "
            f"📅 {_none(r.get('posted_date'))} | "
            f"📍 {_none(r.get('city'))}, {_none(r.get('country'))}"
        )
        lines.append(f"  Level: {_none(r.get('career_status'))} | ID: {_none(r.get('requisition_id'))}")
        lines.append("")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Arbeitsmarkt (BA-Jobbörse)
# ---------------------------------------------------------------------------

def format_arbeitsmarkt_jobs(data: dict, page: int, size: int) -> str:
    total = data.get("total")
    results = data.get("results", [])
    lines = [f"💼 Arbeitsmarkt-Stellenangebote — {format_pagination(total, page, size)}\n"]
    for r in results:
        lines.append(f"• **{_trunc(r.get('titel'), 100)}**")
        lines.append(
            f"  🏢 {_none(r.get('arbeitgeber'))} | 📍 {_none(r.get('ort'))} ({_none(r.get('plz'))}) | "
            f"📅 {_none(r.get('veroeffentlicht'))}"
        )
        lines.append(
            f"  🔖 {_none(r.get('beruf'))} | Branche: {_trunc(r.get('branche'), 60)} | "
            f"Ref: {_none(r.get('refnr'))}"
        )
        if r.get("eintrittsdatum"):
            lines.append(f"  Eintritt: {_none(r.get('eintrittsdatum'))}")
        lines.append("")
    return "\n".join(lines)


def format_arbeitsmarkt_stats(data: dict) -> str:
    timeline = data.get("timeline", [])
    lines = [f"📈 Arbeitsmarkt-Statistiken — letzte {data.get('days', 90)} Tage ({len(timeline)} Datenpunkte)\n"]
    if timeline:
        latest = timeline[0]
        lines.append(f"**Aktuell ({_none(latest.get('snapshot_date'))}):**")
        lines.append(f"  Gesamt: {latest.get('total_jobs', 0):,} Stellen")
        lines.append(f"  Neu: +{latest.get('new_jobs', 0):,} | Entfernt: -{latest.get('removed_jobs', 0):,}")
        lines.append("")
        lines.append("**Verlauf (letzte 10 Tage):**")
        for row in timeline[:10]:
            lines.append(
                f"  {_none(row.get('snapshot_date'))}: "
                f"{row.get('total_jobs', 0):,} gesamt, "
                f"+{row.get('new_jobs', 0):,} neu"
            )
    return "\n".join(lines)


def format_arbeitsmarkt_facets(data: dict) -> str:
    results = data.get("results", [])
    snapshot_date = data.get("snapshot_date", "–")
    lines = [f"📊 Arbeitsmarkt-Facetten — Stand: {snapshot_date}\n"]
    current_type = None
    for r in results:
        facet_type = r.get("facet_type", "")
        if facet_type != current_type:
            current_type = facet_type
            lines.append(f"**{facet_type}:**")
        lines.append(f"  {_none(r.get('facet_label') or r.get('facet_key'))}: {r.get('count', 0):,}")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Energie
# ---------------------------------------------------------------------------

def format_energie_timeseries(data: dict) -> str:
    count = data.get("count", 0)
    results = data.get("results", [])
    lines = [f"⚡ SMARD Zeitreihendaten — {count} Datenpunkte\n"]
    if results:
        filter_name = results[0].get("filter_name", "–")
        lines.append(f"**Datenreihe: {filter_name}**\n")
        for r in results[:20]:
            val = r.get("value_mwh")
            val_str = f"{val:,.1f} MWh" if val is not None else "–"
            lines.append(f"  {_none(r.get('datetime_utc'))[:16]}: {val_str}")
        if count > 20:
            lines.append(f"  … und {count - 20} weitere Datenpunkte")
    return "\n".join(lines)


def format_energie_filters(data: dict) -> str:
    results = data.get("results", [])
    lines = [f"⚡ SMARD Filter — {len(results)} verfügbar\n"]
    for r in results:
        lines.append(
            f"  ID {r.get('filter_id'):>5}: {_none(r.get('filter_name'))} "
            f"(letzter Datenpunkt: {str(r.get('last_datetime_utc', '–'))[:10]})"
        )
    return "\n".join(lines)


def format_energie_mastr_snapshot(data: dict) -> str:
    results = data.get("results", [])
    snapshot_date = data.get("snapshot_date", "–")
    lines = [f"🔋 MaStR-Snapshot — Stand: {snapshot_date}\n"]
    for r in results:
        cap = r.get("capacity_kw")
        cap_str = f"{cap / 1_000_000:,.1f} GW" if cap is not None else "–"
        lines.append(
            f"  {_none(r.get('energietraeger_name'))} | {_none(r.get('bundesland_name'))}: "
            f"{r.get('count', 0):,} Anlagen, {cap_str}"
        )
    return "\n".join(lines)


def format_energie_mastr_totals(data: dict) -> str:
    results = data.get("results", [])
    lines = [f"🔋 MaStR Gesamtzahlen — {len(results)} Datenpunkte\n"]
    for r in results[:15]:
        is_full = "✅" if r.get("is_full") else "⏳"
        lines.append(
            f"  {is_full} {_none(r.get('snapshot_date'))}: "
            f"{r.get('total_count', 0):,} Anlagen"
            + (f" | Balkon: {r.get('balkon_count', 0):,}" if r.get("balkon_count") else "")
        )
    if len(results) > 15:
        lines.append(f"  … und {len(results) - 15} weitere")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Förderung
# ---------------------------------------------------------------------------

def format_foerderung_programme(data: dict, page: int, size: int) -> str:
    total = data.get("total", 0)
    results = data.get("results", [])
    lines = [f"💶 Förderprogramme — {format_pagination(total, page, size)}\n"]
    for r in results:
        active = "✅" if r.get("is_active") else "❌"
        lines.append(f"{active} **{_none(r.get('title'))}**")
        lines.append(
            f"   Fördergeber: {_none(r.get('foerdergeber'))} | "
            f"Bereich: {_trunc(r.get('foerderbereich'), 60)}"
        )
        if r.get("kurztext"):
            lines.append(f"   {_trunc(r.get('kurztext'), 200)}")
        lines.append(f"   🔗 {_none(r.get('url'))}")
        lines.append("")
    return "\n".join(lines)


def format_foerderung_programm(data: dict) -> str:
    lines = [
        f"💶 **{_none(data.get('title'))}**",
        f"🌐 {_none(data.get('url'))}",
        f"Fördergeber: {_none(data.get('foerdergeber'))}",
        f"Bereich: {_none(data.get('foerderbereich'))}",
        f"Gebiet: {_none(data.get('foerdergebiet'))}",
        f"Berechtigte: {_none(data.get('foerderberechtigte'))}",
        f"Art: {_none(data.get('foerderart'))}",
        f"Unternehmensgröße: {_none(data.get('unternehmensgroesse'))}",
        f"Aktiv: {'✅' if data.get('is_active') else '❌'}",
        f"Aktualisiert: {_none(data.get('updated_at'))}",
    ]
    if data.get("kurztext"):
        lines.append(f"\n**Kurztext:**\n{_trunc(data.get('kurztext'), 1000)}")
    if data.get("beschreibung"):
        lines.append(f"\n**Beschreibung:**\n{_trunc(data.get('beschreibung'), 1000)}")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Vergabe
# ---------------------------------------------------------------------------

def format_vergabe_ausschreibungen(data: dict, page: int, size: int) -> str:
    total = data.get("total", 0)
    results = data.get("results", [])
    lines = [f"📋 Ausschreibungen — {format_pagination(total, page, size)}\n"]
    for r in results:
        lines.append(f"• **{_trunc(r.get('title'), 120)}**")
        lines.append(
            f"  🏢 {_trunc(r.get('organisation_name'), 60)} | "
            f"📜 {_none(r.get('contracting_rule'))} | "
            f"📅 {_none(r.get('publishing_date'))}"
        )
        if r.get("relevant_date"):
            lines.append(f"  ⏰ Frist: {_none(r.get('relevant_date'))}")
        if r.get("detail_url"):
            lines.append(f"  🔗 {_none(r.get('detail_url'))}")
        lines.append("")
    return "\n".join(lines)


def format_vergabe_auftraggeber(data: dict) -> str:
    results = data.get("results", [])
    lines = [f"🏢 Top-Auftraggeber — {len(results)} Einträge\n"]
    for r in results:
        lines.append(
            f"• **{_none(r.get('name'))}** — "
            f"{r.get('active_announcements', 0)} aktiv / "
            f"{r.get('total_announcements', 0)} gesamt"
        )
    return "\n".join(lines)


def format_vergabe_stats(data: dict) -> str:
    lines = [
        "📊 Vergabe-Statistiken\n",
        f"Gesamt: {data.get('total', 0):,} Bekanntmachungen",
        f"Aktive Ausschreibungen: {data.get('active', 0):,}",
        f"Ø Fristlänge: {data.get('avg_frist_days', 0):.1f} Tage",
        "",
        "**Nach Typ:**",
    ]
    for t in data.get("by_type", []):
        lines.append(f"  {_none(t.get('publication_type'))}: {t.get('count', 0):,}")
    lines.append("")
    lines.append("**Nach Vergaberecht:**")
    for t in data.get("by_rule", []):
        lines.append(f"  {_none(t.get('contracting_rule'))}: {t.get('count', 0):,}")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Luftqualität
# ---------------------------------------------------------------------------

def format_luftqualitaet_stationen(data: dict) -> str:
    results = data.get("results", [])
    lines = [f"🌬 Luftqualitäts-Messstationen — {len(results)} Stationen\n"]
    for r in results:
        active = "✅" if not r.get("active_to") else "❌"
        lines.append(
            f"{active} **{_none(r.get('name'))}** (ID: {r.get('id')}) "
            f"— {_none(r.get('city'))} | Netz: {_none(r.get('network_name'))}"
        )
        lines.append(f"   Typ: {_none(r.get('type_name'))} | Lage: {_none(r.get('setting_name'))}")
    return "\n".join(lines)


def format_luftqualitaet_messungen(data: dict, page: int, size: int) -> str:
    total = data.get("total", 0)
    results = data.get("results", [])
    lines = [f"🌬 Luftqualitäts-Messungen — {format_pagination(total, page, size)}\n"]
    for r in results:
        val = r.get("value")
        val_str = f"{val:.2f}" if val is not None else "–"
        lines.append(
            f"• {_none(r.get('measured_at'))[:16]} | "
            f"Station: {_none(r.get('station_name'))} ({_none(r.get('city'))}) | "
            f"Schadstoff-ID {r.get('component_id')}: {val_str}"
        )
    return "\n".join(lines)


def format_luftqualitaet_ueberschreitungen(data: dict) -> str:
    results = data.get("results", [])
    lines = [f"⚠️ Grenzwertüberschreitungen — {len(results)} Einträge\n"]
    for r in results:
        lines.append(
            f"• **{_none(r.get('station_name'))}** ({_none(r.get('city'))}) "
            f"| Jahr: {_none(r.get('year'))} | Schadstoff-ID: {r.get('component_id')} "
            f"| {r.get('total_count', 0)} Überschreitungen"
        )
        months = [r.get(f"month_{i:02d}", 0) or 0 for i in range(1, 13)]
        month_str = " ".join(f"{m:>3}" for m in months)
        lines.append(f"  Monate: {month_str}")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# TED (Tenders Electronic Daily — EU-Ausschreibungen)
# ---------------------------------------------------------------------------

def format_ted_notices(data: dict, page: int, size: int) -> str:
    total = data.get("total", 0)
    items = data.get("items", [])
    lines = [f"🇪🇺 TED EU-Ausschreibungen — {format_pagination(total, page, size)}\n"]
    for r in items:
        type_icon = {"CN": "📋", "CAN": "✅", "PIN": "📌"}.get(r.get("notice_type", ""), "📄")
        lines.append(
            f"{type_icon} **{_none(r.get('publication_number'))}** "
            f"[{_none(r.get('notice_type'))} / {_none(r.get('form_type'))}]"
        )
        lines.append(
            f"  🏢 {_trunc(r.get('buyer_name'), 60)} | "
            f"📍 {_none(r.get('buyer_city'))}, {_none(r.get('buyer_country'))}"
        )
        if r.get("winner_name"):
            lines.append(f"  🏆 Gewinner: {_trunc(r.get('winner_name'), 60)}")
        val = r.get("total_value")
        cur = r.get("total_value_cur", "")
        if val is not None:
            lines.append(f"  💶 {float(val):,.0f} {cur}")
        lines.append(
            f"  🏷 CPV: {_none(r.get('cpv_main'))} | "
            f"Art: {_none(r.get('contract_nature'))} | "
            f"Verfahren: {_none(r.get('procedure_type'))}"
        )
        lines.append(f"  📅 {_none(r.get('publication_date'))}")
        if r.get("html_url"):
            lines.append(f"  🔗 {_none(r.get('html_url'))}")
        lines.append("")
    return "\n".join(lines)


def format_ted_stats(data: dict) -> str:
    lines = [
        "📊 TED EU-Vergabe — Statistiken\n",
        f"Bekanntmachungen gesamt: {data.get('total_notices', 0):,}",
        "",
        "**Nach Typ:**",
    ]
    for k, v in (data.get("notice_types") or {}).items():
        label = {"CN": "Contract Notice", "CAN": "Contract Award Notice", "PIN": "Prior Info Notice"}.get(k, k)
        lines.append(f"  {k} ({label}): {v:,}")
    lines.append("")
    lines.append("**Nach Vertragsart:**")
    for k, v in (data.get("contract_natures") or {}).items():
        lines.append(f"  {_none(k)}: {v:,}")
    avg = data.get("avg_value_eur")
    total_val = data.get("total_value_eur")
    if avg is not None:
        lines.append(f"\nØ Auftragswert (EUR): {avg:,.0f} €")
    if total_val is not None:
        lines.append(f"Gesamtvolumen (EUR): {total_val:,.0f} €")
    lines.append("")
    lines.append("**Top CPV-Codes:**")
    for entry in (data.get("top_cpv") or [])[:10]:
        lines.append(f"  {_none(entry.get('cpv'))}: {entry.get('count', 0):,}")
    return "\n".join(lines)


def format_ted_buyer(data: list) -> str:
    lines = [f"🏢 TED Top-Auftraggeber — {len(data)} Einträge\n"]
    for i, r in enumerate(data, 1):
        val = r.get("total_value_eur")
        val_str = f" | 💶 {float(val):,.0f} €" if val is not None else ""
        lines.append(
            f"{i:>3}. **{_none(r.get('buyer_name'))}** ({_none(r.get('buyer_country'))}) "
            f"— {r.get('notice_count', 0):,} Ausschreibungen{val_str}"
        )
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Composite Tools
# ---------------------------------------------------------------------------

def _format_section_header(icon: str, title: str) -> str:
    """Hilfsfunktion: formatiert einen Abschnitts-Header."""
    return f"\n{icon} **{title}**\n{'─' * 40}"


def format_composite_company_360(
    name: str,
    hr: dict,
    ba: dict,
    news: dict,
) -> str:
    """360°-Unternehmensprofil: Handelsregister + Bundesanzeiger + News."""
    lines = [f"🔭 **360° Unternehmensprofil: {name}**\n"]

    # --- Handelsregister ---
    lines.append(_format_section_header("🏢", "Handelsregister"))
    if not hr.get("ok"):
        lines.append(f"  ❌ {hr.get('error', 'Fehler')}")
    else:
        data = hr["data"]
        results = data.get("results", [])
        total = data.get("total", 0)
        if not results:
            lines.append("  Keine Einträge gefunden.")
        else:
            lines.append(f"  {total} Treffer im Handelsregister:\n")
            for r in results:
                status = "✅" if r.get("current_status") == "currently registered" else "❌"
                lines.append(
                    f"  {status} **{_none(r.get('name'))}**\n"
                    f"     {_none(r.get('register_type'))} {_none(r.get('register_number'))} | "
                    f"{_none(r.get('registrar'))} | {_none(r.get('federal_state'))}\n"
                    f"     Sitz: {_none(r.get('registered_office'))} | Nr: {_none(r.get('company_number'))}"
                )

    # --- Bundesanzeiger ---
    lines.append(_format_section_header("📰", "Bundesanzeiger (Jahresabschlüsse)"))
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
                    lines.append(f"    💬 {_trunc(highlights[0].replace('<mark>', '«').replace('</mark>', '»'), 200)}")

    # --- News ---
    lines.append(_format_section_header("📡", "Aktuelle Nachrichten"))
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


def format_composite_markt_radar(
    beruf: str,
    region: str | None,
    jobs: dict,
    facets: dict,
    vergabe: dict,
) -> str:
    """Marktüberblick: Arbeitsmarkt + Facetten + Vergabe."""
    region_info = f" | Region: {region}" if region else ""
    lines = [f"📡 **Markt-Radar: {beruf}{region_info}**\n"]

    # --- Stellenangebote ---
    lines.append(_format_section_header("💼", "Aktuelle Stellenangebote"))
    if not jobs.get("ok"):
        lines.append(f"  ❌ {jobs.get('error', 'Fehler')}")
    else:
        data = jobs["data"]
        results = data.get("results", [])
        total = data.get("total")
        total_str = f"{total:,}" if total is not None else "?"
        if not results:
            lines.append("  Keine Stellenangebote gefunden.")
        else:
            lines.append(f"  {total_str} Stellen insgesamt:\n")
            for r in results:
                lines.append(
                    f"  • **{_trunc(r.get('titel'), 90)}**\n"
                    f"    🏢 {_none(r.get('arbeitgeber'))} | 📍 {_none(r.get('ort'))} | "
                    f"📅 {_none(r.get('veroeffentlicht'))}"
                )

    # --- Facetten-Überblick ---
    lines.append(_format_section_header("📊", "Markt-Facetten (Arbeitsmarkt gesamt)"))
    if not facets.get("ok"):
        lines.append(f"  ❌ {facets.get('error', 'Fehler')}")
    else:
        data = facets["data"]
        results = data.get("results", [])
        # Zeige max 5 pro Facettentyp
        current_type: str | None = None
        count_in_type = 0
        for r in results:
            ftype = r.get("facet_type", "")
            if ftype != current_type:
                current_type = ftype
                count_in_type = 0
                lines.append(f"\n  **{ftype}:**")
            if count_in_type < 5:
                label = r.get("facet_label") or r.get("facet_key") or "–"
                lines.append(f"    {label}: {r.get('count', 0):,}")
                count_in_type += 1

    # --- Öffentliche Ausschreibungen ---
    lines.append(_format_section_header("📋", "Öffentliche Ausschreibungen"))
    if not vergabe.get("ok"):
        lines.append(f"  ❌ {vergabe.get('error', 'Fehler')}")
    else:
        data = vergabe["data"]
        results = data.get("results", [])
        total = data.get("total", 0)
        if not results:
            lines.append("  Keine Ausschreibungen gefunden.")
        else:
            lines.append(f"  {total} Ausschreibungen:\n")
            for r in results:
                lines.append(
                    f"  • **{_trunc(r.get('title'), 90)}**\n"
                    f"    🏢 {_trunc(r.get('organisation_name'), 50)} | "
                    f"📅 {_none(r.get('publishing_date'))}"
                    + (f" | ⏰ Frist: {_none(r.get('relevant_date'))}" if r.get("relevant_date") else "")
                )

    return "\n".join(lines)


def format_composite_region_dashboard(
    bundesland: str,
    mastr: dict,
    luft: dict,
    arbeitsmarkt: dict,
    vergabe: dict,
) -> str:
    """Standortprofil: Energie + Luft + Arbeitsmarkt + Vergabe."""
    lines = [f"🗺 **Standortprofil: {bundesland}**\n"]

    # --- Energie / MaStR ---
    lines.append(_format_section_header("⚡", "Energie-Infrastruktur (MaStR)"))
    if not mastr.get("ok"):
        lines.append(f"  ❌ {mastr.get('error', 'Fehler')}")
    else:
        data = mastr["data"]
        results = data.get("results", [])
        snapshot_date = data.get("snapshot_date", "–")
        if not results:
            lines.append(f"  Keine MaStR-Daten für {bundesland}.")
        else:
            lines.append(f"  Stand: {snapshot_date}\n")
            for r in results:
                cap = r.get("capacity_kw")
                cap_str = f"{cap / 1_000_000:,.1f} GW" if cap is not None else "–"
                lines.append(
                    f"  • {_none(r.get('energietraeger_name'))}: "
                    f"{r.get('count', 0):,} Anlagen | {cap_str}"
                )

    # --- Luftqualität ---
    lines.append(_format_section_header("🌬", "Luftqualitäts-Messstationen"))
    if not luft.get("ok"):
        lines.append(f"  ❌ {luft.get('error', 'Fehler')}")
    else:
        data = luft["data"]
        results = data.get("results", [])
        if not results:
            lines.append(f"  Keine Messstationen für {bundesland}.")
        else:
            active = [r for r in results if not r.get("active_to")]
            lines.append(f"  {len(results)} Stationen ({len(active)} aktiv):\n")
            for r in results[:5]:
                status = "✅" if not r.get("active_to") else "❌"
                lines.append(
                    f"  {status} {_none(r.get('name'))} — {_none(r.get('city'))} "
                    f"| Netz: {_none(r.get('network_name'))}"
                )
            if len(results) > 5:
                lines.append(f"  … und {len(results) - 5} weitere Stationen")

    # --- Arbeitsmarkt ---
    lines.append(_format_section_header("💼", "Arbeitsmarkt (bundesweit aktuell)"))
    if not arbeitsmarkt.get("ok"):
        lines.append(f"  ❌ {arbeitsmarkt.get('error', 'Fehler')}")
    else:
        data = arbeitsmarkt["data"]
        timeline = data.get("timeline", [])
        if timeline:
            latest = timeline[0]
            lines.append(
                f"  Stand: {_none(latest.get('snapshot_date'))}\n"
                f"  Stellenangebote gesamt: {latest.get('total_jobs', 0):,}\n"
                f"  Neu: +{latest.get('new_jobs', 0):,} | Entfernt: -{latest.get('removed_jobs', 0):,}"
            )
        else:
            lines.append("  Keine Arbeitsmarktdaten verfügbar.")

    # --- Vergabe ---
    lines.append(_format_section_header("📋", "Vergabe-Statistiken"))
    if not vergabe.get("ok"):
        lines.append(f"  ❌ {vergabe.get('error', 'Fehler')}")
    else:
        data = vergabe["data"]
        lines.append(
            f"  Ausschreibungen gesamt: {data.get('total', 0):,}\n"
            f"  Aktive Ausschreibungen: {data.get('active', 0):,}\n"
            f"  Ø Fristlänge: {data.get('avg_frist_days', 0):.1f} Tage"
        )

    return "\n".join(lines)


def format_composite_foerder_match(
    beschreibung: str,
    rechtsform: str | None,
    unternehmensgroesse: str | None,
    foerderung: dict,
) -> str:
    """Förderprogramm-Matching: Formatiert als Matching-Ergebnis."""
    lines = [f"💶 **Förder-Matching: {_trunc(beschreibung, 80)}**\n"]
    if rechtsform:
        lines.append(f"  Rechtsform: {rechtsform}")
    if unternehmensgroesse:
        lines.append(f"  Unternehmensgröße: {unternehmensgroesse}")
    lines.append("")

    if not foerderung.get("ok"):
        lines.append(format_error(foerderung.get("error", "Fehler")))
        return "\n".join(lines)

    data = foerderung["data"]
    results = data.get("results", [])
    total = data.get("total", 0)

    if not results:
        lines.append("❌ Keine passenden Förderprogramme gefunden.")
        lines.append("💡 Tipp: Versuche allgemeinere Suchbegriffe.")
        return "\n".join(lines)

    lines.append(f"✅ {total} Förderprogramme gefunden (zeige top {len(results)}):\n")

    for i, r in enumerate(results, 1):
        active = "✅ Aktiv" if r.get("is_active") else "❌ Inaktiv"
        lines.append(f"**{i}. {_none(r.get('title'))}** [{active}]")
        lines.append(f"   💼 Fördergeber: {_none(r.get('foerdergeber'))}")
        lines.append(f"   🎯 Bereich: {_trunc(r.get('foerderbereich'), 80)}")
        if r.get("foerderberechtigte"):
            lines.append(f"   👥 Berechtigte: {_trunc(r.get('foerderberechtigte'), 80)}")
        if r.get("unternehmensgroesse"):
            ug = r.get("unternehmensgroesse")
            match_icon = "✓" if unternehmensgroesse and unternehmensgroesse.lower() in str(ug).lower() else "→"
            lines.append(f"   {match_icon} Unternehmensgröße: {_trunc(str(ug), 60)}")
        if r.get("kurztext"):
            lines.append(f"   📝 {_trunc(r.get('kurztext'), 200)}")
        lines.append(f"   🔗 {_none(r.get('url'))}")
        lines.append("")

    if total > len(results):
        lines.append(f"💡 Weitere {total - len(results)} Programme über bundestag_list_foerderprogramme abrufbar.")

    return "\n".join(lines)


def format_composite_person_profil(
    name: str,
    officers: dict,
    companies: list,
    news: dict,
) -> str:
    """Personenprofil: Mandate + Firmendaten + News."""
    lines = [f"🔍 **Personenprofil: {name}**\n"]

    # --- Mandate im Handelsregister ---
    lines.append(_format_section_header("📋", "Handelsregister-Mandate"))
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

    # --- Unternehmensprofil der Top-3-Firmen ---
    if companies:
        lines.append(_format_section_header("🏢", "Verknüpfte Unternehmen (Details)"))
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

    # --- Nachrichten ---
    lines.append(_format_section_header("📡", "Aktuelle Nachrichten"))
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


def format_composite_energie_trend(
    days: int,
    smard: dict,
    mastr: dict,
) -> str:
    """Energie-Trend: SMARD-Erzeugung + MaStR-Zubau kombiniert."""
    lines = [f"⚡ **Energie-Trend (letzte {days} Tage)**\n"]

    # --- SMARD-Erzeugung ---
    lines.append(_format_section_header("🏭", "Stromerzeugung (SMARD)"))
    if not smard.get("ok"):
        lines.append(f"  ❌ {smard.get('error', 'Fehler')}")
    else:
        data = smard["data"]
        results = data.get("results", [])
        count = data.get("count", len(results))
        if not results:
            lines.append("  Keine SMARD-Daten verfügbar.")
        else:
            filter_name = results[0].get("filter_name", "Gesamt")
            values = [r.get("value_mwh") for r in results if r.get("value_mwh") is not None]
            if values:
                total_mwh = sum(values)
                avg_mwh = total_mwh / len(values)
                lines.append(
                    f"  Datenreihe: {filter_name}\n"
                    f"  Datenpunkte: {count}\n"
                    f"  Ø pro Zeitpunkt: {avg_mwh:,.0f} MWh\n"
                    f"  Gesamt: {total_mwh / 1_000_000:,.2f} TWh\n"
                )
            lines.append("  Letzten 10 Datenpunkte:")
            for r in results[:10]:
                val = r.get("value_mwh")
                val_str = f"{val:,.0f} MWh" if val is not None else "–"
                lines.append(f"    {str(r.get('datetime_utc', ''))[:16]}: {val_str}")

    # --- MaStR-Zubau ---
    lines.append(_format_section_header("🔋", "Anlagenzubau (MaStR)"))
    if not mastr.get("ok"):
        lines.append(f"  ❌ {mastr.get('error', 'Fehler')}")
    else:
        data = mastr["data"]
        results = data.get("results", [])
        if not results:
            lines.append("  Keine MaStR-Zubaudaten verfügbar.")
        else:
            lines.append(f"  {len(results)} Snapshots:\n")
            for r in results[:10]:
                is_full = "✅" if r.get("is_full") else "⏳"
                lines.append(
                    f"  {is_full} {_none(r.get('snapshot_date'))}: "
                    f"{r.get('total_count', 0):,} Anlagen"
                    + (f" | Balkon: {r.get('balkon_count', 0):,}" if r.get("balkon_count") else "")
                )

    return "\n".join(lines)


def format_composite_arbeitsmarkt_trend(days: int, stats: dict) -> str:
    """Arbeitsmarkt-Trend mit Highlights (max, min, Durchschnitt)."""
    lines = [f"📈 **Arbeitsmarkt-Trend (letzte {days} Tage)**\n"]

    if not stats.get("ok"):
        lines.append(format_error(stats.get("error", "Fehler")))
        return "\n".join(lines)

    data = stats["data"]
    timeline = data.get("timeline", [])

    if not timeline:
        lines.append("  Keine Zeitreihendaten verfügbar.")
        return "\n".join(lines)

    totals = [r.get("total_jobs") for r in timeline if r.get("total_jobs") is not None]
    new_jobs = [r.get("new_jobs") for r in timeline if r.get("new_jobs") is not None]

    if totals:
        max_val = max(totals)
        min_val = min(totals)
        avg_val = sum(totals) / len(totals)
        max_date = next((r.get("snapshot_date") for r in timeline if r.get("total_jobs") == max_val), "–")
        min_date = next((r.get("snapshot_date") for r in timeline if r.get("total_jobs") == min_val), "–")

        lines.append(f"**Highlights ({len(timeline)} Datenpunkte):**\n")
        lines.append(f"  📈 Maximum: {max_val:,} am {max_date}")
        lines.append(f"  📉 Minimum: {min_val:,} am {min_date}")
        lines.append(f"  📊 Durchschnitt: {avg_val:,.0f}")
        if new_jobs:
            lines.append(f"  ➕ Ø neue Stellen/Tag: {sum(new_jobs) / len(new_jobs):,.0f}")
        lines.append("")

    # Aktuellste Werte
    latest = timeline[0]
    lines.append(f"**Aktuell ({_none(latest.get('snapshot_date'))}):**")
    lines.append(f"  Gesamt: {latest.get('total_jobs', 0):,} Stellen")
    lines.append(f"  Neu: +{latest.get('new_jobs', 0):,} | Entfernt: -{latest.get('removed_jobs', 0):,}")
    lines.append("")

    # Verlauf (letzte 10)
    lines.append("**Verlauf (letzte 10 Snapshots):**")
    for row in timeline[:10]:
        total = row.get("total_jobs", 0)
        new = row.get("new_jobs", 0)
        bar_len = int((total / max(totals)) * 20) if totals else 0
        bar = "█" * bar_len
        lines.append(
            f"  {_none(row.get('snapshot_date'))}: {total:>8,} |{bar}"
            f" +{new:,}"
        )

    return "\n".join(lines)


def format_composite_vergabe_trend(
    days: int,
    q: str | None,
    ausschreibungen: dict,
    stats: dict,
) -> str:
    """Vergabe-Trend: Ausschreibungsaktivität + Statistiken."""
    filter_info = f" | Filter: '{q}'" if q else ""
    lines = [f"📋 **Vergabe-Trend (letzte {days} Tage{filter_info})**\n"]

    # --- Statistiken ---
    lines.append(_format_section_header("📊", "Gesamtstatistiken"))
    if not stats.get("ok"):
        lines.append(f"  ❌ {stats.get('error', 'Fehler')}")
    else:
        data = stats["data"]
        lines.append(
            f"  Ausschreibungen gesamt: {data.get('total', 0):,}\n"
            f"  Aktive Ausschreibungen: {data.get('active', 0):,}\n"
            f"  Ø Fristlänge: {data.get('avg_frist_days', 0):.1f} Tage\n"
        )
        if data.get("by_type"):
            lines.append("  **Nach Typ:**")
            for t in data["by_type"][:5]:
                lines.append(f"    {_none(t.get('publication_type'))}: {t.get('count', 0):,}")
        if data.get("by_rule"):
            lines.append("\n  **Nach Vergaberecht:**")
            for t in data["by_rule"][:5]:
                lines.append(f"    {_none(t.get('contracting_rule'))}: {t.get('count', 0):,}")

    # --- Aktuelle Ausschreibungen ---
    lines.append(_format_section_header("📄", "Aktuelle Ausschreibungen"))
    if not ausschreibungen.get("ok"):
        lines.append(f"  ❌ {ausschreibungen.get('error', 'Fehler')}")
    else:
        data = ausschreibungen["data"]
        results = data.get("results", [])
        total = data.get("total", 0)
        if not results:
            lines.append("  Keine Ausschreibungen gefunden.")
        else:
            lines.append(f"  {total} Treffer (zeige {len(results)}):\n")
            for r in results[:20]:
                lines.append(
                    f"  • **{_trunc(r.get('title'), 100)}**\n"
                    f"    🏢 {_trunc(r.get('organisation_name'), 60)} | "
                    f"📅 {_none(r.get('publishing_date'))}"
                    + (f" | ⏰ Frist: {_none(r.get('relevant_date'))}" if r.get("relevant_date") else "")
                )

    return "\n".join(lines)
