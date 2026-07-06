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

import re

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

    # -------- Vendor --------
    vendor = ""

    # Look for Acme-XXXX pattern anywhere
    m = re.search(r"(Acme-[A-Za-z0-9]+.*)", text, re.IGNORECASE)
    if m:
        vendor = m.group(1).split("\n")[0].strip()

    # -------- Currency --------
    cur = re.search(r"\b(USD|EUR|GBP)\b", text)
    currency = cur.group(1).upper() if cur else ""

    # -------- Amount --------
    amounts = re.findall(r"\d+(?:\.\d+)?", text)

    amount = 0.0

    if amounts:
        amount = max(float(x) for x in amounts)

    # -------- Date --------
    d = re.search(r"20\d{2}-\d{2}-\d{2}", text)

    date = d.group(0) if d else ""

    return InvoiceResponse(
        vendor=vendor,
        amount=amount,
        currency=currency,
        date=date
    )