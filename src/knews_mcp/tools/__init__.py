"""MCP Tool-Definitionen für die knews Datenplattform."""

from .bundesanzeiger import BUNDESANZEIGER_TOOLS, handle_bundesanzeiger
from .handelsregister import HANDELSREGISTER_TOOLS, handle_handelsregister
from .news import NEWS_TOOLS, handle_news
from .bundestag import BUNDESTAG_TOOLS, handle_bundestag
from .jobs import JOBS_TOOLS, handle_jobs
from .arbeitsmarkt import ARBEITSMARKT_TOOLS, handle_arbeitsmarkt
from .energie import ENERGIE_TOOLS, handle_energie
from .foerderung import FOERDERUNG_TOOLS, handle_foerderung
from .vergabe import VERGABE_TOOLS, handle_vergabe
from .luftqualitaet import LUFTQUALITAET_TOOLS, handle_luftqualitaet
from .ted import TED_TOOLS, handle_ted
from .blaulicht import BLAULICHT_TOOLS, handle_blaulicht
from .insolvenzen import INSOLVENZEN_TOOLS, handle_insolvenzen
from .parteispenden import PARTEISPENDEN_TOOLS, handle_parteispenden
from .rechtsprechung import RECHTSPRECHUNG_TOOLS, handle_rechtsprechung
from .zwangsversteigerungen import ZWANGSVERSTEIGERUNGEN_TOOLS, handle_zwangsversteigerungen
from .composite import COMPOSITE_TOOLS, handle_composite

__all__ = [
    "BUNDESANZEIGER_TOOLS", "handle_bundesanzeiger",
    "HANDELSREGISTER_TOOLS", "handle_handelsregister",
    "NEWS_TOOLS", "handle_news",
    "BUNDESTAG_TOOLS", "handle_bundestag",
    "JOBS_TOOLS", "handle_jobs",
    "ARBEITSMARKT_TOOLS", "handle_arbeitsmarkt",
    "ENERGIE_TOOLS", "handle_energie",
    "FOERDERUNG_TOOLS", "handle_foerderung",
    "VERGABE_TOOLS", "handle_vergabe",
    "LUFTQUALITAET_TOOLS", "handle_luftqualitaet",
    "TED_TOOLS", "handle_ted",
    "BLAULICHT_TOOLS", "handle_blaulicht",
    "INSOLVENZEN_TOOLS", "handle_insolvenzen",
    "PARTEISPENDEN_TOOLS", "handle_parteispenden",
    "RECHTSPRECHUNG_TOOLS", "handle_rechtsprechung",
    "ZWANGSVERSTEIGERUNGEN_TOOLS", "handle_zwangsversteigerungen",
    "COMPOSITE_TOOLS", "handle_composite",
]

ALL_TOOLS = (
    BUNDESANZEIGER_TOOLS
    + HANDELSREGISTER_TOOLS
    + NEWS_TOOLS
    + BUNDESTAG_TOOLS
    + JOBS_TOOLS
    + ARBEITSMARKT_TOOLS
    + ENERGIE_TOOLS
    + FOERDERUNG_TOOLS
    + VERGABE_TOOLS
    + LUFTQUALITAET_TOOLS
    + TED_TOOLS
    + BLAULICHT_TOOLS
    + INSOLVENZEN_TOOLS
    + PARTEISPENDEN_TOOLS
    + RECHTSPRECHUNG_TOOLS
    + ZWANGSVERSTEIGERUNGEN_TOOLS
    + COMPOSITE_TOOLS
)

TOOL_HANDLERS = {
    **{t.name: handle_bundesanzeiger for t in BUNDESANZEIGER_TOOLS},
    **{t.name: handle_handelsregister for t in HANDELSREGISTER_TOOLS},
    **{t.name: handle_news for t in NEWS_TOOLS},
    **{t.name: handle_bundestag for t in BUNDESTAG_TOOLS},
    **{t.name: handle_jobs for t in JOBS_TOOLS},
    **{t.name: handle_arbeitsmarkt for t in ARBEITSMARKT_TOOLS},
    **{t.name: handle_energie for t in ENERGIE_TOOLS},
    **{t.name: handle_foerderung for t in FOERDERUNG_TOOLS},
    **{t.name: handle_vergabe for t in VERGABE_TOOLS},
    **{t.name: handle_luftqualitaet for t in LUFTQUALITAET_TOOLS},
    **{t.name: handle_ted for t in TED_TOOLS},
    **{t.name: handle_blaulicht for t in BLAULICHT_TOOLS},
    **{t.name: handle_insolvenzen for t in INSOLVENZEN_TOOLS},
    **{t.name: handle_parteispenden for t in PARTEISPENDEN_TOOLS},
    **{t.name: handle_rechtsprechung for t in RECHTSPRECHUNG_TOOLS},
    **{t.name: handle_zwangsversteigerungen for t in ZWANGSVERSTEIGERUNGEN_TOOLS},
    **{t.name: handle_composite for t in COMPOSITE_TOOLS},
}
