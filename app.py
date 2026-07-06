from fastapi import FastAPI
from pydantic import BaseModel
import re

app = FastAPI()


class InvoiceRequest(BaseModel):
    text: str


class InvoiceResponse(BaseModel):
    vendor: str
    amount: float
    currency: str
    date: str


@app.post("/extract", response_model=InvoiceResponse)
def extract(req: InvoiceRequest):

    text = req.text.strip()

    if not text:
        return InvoiceResponse(
            vendor="",
            amount=0.0,
            currency="USD",
            date=""
        )

    # ---------------- Vendor ----------------
    vendor = ""

    vendor_patterns = [
        r"Vendor\s*:\s*([^\n]+)",
        r"From\s*:\s*([^\n]+)",
        r"Issued\s+by\s*:\s*([^\n]+)",
        r"(Acme-[^\n,]+)",
    ]

    for pattern in vendor_patterns:
        m = re.search(pattern, text, re.IGNORECASE)
        if m:
            vendor = m.group(1).strip()
            break

    # ---------------- Currency ----------------
    currency = ""

    m = re.search(r"\b(USD|EUR|GBP)\b", text, re.IGNORECASE)

    if m:
        currency = m.group(1).upper()

    # ---------------- Amount ----------------
    amount = 0.0

    amount_patterns = [

        r"Total\s*Due\s*[:\-]?\s*(?:USD|EUR|GBP)?\s*\$?([0-9]+(?:\.[0-9]+)?)",
        r"Amount\s*Due\s*[:\-]?\s*(?:USD|EUR|GBP)?\s*\$?([0-9]+(?:\.[0-9]+)?)",
        r"Balance\s*Due\s*[:\-]?\s*(?:USD|EUR|GBP)?\s*\$?([0-9]+(?:\.[0-9]+)?)",
        r"Grand\s*Total\s*[:\-]?\s*(?:USD|EUR|GBP)?\s*\$?([0-9]+(?:\.[0-9]+)?)",
        r"Total\s*[:\-]?\s*(?:USD|EUR|GBP)?\s*\$?([0-9]+(?:\.[0-9]+)?)",
        r"(?:USD|EUR|GBP)\s*\$?([0-9]+(?:\.[0-9]+)?)",
    ]

    for pattern in amount_patterns:
        m = re.search(pattern, text, re.IGNORECASE)
        if m:
            amount = float(m.group(1))
            break

    # ---------------- Date ----------------
    date = ""

    m = re.search(r"\b20\d{2}-\d{2}-\d{2}\b", text)

    if m:
        date = m.group(0)

    return InvoiceResponse(
        vendor=vendor,
        amount=amount,
        currency=currency,
        date=date,
    )