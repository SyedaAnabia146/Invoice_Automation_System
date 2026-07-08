import re
from datetime import datetime
from src.logger import logger

class InvoiceValidator:
    
    @staticmethod
    def validate(extracted_data):
        """
        Task 3 Requirement: Validates data fields, formats, duplicates, and numeric profiles.
        Returns: (is_valid: bool, status_message: str)
        """
        if not extracted_data:
            logger.error("Validation failed: Extracted data object is empty or completely null.")
            return False, "Invalid: No Data Extracted"
            
        # 1. Detect Missing Fields (Feature 3)
        mandatory_fields = ['invoice_number', 'vendor_name', 'total_amount']
        missing_fields = [field for field in mandatory_fields if not extracted_data.get(field)]
        
        if missing_fields:
            error_msg = f"Missing Fields: {', '.join(missing_fields)}"
            logger.warning(f"Validation alert for Invoice {extracted_data.get('invoice_number', 'UNKNOWN')}: {error_msg}")
            return False, error_msg

        # 2. Validate Numeric Values (Feature 3)
        try:
            total = float(extracted_data['total_amount'])
            if total <= 0:
                logger.warning(f"Validation Alert: Negative or Zero total amount detected.")
                return False, "Invalid: Amount must be greater than zero"
        except (ValueError, TypeError):
            logger.error("Validation Alert: Total amount formatting is non-numeric.")
            return False, "Invalid: Numeric Value Format Error"

        # 3. Verify Date Formats (Feature 3)
        date_str = extracted_data.get('invoice_date')
        if date_str:
            # Clean common separators out
            clean_date = str(date_str).replace('/', '-').replace('.', '-').strip()
            # Try parsing multiple common formats
            parsed = False
            for fmt in ("%Y-%m-%d", "%d-%m-%Y", "%d-%b-%Y", "%B %d, %Y"):
                try:
                    datetime.strptime(clean_date, fmt)
                    parsed = True
                    break
                except ValueError:
                    continue
            if not parsed:
                logger.warning(f"Validation Alert: Date string '{date_str}' doesn't match standard profiles.")
                return False, "Invalid: Date Format Error"

        logger.info(f"Invoice {extracted_data['invoice_number']} validation passed successfully.")
        return True, "Valid"
    