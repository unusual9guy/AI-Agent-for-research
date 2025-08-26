from __future__ import annotations

import io
from typing import Optional


def markdown_to_pdf_bytes(md_text: str) -> Optional[bytes]:
    """Convert markdown to PDF. Tries WeasyPrint first, then ReportLab. Returns None if neither is available.
    This mirrors the in-app behavior but is factored out for reuse and testing.
    """
    if not md_text:
        return None

    # Convert markdown to HTML (for WeasyPrint path)
    try:
        import markdown as _md
        html_body = _md.markdown(md_text, extensions=["extra", "toc", "tables", "sane_lists"])  # type: ignore
    except Exception:
        html_body = f"<pre>{md_text}</pre>"

    html_doc = f"""
<!doctype html>
<html>
<head>
  <meta charset='utf-8'>
  <style>
    body {{ font-family: Arial, Helvetica, sans-serif; line-height: 1.5; color: #111; }}
    h1, h2, h3, h4, h5 {{ color: #222; margin-top: 1.2em; }}
    code, pre {{ font-family: Consolas, 'Courier New', monospace; background: #f6f8fa; }}
    table {{ width: 100%; border-collapse: collapse; }}
    th, td {{ border: 1px solid #ddd; padding: 6px; }}
    blockquote {{ border-left: 4px solid #ddd; margin: 0; padding: 0 1em; color: #555; }}
  </style>
  <title>Research Report</title>
  <meta name='robots' content='noindex'>
</head>
<body>
{html_body}
</body>
</html>
"""

    # Attempt WeasyPrint
    try:
        from weasyprint import HTML, CSS  # type: ignore
        pdf_bytes = HTML(string=html_doc).write_pdf(stylesheets=[CSS(string="@page { size: A4; margin: 20mm; }")])
        return pdf_bytes
    except Exception:
        pass

    # ReportLab fallback with basic markdown rendering
    try:
        from reportlab.lib.pagesizes import A4  # type: ignore
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, ListFlowable, ListItem  # type: ignore
        from reportlab.lib.styles import getSampleStyleSheet  # type: ignore
        from reportlab.lib.units import mm  # type: ignore
        from reportlab.lib.enums import TA_LEFT  # type: ignore

        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, leftMargin=20*mm, rightMargin=20*mm, topMargin=20*mm, bottomMargin=20*mm)
        styles = getSampleStyleSheet()
        styles["Heading1"].alignment = TA_LEFT
        styles["Heading2"].alignment = TA_LEFT
        styles["Heading3"].alignment = TA_LEFT

        def _inline_md_to_html(text: str) -> str:
            import re as _re2
            s = text
            s = _re2.sub(r"\*\*([^*]+?)\*\*", r"<b>\1</b>", s)
            s = _re2.sub(r"(?<!\*)\*([^*]+?)\*(?!\*)", r"<i>\1</i>", s)
            s = s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            s = s.replace("&lt;b&gt;", "<b>").replace("&lt;/b&gt;", "</b>")
            s = s.replace("&lt;i&gt;", "<i>").replace("&lt;/i&gt;", "</i>")
            return s

        story = []
        lines = md_text.splitlines()
        i = 0
        while i < len(lines):
            line = lines[i].rstrip()
            if not line:
                i += 1
                continue
            if line.startswith("### "):
                story.append(Paragraph(line[4:], styles["Heading3"]))
                story.append(Spacer(1, 6))
            elif line.startswith("## "):
                story.append(Paragraph(line[3:], styles["Heading2"]))
                story.append(Spacer(1, 8))
            elif line.startswith("# "):
                story.append(Paragraph(line[2:], styles["Heading1"]))
                story.append(Spacer(1, 10))
            elif line.lstrip().startswith(("- ", "* ", "• ")):
                items = []
                while i < len(lines) and lines[i].lstrip().startswith(("- ", "* ", "• ")):
                    raw_bullet = lines[i].lstrip()[2:].strip()
                    text_html = _inline_md_to_html(raw_bullet)
                    if raw_bullet.endswith(":"):
                        k = i + 1
                        subitems = []
                        while k < len(lines) and lines[k].lstrip().startswith(("- ", "* ", "• ")):
                            sub_raw = lines[k].lstrip()[2:].strip()
                            if sub_raw.endswith(":"):
                                break
                            subitems.append(ListItem(Paragraph(_inline_md_to_html(sub_raw), styles["BodyText"])))
                            k += 1
                        if subitems:
                            parent_para = Paragraph(text_html, styles["BodyText"])
                            nested = ListFlowable(subitems, bulletType='bullet', bulletChar='•', leftIndent=18)
                            items.append(ListItem([parent_para, Spacer(1, 2), nested]))
                            i = k
                            continue
                    items.append(ListItem(Paragraph(text_html, styles["BodyText"])))
                    i += 1
                story.append(ListFlowable(items, bulletType='bullet', bulletChar='•', leftIndent=18))
                story.append(Spacer(1, 4))
                continue
            else:
                para_lines = [line]
                j = i + 1
                while j < len(lines) and lines[j] and not lines[j].lstrip().startswith(('# ', '## ', '### ', '- ', '* ', '• ')):
                    para_lines.append(lines[j])
                    j += 1
                paragraph_html = "<br/>".join([_inline_md_to_html(l) for l in para_lines])
                story.append(Paragraph(paragraph_html, styles["BodyText"]))
                story.append(Spacer(1, 4))
                i = j - 1
            i += 1

        doc.build(story)
        return buffer.getvalue()
    except Exception:
        return None


