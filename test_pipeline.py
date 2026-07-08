import os
from src.extractor import InvoiceExtractor
from src.validator import InvoiceValidator
from database.database import add_invoice, init_db, get_connection

def run_test():
    # Initialize database first
    init_db()
    
    # Path to the PDF we created
    pdf_path = os.path.join("data", "invoices", "test_invoice.pdf")
    
    print("--- STEP 1: Extracting Data from PDF ---")
    extractor = InvoiceExtractor(pdf_path)
    extracted_data = extractor.parse_invoice_data()
    print("Extracted Data:", extracted_data)
    
    print("\n--- STEP 2: Validating Extracted Data ---")
    is_valid, status = InvoiceValidator.validate(extracted_data)
    print(f"Is Valid: {is_valid} | Status: {status}")
    
    # Update status in data dictionary for database
    extracted_data["validation_status"] = status
    
    print("\n--- STEP 3: Saving to Database ---")
    result = add_invoice(extracted_data)
    print(f"Database Insertion Result: {result}")

if __name__ == "__main__":
    run_test()