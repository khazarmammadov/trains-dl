"""Render report/report.md to report/report.pdf (Markdown -> HTML -> headless Chrome).

No LaTeX needed: math in the report is written with Unicode symbols.
Usage: python src/md_to_pdf.py [path/to/chrome]
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

import markdown

ROOT = Path(__file__).resolve().parent.parent
REPORT = ROOT / "report"
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

CSS = """
@page { size: A4; margin: 18mm 17mm 18mm 17mm; }
body { font-family: "Charter", "Georgia", serif; font-size: 10.3pt; line-height: 1.42;
       color: #111; background: #fff; }
h1, h2, h3, .title, .subtitle, .meta, table, figcaption { font-family: "Helvetica Neue", Arial, sans-serif; }
.title { font-size: 19pt; font-weight: 700; margin: 0 0 4pt; line-height: 1.2; }
.subtitle { font-size: 12pt; color: #444; margin: 0 0 6pt; }
.meta { font-size: 10pt; color: #333; margin-bottom: 14pt; padding-bottom: 8pt; border-bottom: 1px solid #ccc; }
h1 { font-size: 13.5pt; margin: 16pt 0 5pt; border-bottom: 1px solid #ddd; padding-bottom: 2pt; }
h2 { font-size: 11.5pt; margin: 12pt 0 4pt; }
h1, h2 { break-after: avoid; }
p { margin: 0 0 6pt; text-align: justify; }
ul, ol { margin: 0 0 6pt; padding-left: 18pt; }
li { margin-bottom: 2pt; }
code { font-family: "SF Mono", Menlo, monospace; font-size: 8.6pt; background: #f3f3f1; padding: 0 2px; border-radius: 2px; }
table { border-collapse: collapse; margin: 6pt 0 4pt; font-size: 8.4pt; width: 100%; break-inside: avoid; }
th, td { border-bottom: 1px solid #ddd; padding: 2.5pt 4pt; text-align: left; vertical-align: top; }
th { border-bottom: 1.5px solid #888; font-weight: 600; }
img { max-width: 100%; display: block; margin: 8pt auto 2pt; break-inside: avoid; }
p.formula { text-align: center; font-family: "Cambria Math", "STIX Two Math", serif; font-size: 11.5pt; margin: 6pt 0 8pt; }
em { font-style: italic; }
p.caption { text-align: center; font-size: 8.8pt; color: #444; font-style: italic; margin-top: 2pt; }
"""


def front_matter(text: str) -> tuple[dict, str]:
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if not m:
        return {}, text
    meta = {}
    for line in m.group(1).splitlines():
        k, _, v = line.partition(":")
        meta[k.strip()] = v.strip().strip('"')
    return meta, text[m.end():]


def main() -> None:
    chrome = sys.argv[1] if len(sys.argv) > 1 else CHROME
    meta, body = front_matter((REPORT / "report.md").read_text())
    html_body = markdown.markdown(body, extensions=["tables", "sane_lists"])
    # a paragraph that is *only* italic text ("*Figure 1 – ...*") is a caption
    html_body = re.sub(r"<p><em>((?:Figure|Table)[^<]*)</em></p>", r'<p class="caption">\1</p>', html_body)
    head = (f'<div class="title">{meta.get("title", "")}</div>'
            f'<div class="subtitle">{meta.get("subtitle", "")}</div>'
            f'<div class="meta">{meta.get("author", "")} · {meta.get("date", "")}</div>')
    html = (f'<!doctype html><html><head><meta charset="utf-8"><style>{CSS}</style></head>'
            f"<body>{head}{html_body}</body></html>")
    html_path = REPORT / "report.html"
    html_path.write_text(html)
    pdf_path = REPORT / "report.pdf"
    subprocess.run([chrome, "--headless=new", "--disable-gpu", "--no-pdf-header-footer",
                    f"--print-to-pdf={pdf_path}", html_path.as_uri()],
                   check=True, capture_output=True)
    html_path.unlink()
    print(f"wrote {pdf_path}")


if __name__ == "__main__":
    main()
