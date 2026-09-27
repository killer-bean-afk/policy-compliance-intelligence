import os
from pathlib import Path
from typing import Optional
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    HRFlowable,
    KeepTogether
)
from src.config import REPORTS_DIR
from src.models.schemas import ComplianceDossier, ComplianceVerdict, RiskLevel

class ComplianceReportExporter:
    """Exports structured compliance dossiers to official PDF audit reports."""

    @staticmethod
    def export_pdf(dossier: ComplianceDossier, output_path: Optional[Path] = None) -> Path:
        """Generates a professional executive compliance audit PDF report."""
        REPORTS_DIR.mkdir(parents=True, exist_ok=True)
        if output_path is None:
            filename = f"Compliance_Audit_Report_{dossier.analysis_id}.pdf"
            output_path = REPORTS_DIR / filename

        doc = SimpleDocTemplate(
            str(output_path),
            pagesize=letter,
            rightMargin=40,
            leftMargin=40,
            topMargin=40,
            bottomMargin=40
        )

        styles = getSampleStyleSheet()

        # Styles
        title_style = ParagraphStyle(
            'ReportTitle',
            parent=styles['Heading1'],
            fontSize=18,
            leading=22,
            textColor=colors.HexColor('#0F172A'),
            fontName='Helvetica-Bold'
        )

        meta_style = ParagraphStyle(
            'ReportMeta',
            parent=styles['Normal'],
            fontSize=9,
            leading=13,
            textColor=colors.HexColor('#64748B')
        )

        h2_style = ParagraphStyle(
            'SectionHeader',
            parent=styles['Heading2'],
            fontSize=12,
            leading=16,
            textColor=colors.HexColor('#1E293B'),
            fontName='Helvetica-Bold',
            spaceBefore=12,
            spaceAfter=6
        )

        body_style = ParagraphStyle(
            'BodyTextCustom',
            parent=styles['Normal'],
            fontSize=8.5,
            leading=12.5,
            textColor=colors.HexColor('#334155')
        )

        elements = []

        # Header Title
        elements.append(Paragraph("POLICY COMPLIANCE INTELLIGENCE", title_style))
        elements.append(Paragraph("Official Enterprise Multi-Agent Compliance Audit Dossier", meta_style))
        elements.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#2563EB'), spaceBefore=6, spaceAfter=10))

        # Top Metadata Table
        verdict_color = "#DC2626" if dossier.verdict == ComplianceVerdict.NON_COMPLIANT else ("#D97706" if dossier.verdict == ComplianceVerdict.CONDITIONAL else "#16A34A")
        verdict_bg = "#FEF2F2" if dossier.verdict == ComplianceVerdict.NON_COMPLIANT else ("#FFFBEB" if dossier.verdict == ComplianceVerdict.CONDITIONAL else "#F0FDF4")

        meta_rows = [
            [
                Paragraph(f"<b>Dossier ID:</b> {dossier.analysis_id}", meta_style),
                Paragraph(f"<b>Assessment Date:</b> {dossier.created_at}", meta_style)
            ],
            [
                Paragraph(f"<b>Compliance Verdict:</b> <font color='{verdict_color}'><b>{dossier.verdict.value}</b></font>", meta_style),
                Paragraph(f"<b>Composite Risk Score:</b> <b>{dossier.risk_score}/100 ({dossier.risk_level.value})</b>", meta_style)
            ],
            [
                Paragraph(f"<b>Evidentiary Grounding:</b> {dossier.validation.grounding_faithfulness_score * 100:.1f}%", meta_style),
                Paragraph(f"<b>Audit Validation:</b> {'CERTIFIED' if dossier.validation.is_valid else 'FLAGGED'}", meta_style)
            ]
        ]
        meta_table = Table(meta_rows, colWidths=[270, 260])
        meta_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F8FAFC')),
            ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#CBD5E1')),
            ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
            ('PADDING', (0,0), (-1,-1), 5),
        ]))
        elements.append(meta_table)
        elements.append(Spacer(1, 10))

        # Assessed Scenario
        elements.append(Paragraph("<b>1. Evaluated Business Scenario</b>", h2_style))
        scenario_table = Table([[Paragraph(f"<i>\"{dossier.scenario}\"</i>", body_style)]], colWidths=[530])
        scenario_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F1F5F9')),
            ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#94A3B8')),
            ('PADDING', (0,0), (-1,-1), 8),
        ]))
        elements.append(scenario_table)
        elements.append(Spacer(1, 8))

        # Executive Summary
        elements.append(Paragraph("<b>2. Executive Compliance Findings</b>", h2_style))
        summary_table = Table([[Paragraph(dossier.executive_summary, body_style)]], colWidths=[530])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor(verdict_bg)),
            ('BOX', (0,0), (-1,-1), 1, colors.HexColor(verdict_color)),
            ('PADDING', (0,0), (-1,-1), 8),
        ]))
        elements.append(summary_table)
        elements.append(Spacer(1, 10))

        # Clause Assessments Table
        elements.append(Paragraph("<b>3. Clause-by-Clause Policy Assessment Matrix</b>", h2_style))
        clause_headers = ["Citation", "Policy / Section", "Status", "Reasoning & Evidence Excerpt"]
        clause_rows = [[Paragraph(f"<b>{h}</b>", meta_style) for h in clause_headers]]

        for ca in dossier.clause_assessments:
            status_color = "#DC2626" if ca.verdict == ComplianceVerdict.NON_COMPLIANT else ("#D97706" if ca.verdict == ComplianceVerdict.CONDITIONAL else "#16A34A")
            excerpt = ca.evidence_quote[:120] + "..." if len(ca.evidence_quote) > 120 else ca.evidence_quote
            
            clause_rows.append([
                Paragraph(f"<b>{ca.citation}</b><br/>{ca.clause_id}", body_style),
                Paragraph(f"<b>{ca.policy_name}</b><br/>{ca.section}", body_style),
                Paragraph(f"<font color='{status_color}'><b>{ca.verdict.value}</b></font>", body_style),
                Paragraph(f"{ca.reasoning}<br/><font color='#64748B'><i>Evidence: \"{excerpt}\"</i></font>", body_style)
            ])

        clause_table = Table(clause_rows, colWidths=[95, 125, 80, 230])
        clause_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#E2E8F0')),
            ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#94A3B8')),
            ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
            ('PADDING', (0,0), (-1,-1), 4),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ]))
        elements.append(clause_table)
        elements.append(Spacer(1, 10))

        # Identified Gaps & Risk Factors
        if dossier.identified_gaps:
            elements.append(Paragraph("<b>4. Identified Compliance Gaps & Regulatory Exposure</b>", h2_style))
            gap_data = []
            for g in dossier.identified_gaps:
                gap_data.append([Paragraph(f"• <b>GAP:</b> {g}", body_style)])
            for rf in dossier.risk_factors:
                pen = rf.potential_penalties[:110] + "..." if len(rf.potential_penalties) > 110 else rf.potential_penalties
                gap_data.append([Paragraph(f"• <b>{rf.risk_title} ({rf.severity.value}):</b> {pen} <i>[{rf.clause_reference}]</i>", body_style)])

            gap_table = Table(gap_data, colWidths=[530])
            gap_table.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#FEF2F2')),
                ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#F87171')),
                ('PADDING', (0,0), (-1,-1), 5),
            ]))
            elements.append(gap_table)
            elements.append(Spacer(1, 10))

        # Remediation Actions Table
        elements.append(Paragraph("<b>5. Actionable Remediation & Sign-Off Checklist</b>", h2_style))
        remediation_headers = ["Action ID", "Remediation Action & Scope", "Owner", "Approval Required", "SLA"]
        remediation_rows = [[Paragraph(f"<b>{h}</b>", meta_style) for h in remediation_headers]]

        for rem in dossier.recommendations:
            remediation_rows.append([
                Paragraph(f"<b>{rem.action_id}</b>", body_style),
                Paragraph(f"<b>{rem.title}</b><br/>{rem.description}<br/><font color='#2563EB'>{rem.policy_reference}</font>", body_style),
                Paragraph(rem.responsible_party, body_style),
                Paragraph(rem.approval_required, body_style),
                Paragraph(f"{rem.deadline_days} days", body_style)
            ])

        rem_table = Table(remediation_rows, colWidths=[60, 205, 110, 110, 45])
        rem_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#E2E8F0')),
            ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#94A3B8')),
            ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
            ('PADDING', (0,0), (-1,-1), 4),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ]))
        elements.append(rem_table)
        elements.append(Spacer(1, 10))

        # Evidentiary Grounding Stamp
        elements.append(KeepTogether([
            Paragraph("<b>6. Multi-Agent Evidentiary Grounding Certificate</b>", h2_style),
            Paragraph(
                f"<b>Status:</b> {'VERIFIED & CERTIFIED' if dossier.validation.is_valid else 'ACTION REQUIRED'} &nbsp;|&nbsp; "
                f"<b>Grounding Faithfulness:</b> {dossier.validation.grounding_faithfulness_score * 100:.1f}% &nbsp;|&nbsp; "
                f"<b>Coverage Ratio:</b> {dossier.validation.evidence_coverage_ratio * 100:.1f}%<br/>"
                f"<b>Auditor Attestation:</b> {dossier.validation.validator_notes}",
                body_style
            ),
            Spacer(1, 6),
            Paragraph(f"<font color='#64748B'>Generated by Policy Compliance Intelligence Microservice • Timestamp: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%SZ')}</font>", meta_style)
        ]))

        doc.build(elements)
        print(f"Compliance audit report PDF successfully generated at: {output_path}")
        return output_path
