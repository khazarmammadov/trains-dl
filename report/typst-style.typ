// Styling for the pandoc -> Typst build of report.md (see src/md_to_pdf.py)
#set text(font: ("Charter", "STIX Two Math"), size: 10pt, lang: "en")
#set par(justify: true, leading: 0.62em, spacing: 0.9em)
#show heading: set text(font: ("Helvetica Neue", "STIX Two Math"), weight: "bold")
#show heading.where(level: 1): it => block(above: 1.3em, below: 0.6em)[#set text(size: 13pt); #it]
#show heading.where(level: 2): it => block(above: 1.1em, below: 0.5em)[#set text(size: 11pt); #it]
#show raw: set text(font: ("Menlo", "STIX Two Math"), size: 8.5pt)
#show table: set text(font: ("Helvetica Neue", "STIX Two Math"), size: 8pt)
#set table(inset: (x: 4pt, y: 3.5pt), stroke: (x, y) => if y == 0 { (bottom: 0.8pt + luma(120)) } else { (bottom: 0.4pt + luma(210)) })
#show table.cell.where(y: 0): set text(weight: "bold")
#show figure.caption: set text(size: 8.5pt, style: "italic", fill: luma(70))
#show figure: set block(breakable: false)
