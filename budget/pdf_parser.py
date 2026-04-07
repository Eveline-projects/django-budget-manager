import pdfplumber
import re

def extract_transactions(pdf_path):
    text = ""

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            if page.extract_text():
                text += page.extract_text() + "\n"

    pattern = r"(\d{2}-\d{2}-\d{4})\s+(.+?)\s+([+-]?\d+,\d{2})"
    matches = re.findall(pattern, text)

    transactions = []
    for date, desc, amount in matches:
        transactions.append({
            "date": date,
            "description": desc.strip(),
            "amount": float(amount.replace(",", "."))
        })

    return transactions