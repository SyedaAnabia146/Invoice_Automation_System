import os
import pandas as pd
from datetime import datetime
from src.logger import logger

class FinancialReporter:
    
    @staticmethod
    def fetch_all_data(conn):
        """Database se complete data pull karke DataFrame mein convert karta hai."""
        try:
            query = "SELECT * FROM invoices"
            df = pd.read_sql_query(query, conn)
            return df
        except Exception as e:
            logger.error(f"Error fetching data from database: {str(e)}")
            return pd.DataFrame()

    @staticmethod
    def generate_csv_report(conn, output_dir="data/reports"):
        """Consolidated Master Data Matrix dump (.CSV format)"""
        try:
            df = FinancialReporter.fetch_all_data(conn)
            if df.empty:
                logger.warning("No data found to generate CSV report.")
                return None
            
            os.makedirs(output_dir, exist_ok=True)
            filepath = os.path.join(output_dir, "master_consolidated_ledger.csv")
            df.to_csv(filepath, index=False)
            logger.info(f"Master CSV Report successfully written to {filepath}")
            return filepath
        except Exception as e:
            logger.error(f"Failed to compile CSV report: {str(e)}")
            return None

    @staticmethod
    def generate_excel_report(conn, output_dir="data/reports"):
        """
        Feature 6 Requirement: Generates a multi-sheet corporate financial workbook 
        with dynamic group summaries, monthly volumes, and vendor statistics.
        """
        try:
            df = FinancialReporter.fetch_all_data(conn)
            if df.empty:
                logger.warning("No data found to generate Excel workbook.")
                return None
            
            os.makedirs(output_dir, exist_ok=True)
            filepath = os.path.join(output_dir, "executive_financial_analytics.xlsx")
            
            # Data cleansing for aggregation
            df['total_amount'] = pd.to_numeric(df['total_amount'], errors='coerce').fillna(0.0)
            df['tax_amount'] = pd.to_numeric(df['tax_amount'], errors='coerce').fillna(0.0)
            
            # 1. Vendor Aggregation Sheet Logic
            vendor_summary = df.groupby('vendor_name').agg(
                Total_Invoices=('invoice_number', 'count'),
                Gross_Volume=('total_amount', 'sum'),
                Average_Invoice_Value=('total_amount', 'mean'),
                Total_Tax_Contributed=('tax_amount', 'sum')
            ).reset_index()
            
            # 2. Payment Status Summary Sheet Logic
            status_summary = df.groupby('payment_status').agg(
                Count=('invoice_number', 'count'),
                Total_Value=('total_amount', 'sum')
            ).reset_index()

            # Writing into multi-sheet using ExcelWriter
            with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='Master Audit Trail', index=False)
                vendor_summary.to_excel(writer, sheet_name='Vendor Analytics', index=False)
                status_summary.to_excel(writer, sheet_name='Liquidity & Status Summaries', index=False)
                
            logger.info(f"Multi-Sheet Financial Excel Analytics generated at {filepath}")
            return filepath
        except Exception as e:
            logger.error(f"Failed to generate structured Excel workbook: {str(e)}")
            return None