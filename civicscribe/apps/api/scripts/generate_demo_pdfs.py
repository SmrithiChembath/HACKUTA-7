from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.pdfbase import pdfdoc
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import black
import os

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))


def ensure_dir(path: str):
    os.makedirs(os.path.dirname(path), exist_ok=True)


def create_snap_form(path: str):
    ensure_dir(path)
    c = canvas.Canvas(path, pagesize=letter)
    width, height = letter
    c.setFont("Helvetica-Bold", 16)
    c.drawString(72, height - 72, "SNAP Demo Form")
    c.setFont("Helvetica", 11)

    fields = [
        ("Page1.Name", "Full Name", 72, height - 120, 300, 18),
        ("Page1.Name_Repeat", "Full Name (repeat)", 72, height - 145, 300, 18),
        ("Page1.DOB", "Date of Birth", 72, height - 170, 150, 18),
        ("Page1.HouseholdSize", "Household Size", 72, height - 195, 80, 18),
        ("Page1.Address", "Home Address", 72, height - 220, 400, 18),
        ("Page1.Phone", "Phone", 72, height - 245, 180, 18),
        ("Page1.Email", "Email", 72, height - 270, 220, 18),
        ("Page1.MonthlyGrossIncome", "Monthly Gross Income", 72, height - 295, 160, 18),
        ("Page1.MonthlyGrossIncome_Box2", "Monthly Gross Income (box 2)", 240, height - 295, 160, 18),
        ("Page1.SSN4", "SSN Last 4 (optional)", 72, height - 320, 100, 18),
        ("Page1.SignatureName", "Signature Name", 72, height - 370, 300, 18),
    ]

    for name, label, x, y, w, h in fields:
        c.drawString(x, y + 20, label)
        c.acroForm.textfield(
            name=name,
            x=x,
            y=y,
            width=w,
            height=h,
            borderStyle="underlined",
            borderColor=black,
            fillColor=None,
            textColor=black,
            forceBorder=True,
        )

    c.showPage()
    c.save()


def create_volunteer_form(path: str):
    ensure_dir(path)
    c = canvas.Canvas(path, pagesize=letter)
    width, height = letter
    c.setFont("Helvetica-Bold", 16)
    c.drawString(72, height - 72, "Volunteer Waiver Demo")
    c.setFont("Helvetica", 11)

    fields = [
        ("Page1.Name", "Full Name", 72, height - 120, 300, 18),
        ("Page1.Email", "Email", 72, height - 150, 250, 18),
        ("Page1.Phone", "Phone", 72, height - 180, 180, 18),
        ("Page1.EventDate", "Event Date", 72, height - 210, 150, 18),
        ("Page1.Agree", "I agree (type YES)", 72, height - 240, 120, 18),
    ]

    for name, label, x, y, w, h in fields:
        c.drawString(x, y + 20, label)
        c.acroForm.textfield(
            name=name,
            x=x,
            y=y,
            width=w,
            height=h,
            borderStyle="underlined",
            borderColor=black,
            fillColor=None,
            textColor=black,
            forceBorder=True,
        )

    c.showPage()
    c.save()


def create_sample_income_statement(path: str):
    ensure_dir(path)
    c = canvas.Canvas(path, pagesize=letter)
    w, h = letter
    c.setFont("Helvetica-Bold", 14)
    c.drawString(72, h - 72, "Social Security Benefit Statement")
    c.setFont("Helvetica", 12)
    c.drawString(72, h - 110, "Beneficiary: Maria Example")
    c.drawString(72, h - 130, "Monthly Benefit: $950.00")
    c.drawString(72, h - 150, "Statement Date: June 15, 2025")
    c.showPage()
    c.save()


if __name__ == "__main__":
    create_snap_form(os.path.join(ROOT, "packs/snap/form.pdf"))
    create_volunteer_form(os.path.join(ROOT, "packs/volunteer_waiver/form.pdf"))
    create_sample_income_statement(os.path.join(ROOT, "packs/snap/sample_income_statement.pdf"))
