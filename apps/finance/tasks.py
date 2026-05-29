"""Zadania asynchroniczne Celery: generowanie raportow i analiza AI."""
from __future__ import annotations

import csv
import io
from datetime import datetime

from celery import shared_task
from django.core.files.base import ContentFile
from django.utils import timezone

from . import selectors
from .models import Report


@shared_task
def generate_report(report_id: int) -> str:
    """Generuje raport zaleznie od typu. Uruchamiane przez kolejke Redis."""
    report = Report.objects.select_related("user").get(pk=report_id)
    report.status = Report.Status.PROCESSING
    report.save(update_fields=["status"])

    try:
        if report.type == Report.ReportType.CSV:
            _build_csv(report)
        elif report.type == Report.ReportType.PDF:
            _build_pdf(report)
        elif report.type == Report.ReportType.AI:
            report.result = _analyze_ai(report)
        report.status = Report.Status.DONE
        report.completed_at = timezone.now()
        report.save()
    except Exception as exc:  # noqa: BLE001 - chcemy zapisac kazdy blad
        report.status = Report.Status.FAILED
        report.error = str(exc)
        report.completed_at = timezone.now()
        report.save()
        raise
    return report.status


def _build_csv(report: Report) -> None:
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(["data", "typ", "kategoria", "kwota", "opis"])
    qs = selectors.transaction_list(user=report.user)
    if report.month and report.year:
        qs = qs.filter(date__month=report.month, date__year=report.year)
    for t in qs:
        writer.writerow(
            [
                t.date.isoformat(),
                t.get_type_display(),
                t.category.name if t.category else "",
                t.amount,
                t.description,
            ]
        )
    name = f"raport_{report.pk}.csv"
    report.file.save(name, ContentFile(buffer.getvalue().encode("utf-8")), save=False)


def _build_pdf(report: Report) -> None:
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfgen import canvas

    month = report.month or datetime.now().month
    year = report.year or datetime.now().year
    summary = selectors.stats_summary(user=report.user, month=month, year=year)
    by_cat = selectors.stats_by_category(user=report.user, month=month, year=year)

    buffer = io.BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    y = height - 60

    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(50, y, f"Raport finansowy {month:02d}/{year}")
    y -= 40
    pdf.setFont("Helvetica", 12)
    pdf.drawString(50, y, f"Przychody: {summary['income']} PLN")
    y -= 20
    pdf.drawString(50, y, f"Wydatki:   {summary['expense']} PLN")
    y -= 20
    pdf.drawString(50, y, f"Bilans:    {summary['balance']} PLN")
    y -= 40
    pdf.setFont("Helvetica-Bold", 13)
    pdf.drawString(50, y, "Wydatki wg kategorii:")
    y -= 25
    pdf.setFont("Helvetica", 11)
    for row in by_cat:
        pdf.drawString(60, y, f"- {row['category']}: {row['total']} PLN")
        y -= 18
    pdf.showPage()
    pdf.save()

    name = f"raport_{report.pk}.pdf"
    report.file.save(name, ContentFile(buffer.getvalue()), save=False)


def _analyze_ai(report: Report) -> str:
    """Analiza wydatkow. Uzywa Anthropic API jesli ustawiono klucz,
    w przeciwnym razie generuje analize heurystyczna (fallback)."""
    from django.conf import settings

    month = report.month or datetime.now().month
    year = report.year or datetime.now().year
    summary = selectors.stats_summary(user=report.user, month=month, year=year)
    by_cat = selectors.stats_by_category(user=report.user, month=month, year=year)

    if settings.ANTHROPIC_API_KEY:
        return _analyze_with_anthropic(summary, by_cat)
    return _analyze_heuristic(summary, by_cat)


def _analyze_heuristic(summary: dict, by_cat: list[dict]) -> str:
    income = float(summary["income"])
    expense = float(summary["expense"])
    balance = float(summary["balance"])
    lines = [f"Analiza za {summary['month']:02d}/{summary['year']}:", ""]
    if income == 0 and expense == 0:
        return "Brak danych do analizy w tym okresie."

    savings_rate = (balance / income * 100) if income else 0
    lines.append(f"- Stopa oszczednosci: {savings_rate:.0f}% przychodow.")
    if balance < 0:
        lines.append("- UWAGA: wydatki przekroczyly przychody w tym miesiacu.")
    elif savings_rate < 10:
        lines.append("- Niska stopa oszczednosci - rozwaz ograniczenie wydatkow.")
    else:
        lines.append("- Dobra kontrola budzetu, oszczednosci na zdrowym poziomie.")

    if by_cat:
        top = by_cat[0]
        share = (float(top["total"]) / expense * 100) if expense else 0
        lines.append(
            f"- Najwiekszy wydatek: '{top['category']}' "
            f"({top['total']} PLN, {share:.0f}% wszystkich wydatkow)."
        )
        if share > 40:
            lines.append(
                f"  Kategoria '{top['category']}' dominuje budzet - "
                "warto przyjrzec sie tym wydatkom."
            )
    return "\n".join(lines)


def _analyze_with_anthropic(summary: dict, by_cat: list[dict]) -> str:
    """Realna analiza przez Claude API (gdy ustawiono ANTHROPIC_API_KEY)."""
    from django.conf import settings

    try:
        import anthropic
    except ImportError:
        return _analyze_heuristic(summary, by_cat)

    client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
    prompt = (
        "Jestes doradca finansowym. Na podstawie danych wydatkow przygotuj "
        "krotka analize i 3 rekomendacje po polsku.\n"
        f"Przychody: {summary['income']}, Wydatki: {summary['expense']}, "
        f"Bilans: {summary['balance']}.\n"
        f"Wydatki wg kategorii: {by_cat}"
    )
    message = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=500,
        messages=[{"role": "user", "content": prompt}],
    )
    return message.content[0].text
