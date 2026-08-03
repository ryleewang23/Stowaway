from collections import defaultdict
from io import BytesIO

import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

from item_helpers import CATEGORY_ORDER


def create_csv_bytes(items):
    rows = []

    for item in items:
        rows.append(
            {
                "Item": item["name"],
                "Category": item["category"],
                "Source": item["source"],
                "Reason": item["reason"],
                "Packed": "Yes" if item["packed"] else "No"
            }
        )

    return pd.DataFrame(rows).to_csv(
        index=False
    ).encode("utf-8")


def create_pdf_bytes(
        destination,
        start_date,
        end_date,
        items):
    buffer = BytesIO()

    pdf = canvas.Canvas(
        buffer,
        pagesize=letter
    )

    page_width, page_height = letter
    left_margin = 50
    y_position = page_height - 55

    pdf.setTitle(
        f"Stowaway Packing List - {destination}"
    )

    pdf.setFont("Helvetica-Bold", 20)
    pdf.drawString(
        left_margin,
        y_position,
        "Stowaway Packing List"
    )

    y_position -= 25

    pdf.setFont("Helvetica", 10)
    pdf.drawString(
        left_margin,
        y_position,
        f"Destination: {destination}"
    )

    y_position -= 15

    pdf.drawString(
        left_margin,
        y_position,
        f"Dates: {start_date} to {end_date}"
    )

    y_position -= 26

    grouped = defaultdict(list)

    for item in items:
        grouped[item["category"]].append(item)

    ordered_categories = CATEGORY_ORDER + sorted(
        category
        for category in grouped
        if category not in CATEGORY_ORDER
    )

    for category in ordered_categories:
        if not grouped.get(category):
            continue

        if y_position < 80:
            pdf.showPage()
            y_position = page_height - 55

        pdf.setFont("Helvetica-Bold", 12)
        pdf.drawString(
            left_margin,
            y_position,
            category
        )

        y_position -= 18

        for item in grouped[category]:
            if y_position < 60:
                pdf.showPage()
                y_position = page_height - 55

            mark = "[X]" if item["packed"] else "[ ]"

            pdf.setFont("Helvetica", 9)
            pdf.drawString(
                left_margin + 10,
                y_position,
                f"{mark} {item['name']}"[:100]
            )

            y_position -= 14

        y_position -= 6

    pdf.save()
    buffer.seek(0)

    return buffer.getvalue()
