"""Build a clean, sectioned salon fact sheet + simple PDF from chat evidence."""

from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
    PageBreak,
    KeepTogether,
)

OUT_MD = Path("kb/fatima-hair-braiding.md")
OUT_PDF = Path("docs/Fatima_Hair_Braiding_Client_Data.pdf")


# ---------------------------------------------------------------------------
# Clean facts (only high-confidence style prices in the Prices section)
# ---------------------------------------------------------------------------

MD = """# Fatima Hair Braiding & Extensions NYC
## Client Data Sheet (from real chats)

Source: Abdullah Chat Data Collection — Instagram/Facebook DMs.
This file is organized for AI booking. Each section is separate on purpose.

---

# 1. Business

| Field | Value |
|---|---|
| Salon name | Fatima Hair Braiding & Extensions NYC |
| Channels | Instagram DM (main), Facebook DM |
| Service type | Hair braiding and extensions |
| Language | English (main) |

---

# 2. Locations

| # | Address |
|---|---|
| 1 | 2944 3rd Ave, Bronx, NY 10455 |
| 2 | 3201 White Plains Road, Bronx, NY 10467 |

**Rule:** Ask which location is convenient. Put only **one** address on the booking card.

---

# 3. Hours

| Item | Value |
|---|---|
| Regular hours | 8:00 AM – 7:30 PM (EST) |
| After 8:00 PM | By appointment only (extra charge) |
| Walk-ins | Yes (confirm with owner for exact walk-in hours) |

**Needs owner confirm:** Some chats also say open 7 days, 8 AM–8 PM.

---

# 4. Style Prices

Only style prices below. Add-ons are in Section 5.

| Style | Price | Notes |
|---|---|---|
| Boho braids (any style under Boho promo) | $200 | Hair included (synthetic). Most common quote. |
| Boho knotless | $200 | Usually under same Boho promo |
| Boho bob / knotless bob | $200 | Under Boho promo when offered |
| Boho twist | $200 | Under Boho promo when offered |
| Box braids | $200 | When quoted under promo / similar |
| Small / waist-length knotless | $240 | Longer / smaller = higher |
| Freestyle cornrows | $160 | |
| Fulani braids | $180 | Needs owner confirm if still current |
| 4 braids | $80 | |
| 2 stitch braids | $40 | |

**Pricing rule:** Price depends on style, size, and length. If the style is not in this table, do **not** invent a price — ask a human.

---

# 5. Add-ons (not style prices)

| Add-on | Price | Notes |
|---|---|---|
| Synthetic hair | Included / free | With Boho promo |
| Human hair | +$60 per pack | Some chats said $50 — confirm with owner |
| Wash and dry | +$20 | |

---

# 6. Deposit and Payment

| Item | Value |
|---|---|
| Deposit | $30 |
| Methods | Zelle or Cash App |
| Handle | +1 (347) 216-6223 |
| Proof | Customer sends screenshot |
| Deposit use | Goes toward total |
| Before screenshot | Say **reserved — pending deposit** |
| After screenshot | Say **confirmed** |

---

# 7. Promotions

| Promo | Detail |
|---|---|
| Boho promo | Any Boho style $200 including hair |
| BRAIDS10 | 10% off all styles |
| Creator collab | 50% off for video/vlog — escalate to human to approve |

---

# 8. Services Offered

Boho braids, Boho knotless, Knotless braids, Box braids, Fulani, Stitch braids, Cornrows, Bora Bora, Tribal, Goddess, Lemonade, Boho twist, Cuban twist, Marley twist, Passion twist, Senegalese twist, Butterfly, Boho bob, Mohawk, Invisible locs, Weave / sew-in, Miracle knots, French curls.

Kids hair: Yes.

---

# 9. After Service

Google review link: https://g.co/kgs/B8LWq2T

---

# 10. Escalate to Human

- Refund / deposit dispute
- Complaint
- Price not in Section 4
- Discount beyond Section 7
- Customer asks for owner / phone call
- Paid deposit reschedule / cancel

---

# Owner must confirm

1. Exact daily hours (8–7:30 vs 8–8)
2. Fulani $180 still correct?
3. Human hair $50 or $60?
4. Full official price list for non-Boho styles
"""


def build_pdf():
    OUT_PDF.parent.mkdir(parents=True, exist_ok=True)
    doc = SimpleDocTemplate(
        str(OUT_PDF),
        pagesize=letter,
        leftMargin=0.7 * inch,
        rightMargin=0.7 * inch,
        topMargin=0.6 * inch,
        bottomMargin=0.6 * inch,
    )
    styles = getSampleStyleSheet()
    title = ParagraphStyle(
        "T",
        parent=styles["Heading1"],
        alignment=TA_CENTER,
        fontSize=16,
        spaceAfter=6,
    )
    h2 = ParagraphStyle(
        "H2",
        parent=styles["Heading2"],
        fontSize=12,
        textColor=colors.HexColor("#1a1a1a"),
        spaceBefore=14,
        spaceAfter=8,
    )
    body = ParagraphStyle(
        "B",
        parent=styles["Normal"],
        fontSize=9,
        leading=12,
        spaceAfter=4,
    )
    note = ParagraphStyle(
        "N",
        parent=styles["Normal"],
        fontSize=8,
        leading=11,
        textColor=colors.HexColor("#444444"),
        spaceAfter=6,
    )

    story = []
    story.append(Paragraph("Fatima Hair Braiding & Extensions NYC", title))
    story.append(
        Paragraph(
            "Client Data Sheet — from real Instagram/Facebook chats<br/>"
            "Each section is separate. Section 4 = style prices only.",
            ParagraphStyle("sub", parent=body, alignment=TA_CENTER),
        )
    )
    story.append(Spacer(1, 10))

    def table(headers, rows):
        data = [headers] + rows
        t = Table(data, hAlign="LEFT", colWidths=None)
        t.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#222222")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, -1), 8),
                    ("GRID", (0, 0), (-1, -1), 0.4, colors.grey),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 5),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 5),
                    ("TOPPADDING", (0, 0), (-1, -1), 4),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f5f5f5")]),
                ]
            )
        )
        return t

    story.append(Paragraph("1. Business", h2))
    story.append(
        table(
            ["Field", "Value"],
            [
                ["Salon name", "Fatima Hair Braiding & Extensions NYC"],
                ["Channels", "Instagram DM (main), Facebook DM"],
                ["Service", "Hair braiding and extensions"],
                ["Language", "English (main)"],
            ],
        )
    )

    story.append(Paragraph("2. Locations", h2))
    story.append(
        table(
            ["#", "Address"],
            [
                ["1", "2944 3rd Ave, Bronx, NY 10455"],
                ["2", "3201 White Plains Road, Bronx, NY 10467"],
            ],
        )
    )
    story.append(
        Paragraph(
            "<b>Rule:</b> Ask which location. Put only ONE address on the booking card.",
            note,
        )
    )

    story.append(Paragraph("3. Hours", h2))
    story.append(
        table(
            ["Item", "Value"],
            [
                ["Regular hours", "8:00 AM – 7:30 PM (EST)"],
                ["After 8:00 PM", "By appointment only (extra charge)"],
                ["Walk-ins", "Yes (confirm exact walk-in hours with owner)"],
            ],
        )
    )
    story.append(
        Paragraph(
            "<b>Owner confirm:</b> Some chats also say 7 days, 8 AM–8 PM.",
            note,
        )
    )

    story.append(Paragraph("4. Style Prices (only)", h2))
    story.append(
        Paragraph(
            "Add-ons are NOT in this table — see Section 5.",
            note,
        )
    )
    story.append(
        table(
            ["Style", "Price", "Notes"],
            [
                ["Boho braids (Boho promo)", "$200", "Hair included (synthetic). Most common."],
                ["Boho knotless", "$200", "Usually same Boho promo"],
                ["Boho bob / knotless bob", "$200", "When under Boho promo"],
                ["Boho twist", "$200", "When under Boho promo"],
                ["Box braids", "$200", "When quoted under promo"],
                ["Small / waist knotless", "$240", "Longer / smaller = higher"],
                ["Freestyle cornrows", "$160", ""],
                ["Fulani braids", "$180", "Confirm with owner if still current"],
                ["4 braids", "$80", ""],
                ["2 stitch braids", "$40", ""],
            ],
        )
    )
    story.append(
        Paragraph(
            "<b>Rule:</b> Price depends on style, size, length. If not in this table → do not invent → escalate to human.",
            note,
        )
    )

    story.append(Paragraph("5. Add-ons (not style prices)", h2))
    story.append(
        table(
            ["Add-on", "Price", "Notes"],
            [
                ["Synthetic hair", "Included / free", "With Boho promo"],
                ["Human hair", "+$60 / pack", "Some chats $50 — confirm owner"],
                ["Wash and dry", "+$20", ""],
            ],
        )
    )

    story.append(Paragraph("6. Deposit and Payment", h2))
    story.append(
        table(
            ["Item", "Value"],
            [
                ["Deposit", "$30"],
                ["Methods", "Zelle or Cash App"],
                ["Handle", "+1 (347) 216-6223"],
                ["Proof", "Screenshot required"],
                ["Deposit use", "Goes toward total"],
                ["Before screenshot", 'Say "reserved — pending deposit"'],
                ["After screenshot", 'Say "confirmed"'],
            ],
        )
    )

    story.append(Paragraph("7. Promotions", h2))
    story.append(
        table(
            ["Promo", "Detail"],
            [
                ["Boho promo", "Any Boho style $200 including hair"],
                ["BRAIDS10", "10% off all styles"],
                ["Creator collab", "50% off for video — escalate to human"],
            ],
        )
    )

    story.append(Paragraph("8. Services Offered", h2))
    story.append(
        Paragraph(
            "Boho braids, Boho knotless, Knotless, Box braids, Fulani, Stitch, Cornrows, "
            "Bora Bora, Tribal, Goddess, Lemonade, Boho twist, Cuban twist, Marley twist, "
            "Passion twist, Senegalese, Butterfly, Boho bob, Mohawk, Invisible locs, "
            "Weave / sew-in, Miracle knots, French curls. <b>Kids hair: Yes.</b>",
            body,
        )
    )

    story.append(Paragraph("9. After Service", h2))
    story.append(Paragraph("Google review: https://g.co/kgs/B8LWq2T", body))

    story.append(Paragraph("10. Escalate to Human", h2))
    for line in [
        "Refund / deposit dispute",
        "Complaint",
        "Price not in Section 4",
        "Discount beyond Section 7",
        "Asks for owner / phone call",
        "Paid deposit reschedule / cancel",
    ]:
        story.append(Paragraph(f"• {line}", body))

    story.append(Paragraph("Owner Must Confirm", h2))
    for line in [
        "Exact daily hours (8–7:30 vs 8–8)",
        "Fulani $180 still correct?",
        "Human hair $50 or $60?",
        "Full official price list for non-Boho styles",
    ]:
        story.append(Paragraph(f"• {line}", body))

    doc.build(story)
    print(f"PDF -> {OUT_PDF}")


if __name__ == "__main__":
    OUT_MD.write_text(MD, encoding="utf-8")
    print(f"MD  -> {OUT_MD}")
    build_pdf()
