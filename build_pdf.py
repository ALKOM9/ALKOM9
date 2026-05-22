"""Build a Hebrew PDF book from the Streamlit course by mock-executing each page.

Strategy: build a fake `streamlit` module that captures every output call
(markdown/write/info/dataframe/metric/etc.) into a flat list of blocks,
turns widgets into return-the-default stubs, and noops the interactive
bits (plotly charts, FRED data, RRG). Then `runpy.run_path()` each page —
loops, f-strings, glossary list comprehensions, and `phase_to_sectors()`
calls all execute naturally and produce the same Hebrew text the live
site would.

What ends up in the PDF: all teaching text, all 11 sector deep-dives,
all 8 macro indicator cards, the position calculator (default phase),
glossary (all ~60 terms), every quiz with answers.

What's stubbed: live FRED values (placeholder "—"), backtest equity
curves, RRG quadrant table (the data needs network).
"""
from __future__ import annotations

import builtins
import io
import runpy
import sys
import types
from pathlib import Path

import markdown
import pandas as pd
from weasyprint import HTML, CSS

COURSE_DIR = Path(__file__).parent / "sector-rotation-course"
PAGES_DIR = COURSE_DIR / "pages"
APP_FILE = COURSE_DIR / "app.py"
OUT_PDF = Path(__file__).parent / "sector-rotation-course.pdf"


# ============================ CAPTURE BUFFER ============================

BLOCKS: list[dict] = []


def emit(block: dict) -> None:
    BLOCKS.append(block)


def clear_blocks() -> None:
    BLOCKS.clear()


# ============================ MOCK STREAMLIT ============================


class _Ctx:
    """Generic context manager that does nothing (for st.container/sidebar/columns/tabs)."""

    def __init__(self, on_enter=None, on_exit=None):
        self._on_enter = on_enter
        self._on_exit = on_exit

    def __enter__(self):
        if self._on_enter:
            self._on_enter()
        return self

    def __exit__(self, *exc):
        if self._on_exit:
            self._on_exit()
        return False


class _Expander(_Ctx):
    def __init__(self, label: str, expanded: bool = False):
        super().__init__(
            on_enter=lambda: emit({"type": "expander_open", "text": label}),
            on_exit=lambda: emit({"type": "expander_close"}),
        )


class _ColumnList(list):
    """st.columns(...) returns a list of context managers. We just use plain _Ctx for each."""


def _strip_html(s: str) -> str:
    """Drop simple <div style=...> wrappers; keep the inner text but as plain markdown."""
    import re as _re
    s = _re.sub(r"<br\s*/?>", "  \n", s, flags=_re.I)
    s = _re.sub(r"</?(div|span|p|small)[^>]*>", "", s, flags=_re.I)
    return s


def _txt(x) -> str:
    if x is None:
        return ""
    if isinstance(x, str):
        return x
    return str(x)


def _md(text, *_, **kwargs):
    s = _strip_html(_txt(text))
    if not s.strip():
        return
    emit({"type": "md", "text": s})


def _write(*args, **kwargs):
    for a in args:
        if isinstance(a, pd.DataFrame):
            emit({"type": "df", "df": a})
        elif isinstance(a, pd.Series):
            emit({"type": "df", "df": a.to_frame()})
        elif isinstance(a, str):
            emit({"type": "md", "text": _strip_html(a)})
        else:
            emit({"type": "md", "text": _strip_html(str(a))})


def _callout(flavor):
    def fn(text, *_, **__):
        emit({"type": "callout", "flavor": flavor, "text": _strip_html(_txt(text))})
    return fn


def _heading(level):
    def fn(text, *_, **__):
        emit({"type": f"h{level}", "text": _txt(text)})
    return fn


def _caption(text, *_, **__):
    emit({"type": "caption", "text": _strip_html(_txt(text))})


def _divider():
    emit({"type": "hr"})


def _metric(label, value, delta=None, **kwargs):
    emit({"type": "metric", "label": _txt(label), "value": _txt(value), "delta": _txt(delta) if delta is not None else None})


def _dataframe(data, *_, **__):
    if isinstance(data, pd.DataFrame):
        emit({"type": "df", "df": data})
    elif isinstance(data, pd.Series):
        emit({"type": "df", "df": data.to_frame()})
    elif isinstance(data, dict):
        emit({"type": "df", "df": pd.DataFrame(data)})
    else:
        try:
            emit({"type": "df", "df": pd.DataFrame(data)})
        except Exception:
            emit({"type": "md", "text": str(data)})


def _table(data, *_, **__):
    _dataframe(data)


def _code(body, language=None, **__):
    emit({"type": "code", "text": _txt(body), "lang": language or ""})


def _latex(body, **__):
    emit({"type": "code", "text": _txt(body), "lang": "latex"})


def _plotly_chart(*_, **__):
    emit({"type": "chart_stub"})


def _line_chart(*_, **__):
    emit({"type": "chart_stub"})


def _bar_chart(*_, **__):
    emit({"type": "chart_stub"})


def _area_chart(*_, **__):
    emit({"type": "chart_stub"})


def _image(*_, **__):
    pass


def _columns(spec, **__):
    n = spec if isinstance(spec, int) else len(spec) if hasattr(spec, "__len__") else 2
    return [_Ctx() for _ in range(n)]


def _tabs(labels, **__):
    # Render all tabs sequentially with a header
    ctxs = []
    for label in labels:
        ctxs.append(_Ctx(
            on_enter=lambda lbl=label: emit({"type": "h4", "text": f"📑 {lbl}"}),
        ))
    return ctxs


def _container(border=False, **__):
    return _Ctx()


def _expander(label, expanded=False):
    return _Expander(label, expanded)


def _empty():
    return _Ctx()


def _spinner(text=""):
    return _Ctx()


def _form(key=None, **__):
    return _Ctx()


def _popover(label, **__):
    return _Ctx(on_enter=lambda: emit({"type": "h4", "text": f"🔍 {label}"}))


# Widgets — return default values so downstream code keeps flowing.
def _selectbox(label, options, index=0, **kwargs):
    opts = list(options) if not isinstance(options, list) else options
    if not opts:
        return None
    if index is None:
        index = 0
    return opts[index]


def _radio(label, options, index=0, **kwargs):
    return _selectbox(label, options, index)


def _multiselect(label, options, default=None, **kwargs):
    if default is not None:
        return list(default)
    return list(options)


def _checkbox(label, value=False, **kwargs):
    return bool(value)


def _toggle(label, value=False, **kwargs):
    return bool(value)


def _button(label, **kwargs):
    return False


def _download_button(*args, **kwargs):
    return False


def _slider(label, min_value=0, max_value=100, value=None, step=None, **kwargs):
    if value is not None:
        return value
    if min_value is not None:
        return min_value
    return 0


def _number_input(label, min_value=None, max_value=None, value=None, **kwargs):
    if value is not None:
        return value
    if min_value is not None:
        return min_value
    return 0


def _text_input(label, value="", **kwargs):
    return value


def _text_area(label, value="", **kwargs):
    return value


def _date_input(label, value=None, **kwargs):
    return value


def _file_uploader(*args, **kwargs):
    return None


def _color_picker(label, value="#000000", **kwargs):
    return value


# Cache decorators – just return the function unchanged
def _cache_passthrough(*dargs, **dkwargs):
    if len(dargs) == 1 and callable(dargs[0]) and not dkwargs:
        return dargs[0]

    def wrap(f):
        return f

    return wrap


# Session state – minimal dict-like
class _SessionState(dict):
    def __getattr__(self, k):
        return self.get(k)

    def __setattr__(self, k, v):
        self[k] = v


def _stop():
    # In normal Streamlit this halts the page. In capture mode we just raise
    # a sentinel that the top-level catches.
    raise _StopExecution()


class _StopExecution(Exception):
    pass


def build_st_module() -> types.ModuleType:
    m = types.ModuleType("streamlit")
    m.set_page_config = lambda **_: None
    m.markdown = _md
    m.write = _write
    m.info = _callout("info")
    m.warning = _callout("warn")
    m.success = _callout("ok")
    m.error = _callout("err")
    m.exception = _callout("err")
    m.title = _heading(1)
    m.header = _heading(2)
    m.subheader = _heading(3)
    m.caption = _caption
    m.divider = _divider
    m.metric = _metric
    m.dataframe = _dataframe
    m.table = _table
    m.code = _code
    m.latex = _latex
    m.json = lambda obj, **_: _code(__import__("json").dumps(obj, ensure_ascii=False, indent=2), "json")
    m.plotly_chart = _plotly_chart
    m.altair_chart = _plotly_chart
    m.line_chart = _line_chart
    m.bar_chart = _bar_chart
    m.area_chart = _area_chart
    m.pyplot = _plotly_chart
    m.image = _image
    m.video = lambda *a, **k: None
    m.audio = lambda *a, **k: None
    m.map = lambda *a, **k: None
    m.toast = lambda *a, **k: None
    m.balloons = lambda: None
    m.snow = lambda: None
    m.columns = _columns
    m.tabs = _tabs
    m.container = _container
    m.expander = _expander
    m.empty = _empty
    m.spinner = _spinner
    m.form = _form
    m.popover = _popover
    m.form_submit_button = _button
    m.selectbox = _selectbox
    m.radio = _radio
    m.multiselect = _multiselect
    m.checkbox = _checkbox
    m.toggle = _toggle
    m.button = _button
    m.download_button = _download_button
    m.link_button = lambda label, url, **k: None
    m.slider = _slider
    m.select_slider = lambda label, options, value=None, **k: (value if value is not None else (list(options)[0] if options else None))
    m.number_input = _number_input
    m.text_input = _text_input
    m.text_area = _text_area
    m.date_input = _date_input
    m.time_input = lambda *a, **k: None
    m.file_uploader = _file_uploader
    m.color_picker = _color_picker
    m.camera_input = lambda *a, **k: None
    m.chat_input = lambda *a, **k: None
    m.cache_data = _cache_passthrough
    m.cache_resource = _cache_passthrough
    m.cache = _cache_passthrough
    m.session_state = _SessionState()
    m.secrets = {}
    m.query_params = {}
    m.experimental_get_query_params = lambda: {}
    m.experimental_set_query_params = lambda **_: None
    m.stop = _stop
    m.rerun = lambda: None
    m.experimental_rerun = lambda: None

    # sidebar is itself a module-like object with the same API
    sidebar = types.SimpleNamespace(
        markdown=_md, write=_write, info=_callout("info"), warning=_callout("warn"),
        success=_callout("ok"), error=_callout("err"), title=_heading(1),
        header=_heading(2), subheader=_heading(3), caption=_caption, divider=_divider,
        metric=_metric, dataframe=_dataframe, table=_table, code=_code,
        plotly_chart=_plotly_chart, image=_image, columns=_columns, tabs=_tabs,
        container=_container, expander=_expander, empty=_empty, spinner=_spinner,
        selectbox=_selectbox, radio=_radio, multiselect=_multiselect,
        checkbox=_checkbox, toggle=_toggle, button=_button, slider=_slider,
        number_input=_number_input, text_input=_text_input, text_area=_text_area,
        date_input=_date_input, file_uploader=_file_uploader,
    )

    class _SidebarCM:
        def __enter__(self):
            return sidebar

        def __exit__(self, *e):
            return False

        def __getattr__(self, k):
            return getattr(sidebar, k)

    m.sidebar = _SidebarCM()

    # custom render_quiz hookpoint: not used since render_quiz lives in utils
    return m


# ============================ MOCK utils.auth / consent ============================


def install_module(name: str, attrs: dict) -> None:
    m = types.ModuleType(name)
    for k, v in attrs.items():
        setattr(m, k, v)
    sys.modules[name] = m


def install_quiz_capture():
    """Override utils.quiz.render_quiz to capture quiz data."""
    def render_quiz(module_key, questions):
        emit({"type": "quiz", "key": module_key, "questions": questions})

    install_module("utils.quiz", {"render_quiz": render_quiz})


# ============================ RENDER ============================

MD = markdown.Markdown(extensions=["extra", "sane_lists", "tables"])


def md_to_html(text: str) -> str:
    MD.reset()
    return MD.convert(text.strip())


def escape(s: str | None) -> str:
    if s is None:
        return ""
    return _txt(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def df_to_html(df: pd.DataFrame) -> str:
    try:
        # Use pandas built-in HTML rendering but unescape Hebrew + keep simple
        return df.to_html(index=False, border=0, classes="dftbl", escape=True)
    except Exception:
        return "<pre>" + escape(str(df)) + "</pre>"


def render_quiz_block(qs: list[dict]) -> str:
    out = ["<div class='quiz'><h3>🧠 חידון</h3>"]
    answers = []
    for i, q in enumerate(qs, 1):
        if not q.get("q") or not q.get("options"):
            continue
        out.append(f"<div class='q'><p><strong>שאלה {i}.</strong> {escape(q['q'])}</p><ol class='qopts'>")
        for opt in q["options"]:
            out.append(f"<li>{escape(opt)}</li>")
        out.append("</ol></div>")
        ans = q.get("answer")
        if isinstance(ans, int) and 0 <= ans < len(q["options"]):
            letter = "אבגדהוז"[ans] if ans < 7 else str(ans + 1)
            answers.append((i, letter, q["options"][ans], q.get("explain") or ""))
    out.append("<div class='answers'><h4>✅ תשובות</h4><ol>")
    for i, letter, correct, expl in answers:
        out.append(f"<li><strong>שאלה {i}:</strong> ({letter}) {escape(correct)}. {escape(expl)}</li>")
    out.append("</ol></div></div>")
    return "\n".join(out)


def blocks_to_html(blocks: list[dict]) -> str:
    out: list[str] = []
    for b in blocks:
        t = b["type"]
        if t in ("h1", "h2", "h3", "h4"):
            out.append(f"<{t}>{escape(b['text'])}</{t}>")
        elif t == "md":
            out.append(md_to_html(b["text"]))
        elif t == "callout":
            cls = "callout " + b.get("flavor", "info")
            out.append(f"<div class='{cls}'>{md_to_html(b['text'])}</div>")
        elif t == "caption":
            out.append(f"<p class='caption'>{md_to_html(b['text'])}</p>" if "**" in b["text"] or "[" in b["text"] else f"<p class='caption'>{escape(b['text'])}</p>")
        elif t == "hr":
            out.append("<hr/>")
        elif t == "metric":
            delta = f" <span class='delta'>({escape(b['delta'])})</span>" if b.get("delta") else ""
            out.append(f"<div class='metric'><span class='m-label'>{escape(b['label'])}:</span> <span class='m-value'>{escape(b['value'])}</span>{delta}</div>")
        elif t == "df":
            out.append(f"<div class='dfwrap'>{df_to_html(b['df'])}</div>")
        elif t == "code":
            lang = b.get("lang", "")
            out.append(f"<pre><code class='lang-{escape(lang)}'>{escape(b['text'])}</code></pre>")
        elif t == "chart_stub":
            out.append("<p class='chart-stub'>📊 [גרף אינטראקטיבי – זמין בגרסה החיה של הקורס]</p>")
        elif t == "expander_open":
            out.append(f"<div class='expander'><h4 class='expander-title'>▸ {escape(b['text'])}</h4><div class='expander-body'>")
        elif t == "expander_close":
            out.append("</div></div>")
        elif t == "quiz":
            out.append(render_quiz_block(b["questions"]))
    return "\n".join(out)


# ============================ MAIN PIPELINE ============================

MODULES = [
    ("app.py",                                 "ברוכים הבאים"),
    ("pages/1_מודול_1_Business_Cycle.py",     "מודול 1 – Business Cycle"),
    ("pages/2_מודול_2_מיפוי_סקטורים.py",     "מודול 2 – מיפוי סקטורים"),
    ("pages/3_מודול_3_הסיבוב_הקלאסי.py",     "מודול 3 – הסיבוב הקלאסי"),
    ("pages/4_מודול_4_Macro_Dashboard.py",     "מודול 4 – Macro Dashboard"),
    ("pages/5_מודול_5_Relative_Strength.py",   "מודול 5 – Relative Strength + RRG"),
    ("pages/6_מודול_6_יישום.py",               "מודול 6 – יישום"),
    ("pages/7_מודול_7_Backtest.py",            "מודול 7 – Backtest"),
    ("pages/8_מודול_8_שילוב_בתיק.py",         "מודול 8 – שילוב בתיק"),
    ("pages/9_מילון_מונחים.py",                "מילון מונחים"),
]


def setup_mocks():
    """Install streamlit + auth/consent + quiz mocks before importing any page."""
    sys.modules["streamlit"] = build_st_module()
    install_module("utils.auth", {
        "require_password": lambda: None,
        "logout_button": lambda: None,
    })
    install_module("utils.consent", {
        "require_consent": lambda: None,
    })
    install_quiz_capture()
    install_data_mocks()


def install_data_mocks():
    """Patch utils.fred / utils.market with synthetic data so pages render fully."""
    import numpy as np
    sys.path.insert(0, str(COURSE_DIR))
    import utils.fred as fred_mod
    import utils.market as market_mod

    def _series_df(start="2000-01-01", base=100.0, drift=0.0, noise=1.0):
        idx = pd.date_range(start=start, end=pd.Timestamp("2026-05-01"), freq="MS")
        n = len(idx)
        rng = np.random.default_rng(seed=42)
        vals = base + drift * np.arange(n) + noise * rng.standard_normal(n).cumsum() * 0.3
        return pd.DataFrame({"value": vals}, index=idx)

    def fake_get_many(series_ids, start="2000-01-01"):
        out = {}
        for sid in series_ids:
            if sid == "T10Y2Y": out[sid] = _series_df(start, base=0.5, drift=-0.0005, noise=0.3)
            elif sid == "UNRATE": out[sid] = _series_df(start, base=4.0, drift=0.001, noise=0.4)
            elif sid == "CPIAUCSL": out[sid] = _series_df(start, base=200, drift=0.4, noise=0.3)
            elif sid == "INDPRO": out[sid] = _series_df(start, base=100, drift=0.05, noise=0.3)
            elif sid == "BAMLH0A0HYM2": out[sid] = _series_df(start, base=4.0, drift=0.001, noise=0.3)
            elif sid == "FEDFUNDS": out[sid] = _series_df(start, base=2.0, drift=0.003, noise=0.2)
            elif sid == "ICSA": out[sid] = _series_df(start, base=220_000, drift=-50, noise=2000)
            elif sid == "UMCSENT": out[sid] = _series_df(start, base=80, drift=-0.02, noise=2)
            else: out[sid] = _series_df(start)
        return out

    fred_mod.get_many = fake_get_many
    fred_mod.get_series = lambda sid, start="2000-01-01": fake_get_many([sid], start)[sid]
    fred_mod._get_api_key = lambda: "demo"

    def fake_get_prices(tickers, period="5y", interval="1wk"):
        idx = pd.date_range(end=pd.Timestamp("2026-05-01"), periods=260, freq="W-FRI")
        rng = np.random.default_rng(seed=7)
        cols = {}
        for i, t in enumerate(tickers):
            r = rng.standard_normal(len(idx)) * 0.02 + 0.001 * (1 + (i % 5))
            cols[t] = 100.0 * np.exp(np.cumsum(r))
        return pd.DataFrame(cols, index=idx)

    market_mod.get_prices = fake_get_prices

    def fake_get_sector_prices(period="5y", interval="1wk"):
        return fake_get_prices(list(market_mod.SECTORS.keys()) + [market_mod.BENCHMARK], period, interval)

    market_mod.get_sector_prices = fake_get_sector_prices


def render_one(path: Path) -> list[dict]:
    clear_blocks()
    # The page does `from utils.page import bootstrap` which imports utils.auth/consent –
    # already mocked. fred/yfinance etc. are imported lazily inside utils.* – when those
    # try to fetch data they'll fail gracefully because the page handles empty DataFrames.
    sys.path.insert(0, str(COURSE_DIR))
    try:
        runpy.run_path(str(path), run_name="__main__")
    except _StopExecution:
        pass
    except Exception as e:
        emit({"type": "callout", "flavor": "warn", "text": f"_(הרינדור של חלק זה נכשל בגרסת ה-PDF: {type(e).__name__}: {e}. הסעיף זמין בגרסה החיה.)_"})
    finally:
        sys.path.pop(0)
    return list(BLOCKS)


CSS_TEXT = """
@page { size: A4; margin: 18mm 15mm 18mm 15mm;
    @bottom-center { content: counter(page) " / " counter(pages);
        font-family: 'Noto Sans Hebrew',sans-serif; font-size: 9pt; color: #777; } }
@page :first { @bottom-center { content: ""; } }
html, body { direction: rtl; font-family: 'Noto Sans Hebrew','Noto Sans',sans-serif;
    font-size: 10.5pt; line-height: 1.55; color: #1a1a1a; }
h1,h2,h3,h4 { color: #0d3b66; line-height: 1.25; page-break-after: avoid; }
h1 { font-size: 22pt; margin: 0.5em 0 0.4em; border-bottom: 2px solid #0d3b66; padding-bottom: 0.2em; }
h2 { font-size: 15pt; margin-top: 1em; }
h3 { font-size: 12.5pt; margin-top: 0.9em; }
h4 { font-size: 11.2pt; margin-top: 0.7em; }
p.caption { color: #555; font-style: italic; font-size: 9.5pt; margin: 0.2em 0 0.6em; }
p.chart-stub { color: #777; font-style: italic; background:#fafafa; padding:0.5em; border:1px dashed #ccc; border-radius:4px; text-align:center; }
.module { page-break-before: always; }
.cover { text-align: center; margin-top: 4cm; }
.cover h1 { border:none; font-size:30pt; margin-bottom:0.3em; }
.cover .subtitle { font-size:14pt; color:#666; }
.cover .meta { margin-top:5cm; font-size:10pt; color:#888; }
hr { border:none; border-top:1px solid #ccc; margin: 1.2em 0; }
code,pre { font-family:'DejaVu Sans Mono',monospace; direction:ltr; unicode-bidi:embed; text-align:left;
    background:#f3f3f3; border-radius:4px; }
pre { padding:0.6em 0.8em; font-size:9.5pt; page-break-inside: avoid; white-space: pre-wrap; }
code { padding:0.1em 0.3em; font-size:0.9em; }
pre code { background:none; padding:0; font-size:9.5pt; }
.callout { border-radius:6px; padding:0.55em 0.85em; margin:0.6em 0; border-right:4px solid;
    page-break-inside:avoid; }
.callout.info { background:#eaf2fb; border-color:#2b73c2; }
.callout.warn { background:#fff5e0; border-color:#d68a00; }
.callout.ok   { background:#e7f6ec; border-color:#2c9a4a; }
.callout.err  { background:#fbe9e7; border-color:#c0392b; }
.expander { margin:0.7em 0; border:1px solid #ddd; border-radius:6px; padding:0.25em 0.8em 0.5em;
    page-break-inside: avoid; background: #fcfcfc; }
.expander-title { color:#444; margin:0.4em 0; font-size:11pt; }
.expander-body { font-size:10pt; color:#222; }
.metric { background:#f7f9fc; padding:0.35em 0.6em; border-radius:4px; margin:0.3em 0;
    page-break-inside:avoid; display:block; }
.m-label { color:#555; }
.m-value { font-weight:700; color:#0d3b66; }
.delta { color:#666; font-size:0.9em; }
ul,ol { padding-right:1.5em; padding-left:0; }
.dfwrap { overflow-x:hidden; margin:0.7em 0; }
table.dftbl, table { border-collapse:collapse; width:100%; font-size:9.5pt;
    page-break-inside: avoid; }
table.dftbl th, table.dftbl td, th, td { border:1px solid #ccc; padding:0.3em 0.45em; text-align:right; }
table.dftbl th, th { background:#f0f4f8; font-weight:700; }
strong { color:#0d3b66; }
.quiz { background:#fafafa; border:1px solid #e0e0e0; border-radius:8px;
    padding:0.9em 1.1em; margin:0.9em 0; page-break-inside: avoid; }
.quiz h3,.quiz h4 { color:#5b21b6; }
.quiz .q { margin-bottom:0.5em; page-break-inside:avoid; }
.qopts { list-style: hebrew; }
.answers { margin-top:0.9em; background:#f0fdf4; border:1px solid #bbf7d0;
    border-radius:6px; padding:0.6em 0.9em; }
blockquote { border-right:4px solid #aaa; margin:0.6em 0; padding:0.1em 0.85em; background:#f7f7f7; color:#444; }
"""


def cover() -> str:
    return """
<section class='cover'>
  <h1>🔄 Sector Rotation</h1>
  <p class='subtitle'>קורס אינטראקטיבי בעברית – גרסת קריאה (PDF)</p>
  <p class='subtitle'>8 מודולים · מילון מונחים · כל החידונים עם תשובות</p>
  <p class='meta'>הופק במלואו מהקוד של הקורס באמצעות הרצה מבוקרת – כולל כל הלולאות, התרחישים והטבלאות.</p>
  <p class='meta'>גרפים אינטראקטיביים ונתוני FRED חיים זמינים רק בגרסה החיה.</p>
  <p class='meta'><strong>אזהרה:</strong> הקורס למטרות חינוכיות בלבד. אינו ייעוץ פיננסי. ביצועי עבר אינם מבטיחים ביצועי עתיד.</p>
</section>
"""


def toc(titles: list[str]) -> str:
    items = "".join(f"<li>{escape(t)}</li>" for t in titles)
    return f"<section class='module'><h1>תוכן עניינים</h1><ol>{items}</ol></section>"


def main() -> int:
    setup_mocks()

    sections = [cover()]
    titles = [t for _, t in MODULES]
    sections.append(toc(titles))

    for rel, title in MODULES:
        p = COURSE_DIR / rel
        if not p.exists():
            print(f"missing: {p}", file=sys.stderr)
            continue
        print(f"rendering {rel} ...")
        blocks = render_one(p)
        body = blocks_to_html(blocks)
        sections.append(f"<section class='module'>{body}</section>")

    html = f"""<!DOCTYPE html>
<html lang="he" dir="rtl"><head><meta charset="utf-8"></head><body>
{''.join(sections)}
</body></html>"""

    Path("/tmp/course.html").write_text(html, encoding="utf-8")

    HTML(string=html, base_url=str(COURSE_DIR)).write_pdf(
        str(OUT_PDF), stylesheets=[CSS(string=CSS_TEXT)]
    )
    size_kb = OUT_PDF.stat().st_size / 1024
    print(f"OK: {OUT_PDF} ({size_kb:.0f} KB)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
