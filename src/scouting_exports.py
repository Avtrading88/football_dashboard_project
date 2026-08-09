"""CSV and PDF exports for the transfer-shortlist workspace."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from datetime import datetime, timezone
from io import BytesIO
from pathlib import Path
from typing import Any

import pandas as pd
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    KeepTogether,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from src.shortlist_store import decode_snapshot


EXPORT_METRICS = (
    "Minutes Played",
    "Matches Played",
    "Goals",
    "Assists",
    "Goals per 90",
    "Assists per 90",
    "Goals + Assists per 90",
    "Shots on Target per 90",
    "Defensive Actions per 90",
    "Save Percentage",
    "Clean Sheet Percentage",
    "Player Score",
    "Young Talent Score",
    "Role Score",
)


def _entries_list(entries: Iterable[Mapping[str, Any]] | pd.DataFrame) -> list[dict[str, Any]]:
    if isinstance(entries, pd.DataFrame):
        return entries.to_dict(orient="records")
    return [dict(entry) for entry in entries]


def _display_value(value: Any, *, currency: bool = False) -> str:
    if value is None or value is pd.NA or value == "":
        return "-"
    try:
        if pd.isna(value):
            return "-"
    except (TypeError, ValueError):
        pass
    if currency:
        return f"EUR {float(value):,.0f}"
    if isinstance(value, float):
        return f"{value:.2f}".rstrip("0").rstrip(".")
    return str(value)


def prepare_shortlist_export_dataframe(
    entries: Iterable[Mapping[str, Any]] | pd.DataFrame,
) -> pd.DataFrame:
    """Flatten workflow fields and saved football statistics for export."""

    rows: list[dict[str, Any]] = []
    for entry in _entries_list(entries):
        snapshot = decode_snapshot(entry)
        row = {
            "Player Record ID": entry.get("player_record_id"),
            "Player Name": entry.get("player_name"),
            "Nationality": entry.get("nationality"),
            "Position": entry.get("position"),
            "Club": entry.get("club"),
            "League": entry.get("league"),
            "Age": entry.get("age"),
            "Status": entry.get("status"),
            "Priority": entry.get("priority"),
            "Target Fee EUR": entry.get("target_fee_eur"),
            "Scout Rating": entry.get("scout_rating"),
            "Notes": entry.get("notes"),
            "Source Page": entry.get("source_page"),
            "Added At": entry.get("created_at"),
            "Updated At": entry.get("updated_at"),
        }
        for metric in EXPORT_METRICS:
            if metric in snapshot:
                row[metric] = snapshot.get(metric)
        rows.append(row)
    return pd.DataFrame(rows)


def shortlist_to_csv_bytes(
    entries: Iterable[Mapping[str, Any]] | pd.DataFrame,
) -> bytes:
    """Return an Excel-friendly UTF-8 CSV export."""

    dataframe = prepare_shortlist_export_dataframe(entries)
    return dataframe.to_csv(index=False).encode("utf-8-sig")


def _register_report_fonts() -> tuple[str, str]:
    candidates = [
        (
            Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
            Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"),
        ),
        (
            Path("C:/Windows/Fonts/arial.ttf"),
            Path("C:/Windows/Fonts/arialbd.ttf"),
        ),
    ]
    for regular_path, bold_path in candidates:
        if regular_path.exists() and bold_path.exists():
            try:
                pdfmetrics.registerFont(TTFont("ScoutSans", str(regular_path)))
                pdfmetrics.registerFont(TTFont("ScoutSansBold", str(bold_path)))
                return "ScoutSans", "ScoutSansBold"
            except Exception:
                continue
    return "Helvetica", "Helvetica-Bold"


def build_scouting_report_pdf(
    entries: Iterable[Mapping[str, Any]] | pd.DataFrame,
    *,
    report_title: str = "Transfer Shortlist Scouting Report",
) -> bytes:
    """Create a polished, multi-player PDF scouting report."""

    candidates = _entries_list(entries)
    if not candidates:
        raise ValueError("At least one shortlist player is required for a PDF report.")

    regular_font, bold_font = _register_report_fonts()
    output = BytesIO()
    document = SimpleDocTemplate(
        output,
        pagesize=A4,
        rightMargin=16 * mm,
        leftMargin=16 * mm,
        topMargin=18 * mm,
        bottomMargin=17 * mm,
        title=report_title,
        author="European Football Analytics Dashboard",
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "ScoutTitle",
        parent=styles["Title"],
        fontName=bold_font,
        fontSize=21,
        leading=25,
        textColor=colors.HexColor("#102A43"),
        alignment=TA_LEFT,
        spaceAfter=5 * mm,
    )
    player_style = ParagraphStyle(
        "PlayerTitle",
        parent=styles["Heading1"],
        fontName=bold_font,
        fontSize=18,
        leading=22,
        textColor=colors.HexColor("#0F766E"),
        spaceAfter=2 * mm,
    )
    section_style = ParagraphStyle(
        "Section",
        parent=styles["Heading2"],
        fontName=bold_font,
        fontSize=11,
        leading=14,
        textColor=colors.HexColor("#102A43"),
        spaceBefore=4 * mm,
        spaceAfter=2 * mm,
    )
    body_style = ParagraphStyle(
        "Body",
        parent=styles["BodyText"],
        fontName=regular_font,
        fontSize=9.5,
        leading=14,
        textColor=colors.HexColor("#334E68"),
    )
    small_center_style = ParagraphStyle(
        "SmallCenter",
        parent=body_style,
        fontSize=8,
        leading=10,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#627D98"),
    )

    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    def draw_footer(canvas, doc):
        canvas.saveState()
        canvas.setStrokeColor(colors.HexColor("#D9E2EC"))
        canvas.line(16 * mm, 12 * mm, A4[0] - 16 * mm, 12 * mm)
        canvas.setFont(regular_font, 7.5)
        canvas.setFillColor(colors.HexColor("#627D98"))
        canvas.drawString(16 * mm, 8 * mm, "European Football Analytics Dashboard")
        canvas.drawRightString(
            A4[0] - 16 * mm,
            8 * mm,
            f"Generated {generated_at} | Page {doc.page}",
        )
        canvas.restoreState()

    story: list[Any] = [
        Paragraph(report_title, title_style),
        Paragraph(
            f"Recruitment report for {len(candidates)} shortlisted candidate(s). "
            "Statistics are snapshots from the loaded dashboard dataset.",
            body_style,
        ),
        Spacer(1, 5 * mm),
    ]

    for candidate_index, entry in enumerate(candidates):
        snapshot = decode_snapshot(entry)
        player_name = _display_value(entry.get("player_name"))
        club = _display_value(entry.get("club"))
        league = _display_value(entry.get("league"))
        position = _display_value(entry.get("position"))
        nationality = _display_value(entry.get("nationality"))
        age = _display_value(entry.get("age"))
        status = _display_value(entry.get("status"))
        priority = _display_value(entry.get("priority"))

        story.append(Paragraph(player_name, player_style))
        story.append(
            Paragraph(
                f"{club} | {league} | {position} | {nationality} | Age {age}",
                body_style,
            )
        )
        story.append(Spacer(1, 3 * mm))

        workflow_table = Table(
            [
                ["Recruitment status", "Priority", "Target fee", "Scout rating"],
                [
                    status,
                    priority,
                    _display_value(entry.get("target_fee_eur"), currency=True),
                    (
                        f"{_display_value(entry.get('scout_rating'))}/100"
                        if entry.get("scout_rating") is not None
                        else "-"
                    ),
                ],
            ],
            colWidths=[43 * mm, 35 * mm, 45 * mm, 35 * mm],
            hAlign="LEFT",
        )
        workflow_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#102A43")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("FONTNAME", (0, 0), (-1, 0), bold_font),
                    ("FONTNAME", (0, 1), (-1, -1), regular_font),
                    ("FONTSIZE", (0, 0), (-1, -1), 8.5),
                    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                    ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#F0F7FA")),
                    ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#BCCCDC")),
                    ("TOPPADDING", (0, 0), (-1, -1), 6),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ]
            )
        )
        story.append(workflow_table)

        metric_rows = []
        for metric in EXPORT_METRICS:
            if metric in snapshot and snapshot.get(metric) is not None:
                metric_rows.append([metric, _display_value(snapshot.get(metric))])
        if metric_rows:
            story.append(Paragraph("Performance snapshot", section_style))
            midpoint = (len(metric_rows) + 1) // 2
            left_metrics = metric_rows[:midpoint]
            right_metrics = metric_rows[midpoint:]
            while len(right_metrics) < len(left_metrics):
                right_metrics.append(["", ""])
            combined_rows = [
                left_metrics[index] + right_metrics[index]
                for index in range(len(left_metrics))
            ]
            metrics_table = Table(
                combined_rows,
                colWidths=[48 * mm, 25 * mm, 48 * mm, 25 * mm],
                hAlign="LEFT",
            )
            metrics_table.setStyle(
                TableStyle(
                    [
                        ("FONTNAME", (0, 0), (-1, -1), regular_font),
                        ("FONTNAME", (0, 0), (0, -1), bold_font),
                        ("FONTNAME", (2, 0), (2, -1), bold_font),
                        ("FONTSIZE", (0, 0), (-1, -1), 8),
                        ("TEXTCOLOR", (0, 0), (-1, -1), colors.HexColor("#334E68")),
                        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F8FAFC")),
                        ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#D9E2EC")),
                        ("ALIGN", (1, 0), (1, -1), "RIGHT"),
                        ("ALIGN", (3, 0), (3, -1), "RIGHT"),
                        ("TOPPADDING", (0, 0), (-1, -1), 4),
                        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                    ]
                )
            )
            story.append(metrics_table)

        story.append(Paragraph("Scout notes", section_style))
        notes = str(entry.get("notes") or "No scout notes have been added yet.")
        notes_box = Table(
            [[Paragraph(notes.replace("\n", "<br/>"), body_style)]],
            colWidths=[158 * mm],
        )
        notes_box.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#FFFBEA")),
                    ("BOX", (0, 0), (-1, -1), 0.6, colors.HexColor("#F0B429")),
                    ("LEFTPADDING", (0, 0), (-1, -1), 8),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                    ("TOPPADDING", (0, 0), (-1, -1), 8),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
                ]
            )
        )
        story.append(KeepTogether([notes_box, Spacer(1, 3 * mm)]))
        story.append(
            Paragraph(
                "Analytical outputs support recruitment review and do not replace live scouting, "
                "medical checks, contract review, or professional judgment.",
                small_center_style,
            )
        )

        if candidate_index < len(candidates) - 1:
            story.append(PageBreak())

    document.build(story, onFirstPage=draw_footer, onLaterPages=draw_footer)
    return output.getvalue()

