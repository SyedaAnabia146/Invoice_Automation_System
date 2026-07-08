import os
from fpdf import FPDF

# Ensure directory exists
os.makedirs(os.path.join("data", "invoices"), exist_ok=True)

pdf = FPDF()
pdf.add_page()
pdf.set_font("Arial", size=12)

# Writing sample invoice data that matches our regex
pdf.cell(200, 10, txt="ABC Vendor Solutions", ln=1, align="L")
pdf.cell(200, 10, txt="Invoice #: INV-2026-001", ln=2, align="L")
pdf.cell(200, 10, txt="Invoice Date: 08-July-2026", ln=3, align="L")
pdf.cell(200, 10, txt="Due Date: 25-July-2026", ln=4, align="L")
pdf.cell(200, 10, txt="Customer: Syeda Anabia", ln=5, align="L")
pdf.cell(200, 10, txt="Tax: $ 15.00", ln=6, align="L")
pdf.cell(200, 10, txt="Total Amount: $ 150.00", ln=7, align="L")

output_path = os.path.join("data", "invoices", "test_invoice.pdf")
pdf.output(output_path)
print(f"Success! Created sample PDF at: {output_path}")