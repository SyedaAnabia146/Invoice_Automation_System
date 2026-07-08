import sqlite3
import os
from src.logger import logger

DB_PATH = os.path.join("database", "invoices.db")

def get_connection():
    """Establishes connection to SQLite database."""
    return sqlite3.connect(DB_PATH)

def init_db():
    """Initializes the database and creates the required tables."""
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        # Create Invoices Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS invoices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                invoice_number TEXT UNIQUE NOT NULL,
                vendor_name TEXT NOT NULL,
                customer_name TEXT,
                invoice_date TEXT,
                due_date TEXT,
                tax_amount REAL DEFAULT 0.0,
                total_amount REAL NOT NULL,
                currency TEXT DEFAULT 'USD',
                payment_status TEXT DEFAULT 'Pending',
                validation_status TEXT DEFAULT 'Valid',
                processing_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        logger.info("Database initialized successfully with invoices table.")
    except Exception as e:
        logger.error(f"Error initializing database: {str(e)}")
    finally:
        conn.close()

def add_invoice(invoice_data):
    """Inserts a new invoice record into the database."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO invoices (
                invoice_number, vendor_name, customer_name, invoice_date, 
                due_date, tax_amount, total_amount, currency, payment_status, validation_status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            invoice_data['invoice_number'],
            invoice_data['vendor_name'],
            invoice_data['customer_name'],
            invoice_data['invoice_date'],
            invoice_data['due_date'],
            invoice_data.get('tax_amount', 0.0),
            invoice_data['total_amount'],
            invoice_data.get('currency', 'USD'),
            invoice_data.get('payment_status', 'Pending'),
            invoice_data.get('validation_status', 'Valid')
        ))
        conn.commit()
        logger.info(f"Invoice {invoice_data['invoice_number']} successfully saved to database.")
        return True
    except sqlite3.IntegrityError:
        logger.warning(f"Duplicate invoice skipped: {invoice_data['invoice_number']}")
        return "Duplicate"
    except Exception as e:
        logger.error(f"Failed to insert invoice: {str(e)}")
        return False
    finally:
        conn.close()

# If running this file directly, initialize the database
if __name__ == "__main__":
    init_db()