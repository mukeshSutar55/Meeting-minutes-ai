import os
import json
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

class ReportExporter:
    @staticmethod
    def to_pdf(mom_data: dict, output_pdf_path: str):
        """
        Generates a structured PDF using pure ReportLab (no external system libraries required).
        """
        doc = SimpleDocTemplate(
            output_pdf_path,
            pagesize=letter,
            rightMargin=36,
            leftMargin=36,
            topMargin=36,
            bottomMargin=36
        )

        styles = getSampleStyleSheet()
        
        # Custom Paragraph Styles
        title_style = ParagraphStyle(
            'DocTitle',
            parent=styles['Heading1'],
            fontSize=18,
            leading=22,
            textColor=colors.HexColor('#0f172a'),
            spaceAfter=12
        )
        
        section_style = ParagraphStyle(
            'SectionHeader',
            parent=styles['Heading2'],
            fontSize=12,
            leading=15,
            textColor=colors.HexColor('#1e3a8a'),
            spaceBefore=12,
            spaceAfter=6,
            keepWithNext=True
        )
        
        body_style = ParagraphStyle(
            'Body',
            parent=styles['Normal'],
            fontSize=9.5,
            leading=13,
            textColor=colors.HexColor('#1e293b')
        )
        
        table_cell_style = ParagraphStyle(
            'TableCell',
            parent=styles['Normal'],
            fontSize=8.5,
            leading=11,
            textColor=colors.HexColor('#1e293b')
        )

        table_header_style = ParagraphStyle(
            'TableHeader',
            parent=styles['Normal'],
            fontSize=8.5,
            leading=11,
            fontName='Helvetica-Bold',
            textColor=colors.HexColor('#0f172a')
        )

        story = []

        # 1. Document Title
        story.append(Paragraph("Minutes of Meeting (MoM)", title_style))

        # 2. Metadata Block
        metadata = mom_data.get("metadata", {})
        meta_data_table = [
            [
                Paragraph(f"<b>Source File:</b> {metadata.get('source_file', 'N/A')}", body_style),
                Paragraph(f"<b>Language:</b> {metadata.get('primary_language', 'ENGLISH')}", body_style),
                Paragraph(f"<b>Duration:</b> {metadata.get('total_duration_seconds', 0):.2f}s", body_style)
            ]
        ]
        meta_table = Table(meta_data_table, colWidths=[2.5*inch, 2.5*inch, 2.4*inch])
        meta_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#f8fafc')),
            ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#cbd5e1')),
            ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#e2e8f0')),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('TOPPADDING', (0,0), (-1,-1), 6),
            ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ]))
        story.append(meta_table)
        story.append(Spacer(1, 10))

        mom = mom_data.get("minutes_of_meeting", {})

        # 3. Executive Summary
        story.append(Paragraph("1. Executive Summary", section_style))
        story.append(Paragraph(mom.get("summary", "No summary available."), body_style))
        story.append(Spacer(1, 10))

        # 4. Speaker Statistics
        speaker_stats = mom_data.get("speaker_statistics", {})
        if speaker_stats:
            story.append(Paragraph("2. Speaker Duration & Statistics", section_style))
            stats_table_data = [[
                Paragraph("Speaker", table_header_style),
                Paragraph("Speaking Time", table_header_style),
                Paragraph("Speech Turns", table_header_style),
                Paragraph("Talk Percentage", table_header_style)
            ]]
            for spk, stats in speaker_stats.items():
                stats_table_data.append([
                    Paragraph(spk, table_cell_style),
                    Paragraph(f"{stats.get('total_speaking_time_seconds', 0):.2f}s", table_cell_style),
                    Paragraph(str(stats.get('speaking_segments_count', 0)), table_cell_style),
                    Paragraph(f"{stats.get('speaking_percentage', 0):.1f}%", table_cell_style)
                ])
            stats_table = Table(stats_table_data, colWidths=[2.0*inch, 1.8*inch, 1.8*inch, 1.8*inch])
            stats_table.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#f1f5f9')),
                ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#cbd5e1')),
                ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#e2e8f0')),
                ('TOPPADDING', (0,0), (-1,-1), 5),
                ('BOTTOMPADDING', (0,0), (-1,-1), 5),
            ]))
            story.append(stats_table)
            story.append(Spacer(1, 10))

        # 5. Key Discussion Points
        story.append(Paragraph("3. Key Discussion Points", section_style))
        for point in mom.get("key_discussion_points", []):
            story.append(Paragraph(f"• {point}", body_style))
        story.append(Spacer(1, 10))

        # 6. Decisions Made
        story.append(Paragraph("4. Decisions Made", section_style))
        decisions = mom.get("decisions_made", [])
        if decisions:
            for dec in decisions:
                story.append(Paragraph(f"• {dec}", body_style))
        else:
            story.append(Paragraph("<i>None recorded.</i>", body_style))
        story.append(Spacer(1, 10))

        # 7. Action Items
        story.append(Paragraph("5. Action Items", section_style))
        action_items = mom.get("action_items", [])
        if action_items:
            action_table_data = [[
                Paragraph("Task", table_header_style),
                Paragraph("Assigned To", table_header_style),
                Paragraph("Deadline", table_header_style)
            ]]
            for item in action_items:
                action_table_data.append([
                    Paragraph(item.get("task", ""), table_cell_style),
                    Paragraph(item.get("assigned_to", "Unassigned"), table_cell_style),
                    Paragraph(item.get("deadline", "TBD"), table_cell_style)
                ])
            action_table = Table(action_table_data, colWidths=[4.0*inch, 1.7*inch, 1.7*inch])
            action_table.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#f1f5f9')),
                ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#cbd5e1')),
                ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#e2e8f0')),
                ('TOPPADDING', (0,0), (-1,-1), 5),
                ('BOTTOMPADDING', (0,0), (-1,-1), 5),
            ]))
            story.append(action_table)
        story.append(Spacer(1, 10))

        # 8. Transcript Section
        transcript = mom_data.get("transcript", [])
        if transcript:
            story.append(Paragraph("6. Speaker-Wise Timestamped Transcript", section_style))
            for seg in transcript:
                start_m, start_s = divmod(int(seg.get('start', 0)), 60)
                end_m, end_s = divmod(int(seg.get('end', 0)), 60)
                ts = f"[{start_m:02d}:{start_s:02d} - {end_m:02d}:{end_s:02d}]"
                spk = seg.get('speaker', 'Speaker')
                txt = seg.get('text', '')
                line = f"<font color='#64748b'><b>{ts}</b></font> <font color='#2563eb'><b>{spk}:</b></font> {txt}"
                story.append(Paragraph(line, body_style))
                story.append(Spacer(1, 3))

        # Build PDF
        doc.build(story)