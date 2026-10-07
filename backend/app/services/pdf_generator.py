import os
import io
import re
from typing import Dict, Any, List
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import inch, cm, mm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

FONTS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "fonts")
FONTS_REGISTERED = False

def register_fonts():
    """Registers Unicode TrueType fonts for professional English healthcare typography."""
    global FONTS_REGISTERED
    if FONTS_REGISTERED:
        return
    
    eng_reg = os.path.join(FONTS_DIR, "NotoSans-Regular.ttf")
    eng_bold = os.path.join(FONTS_DIR, "NotoSans-Bold.ttf")

    if os.path.exists(eng_reg):
        pdfmetrics.registerFont(TTFont("NotoSans", eng_reg))
    if os.path.exists(eng_bold):
        pdfmetrics.registerFont(TTFont("NotoSans-Bold", eng_bold))
        
    FONTS_REGISTERED = True

def clean_md_for_reportlab(text: str) -> str:
    """Converts raw markdown formatting into clean ReportLab XML markup while preventing parse errors."""
    if not text:
        return ""
    
    text = str(text).strip()
    
    # Strip any leading markdown header hashes
    text = re.sub(r'^#{1,6}\s*', '', text)
    # Strip any leading list dashes or bullet markers if they're redundant
    text = re.sub(r'^[*\-•]\s+', '', text)
    
    # Escape special XML characters while preserving intended bold/italic tags
    text = text.replace("&", "&amp;")
    text = text.replace("<", "&lt;").replace(">", "&gt;")
    
    # Convert markdown bold **text** to <b>text</b>
    text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', text)
    # Convert markdown italic *text* to <i>text</i>
    text = re.sub(r'(?<!\*)\*([^*]+?)\*(?!\*)', r'<i>\1</i>', text)
    
    return text

class NumberedCanvas(canvas.Canvas):
    """Two-pass canvas that computes total page count and adds professional running headers/footers."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        # Do not draw running header and footer on the cover page (Page 1)
        if self._pageNumber == 1:
            return

        self.saveState()
        
        c_primary = colors.HexColor("#0F2942")
        c_muted = colors.HexColor("#64748B")
        c_line = colors.HexColor("#CBD5E1")

        font_reg = "NotoSans"
        font_bold = "NotoSans-Bold"

        # -------------------------------------------------------------
        # RUNNING HEADER
        # -------------------------------------------------------------
        self.setStrokeColor(c_line)
        self.setLineWidth(0.75)
        self.line(40, A4[1] - 40, A4[0] - 40, A4[1] - 40)

        try:
            self.setFont(font_bold, 8)
        except Exception:
            self.setFont("Helvetica-Bold", 8)
        self.setFillColor(c_primary)
        self.drawString(40, A4[1] - 34, "E.V.I.D.A. | Healthcare Evidence Verification")
        
        try:
            self.setFont(font_reg, 8)
        except Exception:
            self.setFont("Helvetica", 8)
        self.setFillColor(c_muted)
        self.drawRightString(A4[0] - 40, A4[1] - 34, "Official Clinical Research Report")

        # -------------------------------------------------------------
        # RUNNING FOOTER
        # -------------------------------------------------------------
        self.line(40, 48, A4[0] - 40, 48)
        
        try:
            self.setFont(font_bold, 8)
        except Exception:
            self.setFont("Helvetica-Bold", 8)
        self.setFillColor(c_primary)
        self.drawString(40, 36, "E.V.I.D.A.")

        try:
            self.setFont(font_reg, 7.5)
        except Exception:
            self.setFont("Helvetica", 7.5)
        self.setFillColor(c_muted)
        self.drawString(40, 26, "Evidence Verification & Intelligent Domain Analysis System")

        page_str = f"Page {self._pageNumber} of {page_count}"
        try:
            self.setFont(font_bold, 8)
        except Exception:
            self.setFont("Helvetica-Bold", 8)
        self.setFillColor(c_primary)
        self.drawRightString(A4[0] - 40, 32, page_str)

        self.restoreState()


class PDFReportGenerator:
    """High-quality PDF report generation engine with complete healthcare clinical styling."""

    @classmethod
    def generate_pdf(cls, data: Dict[str, Any]) -> bytes:
        register_fonts()
        
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            leftMargin=40,
            rightMargin=40,
            topMargin=50,
            bottomMargin=58
        )

        font_reg = "NotoSans"
        font_bold = "NotoSans-Bold"

        # Cohesive Clinical Color Palette
        c_primary = colors.HexColor("#0F2942")     # Deep Hospital Navy
        c_secondary = colors.HexColor("#1E40AF")   # Royal Blue
        c_accent = colors.HexColor("#0284C7")      # Sky Blue Accent
        c_dark = colors.HexColor("#0F172A")        # Slate Dark 900
        c_body = colors.HexColor("#334155")        # Slate 700 text
        c_bg_light = colors.HexColor("#F8FAFC")    # Slate 50 background
        c_card_bg = colors.HexColor("#F1F5F9")     # Slate 100 card
        c_border = colors.HexColor("#CBD5E1")      # Slate 300 border
        c_green = colors.HexColor("#15803D")       # Verified Green
        c_green_bg = colors.HexColor("#F0FDF4")    # Light Green
        c_amber = colors.HexColor("#B45309")       # Warning Amber
        c_amber_bg = colors.HexColor("#FFFBEB")    # Amber Light

        # Paragraph Styles
        st_cover_org = ParagraphStyle(
            'CoverOrg', fontName=font_bold, fontSize=24, leading=28, textColor=c_primary
        )
        st_cover_sub = ParagraphStyle(
            'CoverSub', fontName=font_reg, fontSize=11, leading=15, textColor=c_secondary
        )
        st_cover_title = ParagraphStyle(
            'CoverTitle', fontName=font_bold, fontSize=18, leading=24, textColor=c_primary
        )
        st_cover_q_label = ParagraphStyle(
            'CoverQLabel', fontName=font_bold, fontSize=10.5, leading=14, textColor=c_secondary
        )
        st_cover_q_text = ParagraphStyle(
            'CoverQText', fontName=font_bold, fontSize=13, leading=18, textColor=c_dark
        )
        st_cover_meta = ParagraphStyle(
            'CoverMeta', fontName=font_reg, fontSize=8.5, leading=13, textColor=c_body
        )

        st_sec_heading = ParagraphStyle(
            'SecHeading', fontName=font_bold, fontSize=11.5, leading=15, textColor=c_primary,
            spaceBefore=14, spaceAfter=6, keepWithNext=True
        )
        st_body = ParagraphStyle(
            'Body', fontName=font_reg, fontSize=8.5, leading=12.5, textColor=c_body, spaceAfter=4
        )
        st_body_bold = ParagraphStyle(
            'BodyBold', fontName=font_bold, fontSize=8.5, leading=12.5, textColor=c_dark
        )
        st_callout = ParagraphStyle(
            'Callout', fontName=font_reg, fontSize=9, leading=13.5, textColor=c_dark
        )
        st_table_header = ParagraphStyle(
            'TableHeader', fontName=font_bold, fontSize=7.5, leading=10, textColor=colors.white
        )
        st_table_cell = ParagraphStyle(
            'TableCell', fontName=font_reg, fontSize=7.5, leading=10, textColor=c_body
        )
        st_table_cell_bold = ParagraphStyle(
            'TableCellBold', fontName=font_bold, fontSize=7.5, leading=10, textColor=c_dark
        )
        st_table_cell_small = ParagraphStyle(
            'TableCellSmall', fontName=font_reg, fontSize=6.8, leading=8.5, textColor=c_body
        )
        st_pipe_title = ParagraphStyle(
            'PipeTitle', fontName=font_bold, fontSize=8, leading=10.5, textColor=c_primary
        )
        st_pipe_desc = ParagraphStyle(
            'PipeDesc', fontName=font_reg, fontSize=7, leading=9, textColor=c_body
        )
        st_disclaimer = ParagraphStyle(
            'Disclaimer', fontName=font_reg, fontSize=7.8, leading=11.5, textColor=colors.HexColor("#78350F")
        )

        printable_width = A4[0] - 80 # 515.27 pt

        story = []

        # =========================================================================
        # COVER PAGE
        # =========================================================================
        story.append(Spacer(1, 15))
        story.append(Paragraph("E.V.I.D.A.", st_cover_org))
        story.append(Spacer(1, 4))
        story.append(Paragraph(clean_md_for_reportlab(data.get("org_subtitle", "Evidence Verification & Intelligent Domain Analysis System")), st_cover_sub))
        story.append(Spacer(1, 14))
        story.append(HRFlowable(width="100%", thickness=2.5, color=c_secondary, spaceBefore=0, spaceAfter=18))
        
        story.append(Spacer(1, 20))
        story.append(Paragraph(clean_md_for_reportlab(data.get("report_title", "HEALTHCARE EVIDENCE VERIFICATION REPORT")), st_cover_title))
        story.append(Spacer(1, 18))

        # Research Question Card
        q_label = "RESEARCH QUESTION:"
        q_clean = clean_md_for_reportlab(data.get("question", ""))
        q_box_content = [
            [Paragraph(q_label, st_cover_q_label)],
            [Spacer(1, 4)],
            [Paragraph(f'"{q_clean}"', st_cover_q_text)]
        ]
        q_box_table = Table(q_box_content, colWidths=[printable_width])
        q_box_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), c_bg_light),
            ('BOX', (0,0), (-1,-1), 1, c_border),
            ('PADDING', (0,0), (-1,-1), 12),
        ]))
        story.append(q_box_table)
        
        story.append(Spacer(1, 35))

        # Metadata Summary Card
        meta_data = [
            [
                Paragraph("<b>Domain:</b> " + clean_md_for_reportlab(data.get("domain", "Healthcare / Clinical Research")), st_cover_meta),
                Paragraph("<b>Generated Date:</b> " + data.get("date", ""), st_cover_meta)
            ],
            [
                Paragraph("<b>Audit Depth:</b> " + clean_md_for_reportlab(data.get("research_depth", "Comprehensive Multi-Agent Audit")), st_cover_meta),
                Paragraph("<b>Report Language:</b> English", st_cover_meta)
            ],
            [
                Paragraph("<b>Evidence Source:</b> Official World Health Organization (WHO) Guidelines", st_cover_meta),
                Paragraph("<b>Verification System:</b> E.V.I.D.A. Clinical Multi-Agent Framework", st_cover_meta)
            ]
        ]
        meta_table = Table(meta_data, colWidths=[printable_width/2, printable_width/2])
        meta_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), c_card_bg),
            ('BOX', (0,0), (-1,-1), 0.75, c_border),
            ('INNERGRID', (0,0), (-1,-1), 0.5, c_border),
            ('PADDING', (0,0), (-1,-1), 8),
        ]))
        story.append(meta_table)

        story.append(Spacer(1, 45))
        story.append(HRFlowable(width="100%", thickness=1, color=c_border, spaceBefore=0, spaceAfter=12))
        notice_text = (
            "<b>Clinical Notice:</b> Synthesized from indexed World Health Organization (WHO) clinical practice guidelines for evidence-based verification and clinical research evaluation."
        )
        story.append(Paragraph(notice_text, st_table_cell_small))

        story.append(PageBreak())

        # =========================================================================
        # 1. EXECUTIVE SUMMARY
        # =========================================================================
        story.append(Paragraph("1. EXECUTIVE SUMMARY", st_sec_heading))
        
        exec_table = Table([[Paragraph(clean_md_for_reportlab(data.get("executive_summary", "")), st_callout)]], colWidths=[printable_width])
        exec_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#EFF6FF")),
            ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#BFDBFE")),
            ('PADDING', (0,0), (-1,-1), 10),
        ]))
        story.append(exec_table)
        story.append(Spacer(1, 10))

        # =========================================================================
        # 2. RESEARCH QUESTION
        # =========================================================================
        story.append(Paragraph("2. RESEARCH QUESTION", st_sec_heading))
        
        rq_rows = [
            [
                Paragraph("<b>Question:</b>", st_body_bold),
                Paragraph(clean_md_for_reportlab(data.get("question", "")), st_body)
            ],
            [
                Paragraph("<b>Domain:</b>", st_body_bold),
                Paragraph(clean_md_for_reportlab(data.get("domain", "")), st_body)
            ],
            [
                Paragraph("<b>Research Depth:</b>", st_body_bold),
                Paragraph(clean_md_for_reportlab(data.get("research_depth", "")), st_body)
            ]
        ]
        rq_table = Table(rq_rows, colWidths=[120, printable_width - 120])
        rq_table.setStyle(TableStyle([
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('PADDING', (0,0), (-1,-1), 3),
        ]))
        story.append(rq_table)
        story.append(Spacer(1, 10))

        # =========================================================================
        # 3. RESEARCH METHODOLOGY
        # =========================================================================
        story.append(Paragraph("3. RESEARCH METHODOLOGY", st_sec_heading))
        
        steps = data.get("methodology_steps", [])
        m_rows = []
        for s in steps:
            step_badge = f"<font color='#1E40AF'><b>Step {s['step']}</b></font>"
            m_rows.append([
                Paragraph(step_badge, st_table_cell_bold),
                Paragraph(clean_md_for_reportlab(s["title"]), st_pipe_title),
                Paragraph(clean_md_for_reportlab(s["desc"]), st_pipe_desc)
            ])
        m_table = Table(m_rows, colWidths=[45, 170, printable_width - 215])
        m_table.setStyle(TableStyle([
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('BOX', (0,0), (-1,-1), 0.5, c_border),
            ('INNERGRID', (0,0), (-1,-1), 0.5, c_border),
            ('ROWBACKGROUNDS', (0,0), (-1,-1), [colors.white, c_bg_light]),
            ('PADDING', (0,0), (-1,-1), 4),
        ]))
        story.append(m_table)
        story.append(Spacer(1, 10))

        # =========================================================================
        # 4. RESEARCH SOURCES
        # =========================================================================
        story.append(Paragraph("4. RESEARCH SOURCES", st_sec_heading))
        
        sources = data.get("sources", [])
        s_headers = [
            Paragraph("<b>No.</b>", st_table_header),
            Paragraph("<b>Source / Document</b>", st_table_header),
            Paragraph("<b>Organization</b>", st_table_header),
            Paragraph("<b>Source Type</b>", st_table_header),
            Paragraph("<b>Quality</b>", st_table_header),
            Paragraph("<b>Publication Date</b>", st_table_header),
            Paragraph("<b>URL</b>", st_table_header)
        ]
        s_rows = [s_headers]
        for s in sources:
            url_clean = s.get("url", "Not available")
            url_display = "https://iris.who.int" if "iris.who.int" in url_clean else (url_clean[:20] + "..." if len(url_clean) > 22 else url_clean)
            s_rows.append([
                Paragraph(str(s["index"]), st_table_cell_bold),
                Paragraph(clean_md_for_reportlab(s["title"]), st_table_cell_bold),
                Paragraph(clean_md_for_reportlab(s["organization"]), st_table_cell),
                Paragraph(clean_md_for_reportlab(s["source_type"]), st_table_cell),
                Paragraph(f"<font color='#15803D'><b>{clean_md_for_reportlab(s['quality'])}</b></font>", st_table_cell),
                Paragraph(clean_md_for_reportlab(s["publication_date"]), st_table_cell),
                Paragraph(clean_md_for_reportlab(url_display), st_table_cell_small)
            ])
        s_table = Table(s_rows, colWidths=[22, 140, 85, 75, 50, 65, printable_width - 437], repeatRows=1)
        s_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), c_primary),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('BOX', (0,0), (-1,-1), 0.5, c_border),
            ('INNERGRID', (0,0), (-1,-1), 0.5, c_border),
            ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, c_bg_light]),
            ('PADDING', (0,0), (-1,-1), 3.5),
        ]))
        story.append(s_table)
        story.append(Spacer(1, 10))

        # =========================================================================
        # 5. KEY FINDINGS
        # =========================================================================
        story.append(Paragraph("5. KEY FINDINGS", st_sec_heading))
        
        findings = data.get("key_findings", [])
        if not findings:
            story.append(Paragraph("No clinical findings could be extracted from the current evidence repository.", st_body))
        else:
            f_rows = []
            for f in findings:
                f_rows.append([
                    Paragraph(f"<b>{clean_md_for_reportlab(f['title'])}</b>", st_table_cell_bold),
                    Paragraph(clean_md_for_reportlab(f['description']), st_table_cell),
                    Paragraph(f"<font color='#15803D'><b>{clean_md_for_reportlab(f['status'])}</b></font>", st_table_cell)
                ])
            f_table = Table(f_rows, colWidths=[80, printable_width - 190, 110])
            f_table.setStyle(TableStyle([
                ('VALIGN', (0,0), (-1,-1), 'TOP'),
                ('BOX', (0,0), (-1,-1), 0.5, c_border),
                ('INNERGRID', (0,0), (-1,-1), 0.5, c_border),
                ('ROWBACKGROUNDS', (0,0), (-1,-1), [c_bg_light, colors.white]),
                ('PADDING', (0,0), (-1,-1), 5),
            ]))
            story.append(f_table)
        story.append(Spacer(1, 10))

        # =========================================================================
        # 6. CLAIMS AND EVIDENCE
        # =========================================================================
        story.append(Paragraph("6. CLAIMS AND EVIDENCE", st_sec_heading))
        
        claims_tbl_data = data.get("claims_table", [])
        c_headers = [
            Paragraph("<b>Claim</b>", st_table_header),
            Paragraph("<b>Supporting Evidence</b>", st_table_header),
            Paragraph("<b>Source</b>", st_table_header),
            Paragraph("<b>Page</b>", st_table_header),
            Paragraph("<b>Verification</b>", st_table_header)
        ]
        c_rows = [c_headers]
        for c in claims_tbl_data:
            c_rows.append([
                Paragraph(f"<b>#{c['index']}</b> {clean_md_for_reportlab(c['claim'])}", st_table_cell),
                Paragraph(clean_md_for_reportlab(c["evidence"]), st_table_cell),
                Paragraph(clean_md_for_reportlab(c["source"]), st_table_cell),
                Paragraph(clean_md_for_reportlab(str(c["page"])), st_table_cell),
                Paragraph(f"<font color='#15803D'><b>{clean_md_for_reportlab(c['verification'])}</b></font>", st_table_cell)
            ])
        c_table = Table(c_rows, colWidths=[135, 170, 100, 35, printable_width - 440], repeatRows=1)
        c_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), c_primary),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('BOX', (0,0), (-1,-1), 0.5, c_border),
            ('INNERGRID', (0,0), (-1,-1), 0.5, c_border),
            ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, c_bg_light]),
            ('PADDING', (0,0), (-1,-1), 4),
        ]))
        story.append(c_table)
        story.append(Spacer(1, 10))

        # =========================================================================
        # 7. EVIDENCE VERIFICATION
        # =========================================================================
        story.append(Paragraph("7. EVIDENCE VERIFICATION", st_sec_heading))
        
        ev_breakdown = data.get("evidence_breakdown", [])
        for eb in ev_breakdown:
            eb_content = [
                [Paragraph(f"<b>Claim:</b> {clean_md_for_reportlab(eb['claim'])}", st_body_bold)],
                [Paragraph(f"<b>Evidence:</b> {clean_md_for_reportlab(eb['evidence'])}", st_body)],
                [Paragraph(f"<b>Source:</b> {clean_md_for_reportlab(eb['source'])} (Page {clean_md_for_reportlab(str(eb['page']))}) | <b>Verification:</b> <font color='#15803D'>{clean_md_for_reportlab(eb['verification'])}</font>", st_body)],
                [Paragraph(f"<b>Reason:</b> {clean_md_for_reportlab(eb['reason'])}", st_body)]
            ]
            eb_t = Table(eb_content, colWidths=[printable_width])
            eb_t.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,-1), c_bg_light),
                ('BOX', (0,0), (-1,-1), 0.5, c_border),
                ('PADDING', (0,0), (-1,-1), 6),
            ]))
            story.append(eb_t)
            story.append(Spacer(1, 6))

        story.append(Spacer(1, 6))

        # =========================================================================
        # 8. SOURCE QUALITY ASSESSMENT
        # =========================================================================
        story.append(Paragraph("8. SOURCE QUALITY ASSESSMENT", st_sec_heading))
        
        sq_items = data.get("source_quality", [])
        sq_headers = [
            Paragraph("<b>Source / Guideline</b>", st_table_header),
            Paragraph("<b>Authority</b>", st_table_header),
            Paragraph("<b>Publication Info</b>", st_table_header),
            Paragraph("<b>Quality Rating</b>", st_table_header),
            Paragraph("<b>Evaluation Rationale</b>", st_table_header)
        ]
        sq_rows = [sq_headers]
        for sq in sq_items:
            sq_rows.append([
                Paragraph(f"<b>{clean_md_for_reportlab(sq['source_title'])}</b>", st_table_cell),
                Paragraph(clean_md_for_reportlab(sq["authority"]), st_table_cell),
                Paragraph(clean_md_for_reportlab(sq["publication_info"]), st_table_cell),
                Paragraph(f"<font color='#15803D'><b>{clean_md_for_reportlab(sq['evidence_quality'])}</b></font>", st_table_cell),
                Paragraph(clean_md_for_reportlab(sq["explanation"]), st_table_cell)
            ])
        sq_table = Table(sq_rows, colWidths=[140, 95, 75, 55, printable_width - 365], repeatRows=1)
        sq_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), c_primary),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('BOX', (0,0), (-1,-1), 0.5, c_border),
            ('INNERGRID', (0,0), (-1,-1), 0.5, c_border),
            ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, c_bg_light]),
            ('PADDING', (0,0), (-1,-1), 4),
        ]))
        story.append(sq_table)
        story.append(Spacer(1, 10))

        # =========================================================================
        # 9. CONFLICTING EVIDENCE
        # =========================================================================
        story.append(Paragraph("9. CONFLICTING EVIDENCE", st_sec_heading))
        
        conflicts = data.get("conflicts", [])
        has_real_conflict = any(c.get("has_conflict", False) for c in conflicts)
        
        if not has_real_conflict:
            no_conf_text = "No significant conflicting evidence was identified in the retrieved sources."
            conf_box = [[Paragraph(f"• {no_conf_text}", st_body)]]
            c_t = Table(conf_box, colWidths=[printable_width])
            c_t.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#F8FAFC")),
                ('BOX', (0,0), (-1,-1), 0.5, c_border),
                ('PADDING', (0,0), (-1,-1), 8),
            ]))
            story.append(c_t)
        else:
            for conf in conflicts:
                if not conf.get("has_conflict"):
                    continue
                conf_box = [
                    [Paragraph(f"<b>Claim / Topic:</b> {clean_md_for_reportlab(conf['topic'])}", st_body_bold)],
                    [Paragraph(f"<b>Evidence A:</b> {clean_md_for_reportlab(conf['evidence_a'])} (Source: {clean_md_for_reportlab(conf['source_a'])})", st_body)],
                    [Paragraph(f"<b>Evidence B:</b> {clean_md_for_reportlab(conf['evidence_b'])} (Source: {clean_md_for_reportlab(conf['source_b'])})", st_body)],
                    [Paragraph(f"<b>Conflict Explanation:</b> {clean_md_for_reportlab(conf['explanation'])}", st_body)]
                ]
                c_t = Table(conf_box, colWidths=[printable_width])
                c_t.setStyle(TableStyle([
                    ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#FFFBEB")),
                    ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor("#FDE68A")),
                    ('PADDING', (0,0), (-1,-1), 6),
                ]))
                story.append(c_t)
                story.append(Spacer(1, 6))

        story.append(Spacer(1, 10))

        # =========================================================================
        # 10. CONFIDENCE ASSESSMENT
        # =========================================================================
        story.append(Paragraph("10. CONFIDENCE ASSESSMENT", st_sec_heading))
        
        conf_info = data.get("confidence", {})
        conf_rows = [
            [
                Paragraph(f"<b>Overall Confidence:</b> <font color='#15803D'><b>{conf_info.get('rating', 'HIGH')}</b></font>", st_body_bold),
                Paragraph(f"<b>Score:</b> <font color='#15803D'><b>{conf_info.get('score_display', '88%')}</b></font>", st_body_bold)
            ],
            [
                Paragraph(f"<b>Supporting Sources:</b> {conf_info.get('supporting_sources_count', 1)}", st_body),
                Paragraph(f"<b>Contradictory Sources:</b> {conf_info.get('contradictory_sources_count', 0)}", st_body)
            ]
        ]
        conf_table = Table(conf_rows, colWidths=[printable_width/2, printable_width/2])
        conf_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), c_green_bg),
            ('BOX', (0,0), (-1,-1), 0.75, colors.HexColor("#BBF7D0")),
            ('PADDING', (0,0), (-1,-1), 6),
        ]))
        story.append(conf_table)
        story.append(Spacer(1, 4))
        for r in conf_info.get("reasons", []):
            story.append(Paragraph(f"• {clean_md_for_reportlab(r)}", st_body))
        story.append(Spacer(1, 10))

        # =========================================================================
        # 11. FINAL ANSWER
        # =========================================================================
        story.append(Paragraph("11. FINAL ANSWER", st_sec_heading))
        
        final_ans = data.get("final_answer", {})
        story.append(Paragraph(clean_md_for_reportlab(final_ans.get("summary", "")), st_body))
        story.append(Spacer(1, 4))
        for bp in final_ans.get("bullet_points", []):
            story.append(Paragraph(f"• {clean_md_for_reportlab(bp)}", st_body))
        story.append(Spacer(1, 10))

        # =========================================================================
        # 12. LIMITATIONS
        # =========================================================================
        story.append(Paragraph("12. LIMITATIONS", st_sec_heading))
        for lim in data.get("limitations", []):
            story.append(Paragraph(f"• {clean_md_for_reportlab(lim)}", st_body))
        story.append(Spacer(1, 10))

        # =========================================================================
        # 13. MEDICAL DISCLAIMER
        # =========================================================================
        story.append(Paragraph("13. MEDICAL DISCLAIMER", st_sec_heading))
        
        disc_table = Table([[Paragraph(clean_md_for_reportlab(data.get("disclaimer", "")), st_disclaimer)]], colWidths=[printable_width])
        disc_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), c_amber_bg),
            ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#FDE68A")),
            ('PADDING', (0,0), (-1,-1), 8),
        ]))
        story.append(disc_table)

        # Build document with NumberedCanvas
        doc.build(story, canvasmaker=NumberedCanvas)
        buffer.seek(0)
        return buffer.getvalue()
