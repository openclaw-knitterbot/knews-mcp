"""
MCP Tools für die Epstein Files (declassified DOJ case documents).

Scope required: all
ES-only index: epstein-000001 (bilingual analyzer EN+DE)
"""

from mcp.types import TextContent, Tool

from ..client import api_get
from ..formatting import format_error

EPSTEIN_TOOLS = [
    Tool(
        name="epstein_search",
        description=(
            "Volltextsuche in den Epstein Files (Elasticsearch, bilingual EN/DE). "
            "Durchsucht gerichtlich freigegebene Dokumente aus dem Epstein-Komplex: "
            "Zeugenaussagen, Gerichtsakten, E-Mails, Flugprotokolle, Deposition-Transcripte. "
            "12 Datensätze (datasets 1–12), mehrere tausend Dokumente. "
            "Nützlich für: Personenrecherche (Maxwell, Prince Andrew, Clinton, Trump, …), "
            "Orte (Epstein-Insel, Palm Beach, New York), Ereignisse, Daten.\n\n"
            "Full-text search in declassified Jeffrey Epstein case documents from the DOJ. "
            "Covers depositions, court filings, emails, flight logs, transcripts."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "q": {
                    "type": "string",
                    "description": (
                        "Suchbegriff (z.B. 'Ghislaine Maxwell flight logs', 'Prince Andrew', "
                        "'Palm Beach estate', 'recruitment')"
                    ),
                },
                "dataset": {
                    "type": "integer",
                    "description": "Datensatz-Filter 1–12 (optional — ohne Filter = alle Datensätze)",
                    "minimum": 1,
                    "maximum": 12,
                },
                "text_method": {
                    "type": "string",
                    "description": "Extraktionsmethode: 'native' (durchsuchbares PDF), 'ocr' (gescannt), 'empty' (kein Text)",
                    "enum": ["native", "ocr", "empty"],
                },
                "size": {
                    "type": "integer",
                    "description": "Anzahl Ergebnisse (Standard: 20, max: 200)",
                    "default": 20,
                    "minimum": 1,
                    "maximum": 200,
                },
            },
            "required": ["q"],
        },
    ),
    Tool(
        name="epstein_documents",
        description=(
            "Listet Epstein-Dokumente (Metadaten ohne Volltext, paginiert). "
            "Filterbar nach Datensatz, Extraktionsmethode und Scrape-Datum. "
            "Nützlich für: Überblick welche Dokumente vorhanden sind, "
            "Datensatz-Exploration, Metadaten-Analyse.\n\n"
            "List Epstein case documents (metadata only, paginated). "
            "Filter by dataset, text method, and scrape date."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "dataset": {
                    "type": "integer",
                    "description": "Datensatz-Filter 1–12",
                    "minimum": 1,
                    "maximum": 12,
                },
                "text_method": {
                    "type": "string",
                    "description": "Extraktionsmethode: 'native', 'ocr', 'empty'",
                    "enum": ["native", "ocr", "empty"],
                },
                "scraped_after": {
                    "type": "string",
                    "description": "Nur Dokumente gescrapt nach (ISO-Datum, z.B. 2024-01-01)",
                    "pattern": "^\\d{4}-\\d{2}-\\d{2}$",
                },
                "limit": {
                    "type": "integer",
                    "description": "Anzahl Ergebnisse (Standard: 50, max: 500)",
                    "default": 50,
                    "minimum": 1,
                    "maximum": 500,
                },
                "offset": {
                    "type": "integer",
                    "description": "Pagination Offset (Standard: 0)",
                    "default": 0,
                    "minimum": 0,
                },
            },
        },
    ),
    Tool(
        name="epstein_get_document",
        description=(
            "Ruft ein einzelnes Epstein-Dokument mit vollständigem Extraktionstext ab. "
            "Benötigt die doc_id aus epstein_search oder epstein_documents. "
            "Nützlich für: Volltext lesen, Dokument-Details, vollständige Transkripte.\n\n"
            "Retrieve a single Epstein document by ID including full extracted text."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "doc_id": {
                    "type": "string",
                    "description": "Dokument-ID (aus epstein_search oder epstein_documents, z.B. 'epstein_d01_0042')",
                },
            },
            "required": ["doc_id"],
        },
    ),
    Tool(
        name="epstein_stats",
        description=(
            "Statistiken zu den Epstein Files: Gesamtzahl Dokumente, Aufschlüsselung nach "
            "Datensatz und Extraktionsmethode, durchschnittliche Seitenanzahl, Gesamtgröße.\n\n"
            "Statistics on the Epstein Files: totals, breakdown by dataset and text method."
        ),
        inputSchema={
            "type": "object",
            "properties": {},
        },
    ),
]


async def handle_epstein(name: str, arguments: dict) -> list[TextContent]:
    if name == "epstein_search":
        result = await api_get(
            "/v1/epstein/search",
            params={
                "q": arguments["q"],
                "dataset": arguments.get("dataset"),
                "text_method": arguments.get("text_method"),
                "size": arguments.get("size", 20),
            },
        )
        if not result["ok"]:
            return [TextContent(type="text", text=format_error(result["error"]))]
        return [TextContent(type="text", text=_format_epstein_search(result["data"]))]

    elif name == "epstein_documents":
        result = await api_get(
            "/v1/epstein/documents",
            params={
                "dataset": arguments.get("dataset"),
                "text_method": arguments.get("text_method"),
                "scraped_after": arguments.get("scraped_after"),
                "limit": arguments.get("limit", 50),
                "offset": arguments.get("offset", 0),
            },
        )
        if not result["ok"]:
            return [TextContent(type="text", text=format_error(result["error"]))]
        return [TextContent(type="text", text=_format_epstein_documents(result["data"]))]

    elif name == "epstein_get_document":
        doc_id = arguments["doc_id"]
        result = await api_get(f"/v1/epstein/documents/{doc_id}")
        if not result["ok"]:
            return [TextContent(type="text", text=format_error(result["error"]))]
        return [TextContent(type="text", text=_format_epstein_document(result["data"]))]

    elif name == "epstein_stats":
        result = await api_get("/v1/epstein/stats")
        if not result["ok"]:
            return [TextContent(type="text", text=format_error(result["error"]))]
        return [TextContent(type="text", text=_format_epstein_stats(result["data"]))]

    return [TextContent(type="text", text=format_error(f"Unbekanntes Tool: {name}"))]


# ---------------------------------------------------------------------------
# Formatting
# ---------------------------------------------------------------------------

def _trunc(s, maxlen=300):
    if not s:
        return ""
    s = str(s).strip()
    return s[:maxlen] + "…" if len(s) > maxlen else s


def _none(v, fallback="–"):
    if v is None or v == "":
        return fallback
    return str(v)


def _format_epstein_search(data: dict) -> str:
    total = data.get("total", 0)
    results = data.get("results", [])
    lines = [f"🔍 Epstein Files — {total} Treffer\n"]
    for r in results:
        doc_id = _none(r.get("doc_id"))
        title = _none(r.get("pdf_title") or r.get("filename"), "Unbenannt")
        dataset = _none(r.get("dataset"))
        method = _none(r.get("text_method"))
        pages = _none(r.get("page_count"))
        lines.append(f"📄 **{title}**")
        lines.append(f"   ID: `{doc_id}` | Dataset {dataset} | {method} | {pages} Seiten")
        if r.get("pdf_author"):
            lines.append(f"   Autor: {r['pdf_author']}")
        # Highlights
        hl = r.get("highlights", {})
        for field_highlights in hl.values():
            if field_highlights:
                snippet = field_highlights[0].replace("<mark>", "«").replace("</mark>", "»")
                lines.append(f"   💬 {_trunc(snippet, 250)}")
                break
        lines.append("")
    return "\n".join(lines)


def _format_epstein_documents(data: dict) -> str:
    total = data.get("total", 0)
    results = data.get("results", [])
    lines = [f"📂 Epstein Documents — {total} gesamt\n"]
    for r in results:
        doc_id = _none(r.get("doc_id"))
        title = _none(r.get("pdf_title") or r.get("filename"), "Unbenannt")
        dataset = _none(r.get("dataset"))
        method = _none(r.get("text_method"))
        pages = _none(r.get("page_count"))
        size_mb = round(r.get("file_size_bytes", 0) / 1024 / 1024, 1) if r.get("file_size_bytes") else "–"
        lines.append(f"📄 **{title}**  [{doc_id}]")
        lines.append(f"   Dataset {dataset} | {method} | {pages} S. | {size_mb} MB")
        lines.append("")
    return "\n".join(lines)


def _format_epstein_document(data: dict) -> str:
    doc_id = _none(data.get("doc_id"))
    title = _none(data.get("pdf_title") or data.get("filename"), "Unbenannt")
    dataset = _none(data.get("dataset"))
    method = _none(data.get("text_method"))
    pages = _none(data.get("page_count"))
    size_mb = round(data.get("file_size_bytes", 0) / 1024 / 1024, 1) if data.get("file_size_bytes") else "–"
    text = data.get("text", "")

    lines = [
        f"📄 **{title}**",
        f"ID: `{doc_id}` | Dataset {dataset} | {method} | {pages} Seiten | {size_mb} MB",
    ]
    if data.get("pdf_author"):
        lines.append(f"Autor: {data['pdf_author']}")
    if data.get("pdf_subject"):
        lines.append(f"Betreff: {data['pdf_subject']}")
    if data.get("pdf_keywords"):
        lines.append(f"Keywords: {data['pdf_keywords']}")
    if data.get("original_url"):
        lines.append(f"URL: {data['original_url']}")
    lines.append(f"Gescrapt: {_none(data.get('scraped_at'))}")
    lines.append("")
    if text:
        lines.append("**Volltext:**")
        lines.append(text[:8000] + ("…[gekürzt]" if len(text) > 8000 else ""))
    else:
        lines.append("*(kein extrahierter Text verfügbar)*")
    return "\n".join(lines)


def _format_epstein_stats(data: dict) -> str:
    lines = [
        "📊 Epstein Files — Statistiken\n",
        f"Dokumente gesamt: {data.get('total', 0):,}",
        f"Durchschn. Seitenanzahl: {data.get('avg_page_count', 0):.1f}",
        f"Gesamtgröße: {data.get('total_size_gb', 0):.2f} GB",
        "",
        "**Nach Datensatz:**",
    ]
    for item in data.get("by_dataset", []):
        lines.append(f"  Dataset {_none(item.get('dataset'))}: {item.get('count', 0):,} Dokumente")
    lines.append("")
    lines.append("**Nach Extraktionsmethode:**")
    for item in data.get("by_text_method", []):
        lines.append(f"  {_none(item.get('text_method'))}: {item.get('count', 0):,}")
    return "\n".join(lines)
