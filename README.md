# InvoiceAuto: Enterprise Invoice Processing & Data Pipeline

An automated, end-to-end Invoice Processing System built with **Python**, **Streamlit**, and **SQLite**. This system parses raw invoice records via localized OCR logic, performs deep corporate format validations, maintains transactional state persistence dynamically, and generates multi-sheet financial accounting summaries automatically.

---

## 🚀 Key Architectural Features

* **Document Parsing Engine:** Real-time data processing layer built to isolate metadata, entity metrics, and line-item summaries from invoice uploads.
* **Deep Validation Network:** Built-in validation structures checking for anomalies such as missing parameters (`total_amount`, `vendor_name`), zero/negative balances, and heterogeneous date formats.
* **Dynamic Client Workspace:** Premium executive dark-themed interface supporting text keyword search, conditional drop-down matrices, and automated layout scaling.
* **Multi-Sheet Reporting Engine:** Implements advanced ledger tracking exported natively to professional multi-tab Excel workbooks (`Master Audit Trail`, `Vendor Analytics`, `Liquidity Summaries`) and consolidated CSV spreadsheets.
* **Resilient Database Control:** Full schema persistence maintaining transactional updates, record serialization, and verification state logs cleanly.

---

## 📁 System Architecture & Directory Layout

```text
Invoice_Automation_System/
│
├── app.py                  # Main Executive Streamlit Client Dashboard
├── database/
│   └── database.py         # Relational Storage Control & SQLite Init
├── src/
│   ├── extractor.py        # Core PDF Metadata Data Parsing Logic
│   ├── validator.py        # Validation Engine & Content Verification Rules
│   ├── reporter.py         # Multi-Tab Corporate Reporting Exports
│   └── logger.py           # Structured Verification Log Streamer
├── data/
│   ├── invoices/           # Local Document Cluster Staging
│   └── reports/            # Generated Enterprise Financial Reports
├── .gitignore              # Production Exclusions File
└── README.md               # Architecture Documentation File

(Clone the Workspace Repository)
git clone [https://github.com/SyedaAnabia146/Invoice_Automation_System.git](https://github.com/SyedaAnabia146/Invoice_Automation_System.git)
cd Invoice_Automation_System 

(Install Required Enterprise Libraries)
pip install streamlit pandas openpyxl reportlab

(Launch the Application Client)
python -m streamlit run app.py

