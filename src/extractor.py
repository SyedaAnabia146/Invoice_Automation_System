import re
import pdfplumber
from src.logger import logger

class InvoiceExtractor:
    def __init__(self, pdf_path):
        self.pdf_path = pdf_path
        self.text = ""
        self.extract_raw_text()

    def extract_raw_text(self):
        """Extracts all raw text from the provided PDF file."""
        try:
            with pdfplumber.open(self.pdf_path) as pdf:
                full_text = []
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        full_text.append(page_text)
                self.text = "\n".join(full_text)
            logger.info(f"Successfully extracted raw text from {self.pdf_path}")
        except Exception as e:
            logger.error(f"Error reading PDF file {self.pdf_path}: {str(e)}")
            self.text = ""

    def parse_invoice_data(self):
        """Parses specific fields from the extracted text using Regex."""
        # Default dictionary structure as required by task details
        data = {
            "invoice_number": None,
            "vendor_name": "Unknown Vendor",
            "customer_name": None,
            "invoice_date": None,
            "due_date": None,
            "tax_amount": 0.0,
            "total_amount": 0.0,
            "currency": "USD",
            "payment_status": "Pending"
        }

        if not self.text:
            return data

        # 1. Extract Invoice Number
        inv_match = re.search(r'(?i)(invoice\s*s*#?|inv-?\d*)\s*:\s*([A-Z0-9-]+)', self.text)
        if inv_match:
            data["invoice_number"] = inv_match.group(2).strip()
        else:
            # Fallback regex for standalone numbers that look like invoice IDs
            inv_fallback = re.search(r'(?i)invoice\s*number\s*([A-Z0-9-]+)', self.text)
            if inv_fallback:
                data["invoice_number"] = inv_fallback.group(1).strip()

        # 2. Extract Total Amount
        amount_match = re.search(r'(?i)(total|total\s*amount|amount\s*due|grand\s*total)\s*:?\s*([$€£]?)\s*([\d,]+\.\d{2})', self.text)
        if amount_match:
            data["total_amount"] = float(amount_match.group(3).replace(',', ''))
            # Currency detection
            curr_symbol = amount_match.group(2)
            if curr_symbol == "$": data["currency"] = "USD"
            elif curr_symbol == "€": data["currency"] = "EUR"
            elif curr_symbol == "£": data["currency"] = "GBP"

        # 3. Extract Invoice Date
        date_match = re.search(r'(?i)(invoice\s*date|date)\s*:\s*([\d\-/A-Za-z ]+)', self.text)
        if date_match:
            data["invoice_date"] = date_match.group(2).strip().split('\n')[0]

        # 4. Extract Due Date
        due_match = re.search(r'(?i)(due\s*date)\s*:\s*([\d\-/A-Za-z ]+)', self.text)
        if due_match:
            data["due_date"] = due_match.group(2).strip().split('\n')[0]

        # 5. Extract Tax Amount
        tax_match = re.search(r'(?i)(tax|vat)\s*:\s*([$€£]?)\s*([\d,]+\.\d{2})', self.text)
        if tax_match:
            data["tax_amount"] = float(tax_match.group(3).replace(',', ''))

        # 6. Extract Vendor Name (Simple fallback strategy for top lines)
        lines = [line.strip() for line in self.text.split('\n') if line.strip()]
        if lines:
            # Usually company name or vendor is in the first 2 lines of an invoice
            data["vendor_name"] = lines[0]

        return data