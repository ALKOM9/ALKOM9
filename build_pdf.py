"""Build a Hebrew PDF book from the Streamlit course pages.

Parses each pages/*.py file with the `ast` module, extracts the Hebrew
educational content (markdown blocks, headers, expanders, quiz data),
renders to HTML with proper RTL + Hebrew font, and prints to PDF via
WeasyPrint.

Loses: interactive widgets, live charts, the FRED dashboard, the RRG, the
backtester. Keeps: ~95% of the teaching text and all quizzes.
"""
from __future__ import annotations

import ast
import re
import sys
from pathlib import Path

import markdown
from weasyprint import HTML, CSS

COURSE_DIR = Path(__file__).parent / "sector-rotation-course"
PAGES_DIR = COURSE_DIR / "pages"
APP_FILE = COURSE_DIR / "app.py"
OUT_PDF = Path(__file__).parent / "sector-rotation-course.pdf"


# ----------------------------- AST EXTRACTION -----------------------------

# Functions whose first string argument is content we want to capture.
CONTENT_CALLS = {
    "st.markdown",
    "st.write",
    "st.info",
    "st.warning",
    "st.success",
    "st.error",
    "st.caption",
}
TITLE_CALLS = {"st.title", "st.header", "st.subheader"}
EXPANDER_CALL = "st.expander"
PAGE_HEADER_CALL = "page_header"


def _node_to_str(node: ast.AST) -> str | None:
    """Return string value if node is a constant string, else None."""
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    if isinstance(node, ast.JoinedStr):  # f-strings - take literal parts
        parts = []
        for v in node.values:
            if isinstance(v, ast.Constant):
                parts.append(str(v.value))
            else:
                parts.append("…")
        return "".join(parts)
    return None


def _call_name(node: ast.Call) -> str:
    """Return dotted name of the call target, e.g. 'st.markdown' or 'page_header'."""
    f = node.func
    if isinstance(f, ast.Attribute):
        parts = []
        cur = f
        while isinstance(cur, ast.Attribute):
            parts.append(cur.attr)
            cur = cur.value
        if isinstance(cur, ast.Name):
            parts.append(cur.id)
        return ".".join(reversed(parts))
    if isinstance(f, ast.Name):
        return f.id
    return ""


def _extract_quiz_questions(node: ast.Call) -> list[dict] | None:
    """If node is render_quiz(key, [...]), return the question list."""
    if _call_name(node) != "render_quiz":
        return None
    if len(node.args) < 2:
        return None
    qlist = node.args[1]
    if not isinstance(qlist, ast.List):
        return None
    questions = []
    for elt in qlist.elts:
        if not isinstance(elt, ast.Dict):
            continue
        q = {}
        for key_node, val_node in zip(elt.keys, elt.values):
            k = _node_to_str(key_node)
            if k == "q":
                q["q"] = _node_to_str(val_node)
            elif k == "options":
                if isinstance(val_node, ast.List):
                    q["options"] = [_node_to_str(o) for o in val_node.elts]
            elif k == "answer":
                if isinstance(val_node, ast.Constant):
                    q["answer"] = val_node.value
            elif k == "explain":
                q["explain"] = _node_to_str(val_node)
        if q:
            questions.append(q)
    return questions


def extract_blocks(source: str) -> list[dict]:
    """Walk AST, return ordered list of blocks: title/markdown/expander/quiz."""
    tree = ast.parse(source)
    blocks: list[dict] = []

    def visit(node: ast.AST, depth: int = 0) -> None:
        # Walk only direct child statements of Module / With body / If body etc.
        body = getattr(node, "body", None)
        if body is None:
            return
        for stmt in body:
            # st.markdown / page_header / etc. at statement level
            if isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Call):
                call = stmt.value
                name = _call_name(call)
                if name == PAGE_HEADER_CALL and call.args:
                    t = _node_to_str(call.args[0]) or ""
                    sub = _node_to_str(call.args[1]) if len(call.args) > 1 else None
                    blocks.append({"type": "h1", "text": t, "sub": sub})
                    continue
                if name in TITLE_CALLS and call.args:
                    t = _node_to_str(call.args[0])
                    if t:
                        lvl = {"st.title": "h1", "st.header": "h2", "st.subheader": "h3"}[name]
                        blocks.append({"type": lvl, "text": t})
                    continue
                if name in CONTENT_CALLS and call.args:
                    t = _node_to_str(call.args[0])
                    if t:
                        kind = "callout" if name in {"st.info", "st.warning", "st.success", "st.error"} else "md"
                        flavor = {"st.info": "info", "st.warning": "warn", "st.success": "ok", "st.error": "err", "st.caption": "caption"}.get(name)
                        blocks.append({"type": kind, "text": t, "flavor": flavor or "md"})
                    continue
                # render_quiz
                quiz = _extract_quiz_questions(call)
                if quiz is not None:
                    blocks.append({"type": "quiz", "questions": quiz})
                    continue
                # st.divider
                if name == "st.divider":
                    blocks.append({"type": "hr"})
                    continue
            # `with st.expander("title"):`
            if isinstance(stmt, ast.With):
                for item in stmt.items:
                    ce = item.context_expr
                    if isinstance(ce, ast.Call) and _call_name(ce) == EXPANDER_CALL and ce.args:
                        title = _node_to_str(ce.args[0]) or ""
                        blocks.append({"type": "expander_open", "text": title})
                        visit(stmt, depth + 1)
                        blocks.append({"type": "expander_close"})
                        break
                else:
                    visit(stmt, depth + 1)
                continue
            # `for ... in modules: st.markdown(...)` etc - skip loops to keep simple
            if isinstance(stmt, (ast.If, ast.For, ast.While, ast.Try)):
                # We still descend so docstrings in bodies are picked up.
                visit(stmt, depth + 1)
                continue

    visit(tree)
    return blocks


# ----------------------------- RENDER TO HTML -----------------------------

MD = markdown.Markdown(extensions=["extra", "sane_lists", "tables"])


def md_to_html(text: str) -> str:
    MD.reset()
    # Convert leading/trailing strip
    return MD.convert(text.strip())


def blocks_to_html(blocks: list[dict]) -> str:
    out: list[str] = []
    in_expander = False
    for b in blocks:
        t = b["type"]
        if t == "h1":
            out.append(f"<h1>{escape(b['text'])}</h1>")
            if b.get("sub"):
                out.append(f"<p class='subtitle'>{escape(b['sub'])}</p>")
        elif t == "h2":
            out.append(f"<h2>{escape(b['text'])}</h2>")
        elif t == "h3":
            out.append(f"<h3>{escape(b['text'])}</h3>")
        elif t == "md":
            out.append(md_to_html(b["text"]))
        elif t == "callout":
            cls = "callout " + b.get("flavor", "info")
            out.append(f"<div class='{cls}'>{md_to_html(b['text'])}</div>")
        elif t == "hr":
            out.append("<hr/>")
        elif t == "expander_open":
            out.append(f"<div class='expander'><h4 class='expander-title'>▸ {escape(b['text'])}</h4><div class='expander-body'>")
            in_expander = True
        elif t == "expander_close":
            out.append("</div></div>")
            in_expander = False
        elif t == "quiz":
            out.append(render_quiz_html(b["questions"]))
    if in_expander:
        out.append("</div></div>")
    return "\n".join(out)


def render_quiz_html(questions: list[dict]) -> str:
    html = ["<div class='quiz'><h3>🧠 חידון</h3>"]
    answers = []
    for i, q in enumerate(questions, 1):
        if not q.get("q") or not q.get("options"):
            continue
        html.append(f"<div class='q'><p><strong>שאלה {i}.</strong> {escape(q['q'])}</p><ol type='א'>")
        for opt in q["options"]:
            if opt is None:
                continue
            html.append(f"<li>{escape(opt)}</li>")
        html.append("</ol></div>")
        ans_idx = q.get("answer", -1)
        if isinstance(ans_idx, int) and 0 <= ans_idx < len(q["options"]):
            letter = "אבגדהוז"[ans_idx] if ans_idx < 7 else str(ans_idx + 1)
            correct = q["options"][ans_idx] or ""
            expl = q.get("explain") or ""
            answers.append((i, letter, correct, expl))
    html.append("<div class='answers'><h4>✅ תשובות</h4><ol>")
    for i, letter, correct, expl in answers:
        html.append(f"<li><strong>שאלה {i}:</strong> ({letter}) {escape(correct)}. {escape(expl)}</li>")
    html.append("</ol></div></div>")
    return "\n".join(html)


def escape(s: str) -> str:
    if s is None:
        return ""
    return (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


# ----------------------------- COMPOSE -----------------------------

CSS_TEXT = """
@page {
    size: A4;
    margin: 18mm 16mm 20mm 16mm;
    @bottom-center {
        content: counter(page) " / " counter(pages);
        font-family: 'Noto Sans Hebrew', sans-serif;
        font-size: 9pt;
        color: #666;
    }
}
@page :first {
    @bottom-center { content: ""; }
}
html, body {
    direction: rtl;
    font-family: 'Noto Sans Hebrew', 'Noto Sans', sans-serif;
    font-size: 11pt;
    line-height: 1.55;
    color: #1a1a1a;
}
h1, h2, h3, h4 {
    color: #0d3b66;
    line-height: 1.25;
    page-break-after: avoid;
}
h1 { font-size: 22pt; margin-top: 0.6em; border-bottom: 2px solid #0d3b66; padding-bottom: 0.2em; }
h2 { font-size: 16pt; margin-top: 1.2em; }
h3 { font-size: 13pt; margin-top: 1em; }
h4 { font-size: 11.5pt; margin-top: 0.8em; }
p.subtitle { color: #555; font-style: italic; margin-top: -0.3em; }
.module { page-break-before: always; }
.cover {
    text-align: center;
    margin-top: 4cm;
}
.cover h1 { border: none; font-size: 32pt; margin-bottom: 0.2em; }
.cover .subtitle { font-size: 14pt; color: #666; }
.cover .meta { margin-top: 5cm; font-size: 10pt; color: #888; }
hr { border: none; border-top: 1px solid #ccc; margin: 1.5em 0; }
code, pre {
    font-family: 'DejaVu Sans Mono', monospace;
    direction: ltr;
    unicode-bidi: embed;
    text-align: left;
    background: #f3f3f3;
    border-radius: 4px;
}
pre {
    padding: 0.6em 0.8em;
    font-size: 9.5pt;
    overflow-x: hidden;
    page-break-inside: avoid;
}
code { padding: 0.1em 0.3em; font-size: 0.9em; }
pre code { background: none; padding: 0; }
.callout {
    border-radius: 6px;
    padding: 0.6em 0.9em;
    margin: 0.7em 0;
    border-right: 4px solid;
    page-break-inside: avoid;
}
.callout.info { background: #eaf2fb; border-color: #2b73c2; }
.callout.warn { background: #fff5e0; border-color: #d68a00; }
.callout.ok   { background: #e7f6ec; border-color: #2c9a4a; }
.callout.err  { background: #fbe9e7; border-color: #c0392b; }
.expander {
    margin: 0.8em 0;
    border: 1px solid #ddd;
    border-radius: 6px;
    padding: 0.3em 0.8em 0.6em;
    page-break-inside: avoid;
}
.expander-title { color: #444; margin: 0.4em 0; font-size: 11pt; }
.expander-body { font-size: 10pt; color: #333; }
ul, ol { padding-right: 1.5em; padding-left: 0; }
table {
    border-collapse: collapse;
    width: 100%;
    margin: 0.8em 0;
    font-size: 10pt;
    page-break-inside: avoid;
}
th, td { border: 1px solid #ccc; padding: 0.35em 0.5em; text-align: right; }
th { background: #f0f4f8; }
strong { color: #0d3b66; }
.quiz { background: #fafafa; border: 1px solid #e0e0e0; border-radius: 8px;
    padding: 1em 1.2em; margin: 1em 0; }
.quiz h3, .quiz h4 { color: #5b21b6; }
.quiz .q { margin-bottom: 0.6em; page-break-inside: avoid; }
.answers { margin-top: 1em; background: #f0fdf4; border: 1px solid #bbf7d0;
    border-radius: 6px; padding: 0.7em 1em; }
blockquote { border-right: 4px solid #aaa; margin: 0.7em 0; padding: 0.1em 0.9em;
    background: #f7f7f7; color: #444; }
img { max-width: 100%; }
"""

MODULES = [
    ("1_מודול_1_Business_Cycle.py",          "מודול 1 – Business Cycle"),
    ("2_מודול_2_מיפוי_סקטורים.py",          "מודול 2 – מיפוי סקטורים"),
    ("3_מודול_3_הסיבוב_הקלאסי.py",          "מודול 3 – הסיבוב הקלאסי"),
    ("4_מודול_4_Macro_Dashboard.py",          "מודול 4 – Macro Dashboard"),
    ("5_מודול_5_Relative_Strength.py",        "מודול 5 – Relative Strength + RRG"),
    ("6_מודול_6_יישום.py",                    "מודול 6 – יישום"),
    ("7_מודול_7_Backtest.py",                  "מודול 7 – Backtest"),
    ("8_מודול_8_שילוב_בתיק.py",                "מודול 8 – שילוב בתיק"),
    ("9_מילון_מונחים.py",                      "מילון מונחים"),
]


def file_to_html(path: Path, module_title: str) -> str:
    src = path.read_text(encoding="utf-8")
    blocks = extract_blocks(src)
    body = blocks_to_html(blocks)
    return f"<section class='module'>\n{body}\n</section>"


def cover_html() -> str:
    return """
<section class='cover'>
  <h1>🔄 Sector Rotation</h1>
  <p class='subtitle'>קורס אינטראקטיבי בעברית – גרסת קריאה</p>
  <p class='subtitle'>8 מודולים + מילון מונחים</p>
  <p class='meta'>מהדורה מודפסת של הקורס. הגרסה האינטראקטיבית (Macro Dashboard חי, RRG, backtester) זמינה בנפרד.</p>
  <p class='meta'><strong>אזהרה:</strong> הקורס למטרות חינוכיות בלבד. אינו ייעוץ פיננסי. ביצועי עבר אינם מבטיחים ביצועי עתיד.</p>
</section>
"""


def app_intro_html() -> str:
    src = APP_FILE.read_text(encoding="utf-8")
    blocks = extract_blocks(src)
    body = blocks_to_html(blocks)
    return f"<section class='module'>\n<h1>ברוכים הבאים</h1>\n{body}\n</section>"


def toc_html() -> str:
    items = "".join(f"<li>{escape(title)}</li>" for _, title in MODULES)
    return f"""
<section class='module'>
  <h1>תוכן עניינים</h1>
  <ol>{items}</ol>
</section>
"""


def main() -> int:
    sections = [cover_html(), app_intro_html(), toc_html()]
    for fname, title in MODULES:
        p = PAGES_DIR / fname
        if not p.exists():
            print(f"missing: {p}", file=sys.stderr)
            continue
        sections.append(file_to_html(p, title))

    html = f"""<!DOCTYPE html>
<html lang="he" dir="rtl"><head><meta charset="utf-8"></head><body>
{''.join(sections)}
</body></html>"""

    Path("/tmp/course.html").write_text(html, encoding="utf-8")
    print(f"HTML written. Rendering PDF -> {OUT_PDF}")

    HTML(string=html, base_url=str(COURSE_DIR)).write_pdf(
        str(OUT_PDF),
        stylesheets=[CSS(string=CSS_TEXT)],
    )
    size_kb = OUT_PDF.stat().st_size / 1024
    print(f"OK: {OUT_PDF} ({size_kb:.0f} KB)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
