from fastapi import FastAPI
from pydantic import BaseModel
from datetime import datetime
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

    text = req.text

    if not text.strip():
        return InvoiceResponse(
            vendor="",
            amount=0,
            currency="USD",
            date=""
        )

    # Vendor
    vendor = ""
    patterns = [
        r"Vendor[:\-]\s*(.+)",
        r"From[:\-]\s*(.+)",
        r"Issued by[:\-]\s*(.+)"
    ]

    for p in patterns:
        m = re.search(p, text, re.IGNORECASE)
        if m:
            vendor = m.group(1).split("\n")[0].strip()
            break

    # Currency
    cur = re.search(r"\b(USD|EUR|GBP)\b", text)

    currency = cur.group(1).upper() if cur else "USD"

    # Amount
    amt = re.search(
        r"(?:Total|Amount|Due|Total Due)[^\d]*([\d]+(?:\.\d+)?)",
        text,
        re.IGNORECASE,
    )

    amount = float(amt.group(1)) if amt else 0

    # Date
    d = re.search(r"(20\d\d-\d\d-\d\d)", text)

    date = d.group(1) if d else ""

    return InvoiceResponse(
        vendor=vendor,
        amount=amount,
        currency=currency,
        date=date,
    )