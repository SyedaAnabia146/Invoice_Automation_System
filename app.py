import streamlit as st
import pandas as pd
import os
from datetime import datetime
from database.database import get_connection, init_db, add_invoice
from src.extractor import InvoiceExtractor
from src.validator import InvoiceValidator
from src.reporter import FinancialReporter
from src.logger import logger

# 1. PAGE CONFIGURATION & APP INITIALIZATION
st.set_page_config(page_title="InvoiceAuto", layout="wide", page_icon="💼")
init_db()

# 2. EXECUTIVE DARK THEME CUSTOM CSS (FULLY OPTIMIZED CONTRAST & CENTERED TALL UPLOADER)
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght=400;500;600;700&display=swap');
        
        .stApp {
            background-color: #1A1A1E !important;
            color: #E2E8F0 !important;
        }
        * {
            font-family: 'Inter', sans-serif;
        }
        section[data-testid="stSidebar"] {
            background-color: #111115 !important;
            border-right: 1px solid #27272A !important;
        }
        h1, h2, h3, h4, h5, h6 {
            color: #FFFFFF !important;
            font-weight: 600 !important;
        }
        p, label, span {
            color: #94A3B8 !important;
        }
        .kpi-container {
            display: flex;
            gap: 16px;
            margin-bottom: 25px;
        }
        .card-custom {
            flex: 1;
            padding: 20px;
            border-radius: 12px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.2);
        }
        .card-title-sub { font-size: 14px; font-weight: 500; margin-bottom: 8px; }
        .card-value-main { font-size: 32px; font-weight: 700; }
        
        .c-total { background-color: #EFF6FF; color: #1E40AF; }
        .c-total .card-title-sub { color: #1D4ED8; } .c-total .card-value-main { color: #1E3A8A; }
        .c-paid { background-color: #F0FDF4; color: #166534; }
        .c-paid .card-title-sub { color: #15803D; } .c-paid .card-value-main { color: #14532D; }
        .c-pending { background-color: #FEF3C7; color: #92400E; }
        .c-pending .card-title-sub { color: #B45309; } .c-pending .card-value-main { color: #78350F; }
        .c-overdue { background-color: #FEF2F2; color: #991B1B; }
        .c-overdue .card-title-sub { color: #B91C1C; } .c-overdue .card-value-main { color: #7A2021; }

        .workspace-panel {
            background-color: #222227 !important;
            border: 1px solid #2E2E35 !important;
            border-radius: 12px !important;
            padding: 24px !important;
            margin-bottom: 20px;
        }

        /* --- ALL BUTTONS STYLING OVERRIDE (Fixes Gray Text & Whiteout Hover) --- */
        div.stButton > button, div.stDownloadButton > button {
            background-color: #0D9488 !important;
            color: #FFFFFF !important;
            border: none !important;
            border-radius: 8px !important;
            padding: 10px 20px !important;
            font-weight: 600 !important;
            text-shadow: none !important;
        }
        
        div.stButton > button p, div.stDownloadButton > button p {
            color: #FFFFFF !important;
        }

        div.stButton > button:hover, div.stDownloadButton > button:hover {
            background-color: #14B8A6 !important;
            color: #FFFFFF !important;
            box-shadow: 0 0 12px rgba(13, 148, 136, 0.5) !important;
        }
        
        div.stButton > button:hover p, div.stDownloadButton > button:hover p {
            color: #FFFFFF !important;
        }

        div.stButton > button:active, div.stDownloadButton > button:active,
        div.stButton > button:focus, div.stDownloadButton > button:focus {
            background-color: #0F766E !important;
            color: #FFFFFF !important;
        }

        /* --- FILE UPLOADER TALL HEIGHT & PERFECT CENTER ALIGNMENT --- */
        div[data-testid="stFileUploader"] section {
            padding: 45px 20px !important;
            background-color: #1A1A1E !important;
            border: 2px dashed #2E2E35 !important;
            border-radius: 10px !important;
            min-height: 190px !important;
            display: flex !important;
            flex-direction: column !important;
            justify-content: center !important;
            align-items: center !important;
            text-align: center !important;
        }
        
        /* Forces internal drag-drop rows/widgets to center perfectly */
        div[data-testid="stFileUploader"] section > div {
            display: flex !important;
            flex-direction: column !important;
            align-items: center !important;
            justify-content: center !important;
            width: 100% !important;
        }

        div[data-testid="stFileUploader"] label {
            margin-bottom: 15px !important;
            font-size: 16px !important;
            text-align: center !important;
            display: block !important;
            width: 100% !important;
        }

        .stDataFrame {
            background-color: #222227 !important;
            border: 1px solid #2E2E35 !important;
            border-radius: 8px !important;
        }
    </style>
""", unsafe_allow_html=True)

# 3. SIDEBAR NAVIGATION
with st.sidebar:
    st.markdown("<h2 style='color:#FFFFFF; font-size:22px; margin-bottom:0px;'>💵 InvoiceAuto</h2>", unsafe_allow_html=True)
    st.caption("Enterprise Document Pipeline")
    st.markdown("<br>", unsafe_allow_html=True)
    
    navigation = st.radio(
        "Workspace Options",
        ["📁 Dashboard", "📝 Create Invoice", "📜 Invoice History", "👥 Clients", "📊 Reports", "⚙️ Settings"],
        label_visibility="collapsed"
    )

# Fetch current master data from database
conn = get_connection()
df_master = FinancialReporter.fetch_all_data(conn)

# ----------------------------------------------------
# SCREEN 1: THE BRAND NEW DASHBOARD WITH REAL FILTERS
# ----------------------------------------------------
if "Dashboard" in navigation:
    st.markdown("<h2 style='margin-bottom:2px;'>Dashboard</h2>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    
    # KPI Calculations
    if not df_master.empty:
        total_invoices = len(df_master)
        paid_count = df_master[df_master['payment_status'] == 'Paid'].shape[0]
        pending_count = df_master[df_master['payment_status'] == 'Pending'].shape[0]
        overdue_count = df_master[df_master['validation_status'] != 'Valid'].shape[0]
    else:
        total_invoices, paid_count, pending_count, overdue_count = 0, 0, 0, 0
        
    st.markdown(f"""
    <div class="kpi-container">
        <div class="card-custom c-total"><div class="card-title-sub">Total invoices</div><div class="card-value-main">{total_invoices}</div></div>
        <div class="card-custom c-paid"><div class="card-title-sub">Paid</div><div class="card-value-main">{paid_count}</div></div>
        <div class="card-custom c-pending"><div class="card-title-sub">Pending</div><div class="card-value-main">{pending_count}</div></div>
        <div class="card-custom c-overdue"><div class="card-title-sub">Validation Issues</div><div class="card-value-main">{overdue_count}</div></div>
    </div>
    """, unsafe_allow_html=True)
    
    # ADVANCED SEARCH & FILTERING CONTROL BLOCK (Feature 5)
    st.markdown("<div class='workspace-panel'>", unsafe_allow_html=True)
    st.markdown("<h3 style='margin-top:0px; font-size:18px;'>🔍 Filter & Search Workspace Records</h3>", unsafe_allow_html=True)
    
    f1, f2, f3 = st.columns([2, 1, 1])
    with f1:
        search_kw = st.text_input("Search by Vendor or Invoice ID", placeholder="Type keywords...")
    with f2:
        status_sel = st.selectbox("Payment Status", ["All Statuses", "Paid", "Pending"])
    with f3:
        valid_sel = st.selectbox("Validation Status", ["All Statuses", "Valid", "Invalid"])
        
    # Apply Filtering Mechanism to DataFrame dynamically
    df_filtered = df_master.copy() if not df_master.empty else pd.DataFrame()
    
    if not df_filtered.empty:
        if search_kw:
            df_filtered = df_filtered[
                df_filtered['vendor_name'].str.contains(search_kw, case=False, na=False) |
                df_filtered['invoice_number'].str.contains(search_kw, case=False, na=False)
            ]
        if status_sel != "All Statuses":
            df_filtered = df_filtered[df_filtered['payment_status'] == status_sel]
        if valid_sel != "All Statuses":
            if valid_sel == "Valid":
                df_filtered = df_filtered[df_filtered['validation_status'] == 'Valid']
            else:
                df_filtered = df_filtered[df_filtered['validation_status'] != 'Valid']
                
        # Display the targeted result table
        st.dataframe(
            df_filtered[['invoice_number', 'vendor_name', 'total_amount', 'payment_status', 'validation_status']].tail(10),
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("No documents active in database pipeline context.")
    st.markdown("</div>", unsafe_allow_html=True)

    # File Uploader Panel with Extended Centered Box
    st.markdown("<div class='workspace-panel'>", unsafe_allow_html=True)
    st.markdown("<h3>📥 Upload & Process New Invoice PDFs</h3>", unsafe_allow_html=True)
    uploaded_files = st.file_uploader("Upload Cluster", type=["pdf"], accept_multiple_files=True)
    if uploaded_files:
        for uploaded_file in uploaded_files:
            save_dir = os.path.join("data", "invoices")
            os.makedirs(save_dir, exist_ok=True)
            file_path = os.path.join(save_dir, uploaded_file.name)
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            with st.spinner(f"Running automated parser for {uploaded_file.name}..."):
                extractor = InvoiceExtractor(file_path)
                extracted_data = extractor.parse_invoice_data()
                _, validation_status = InvoiceValidator.validate(extracted_data)
                extracted_data["validation_status"] = validation_status
                add_invoice(extracted_data)
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

# ----------------------------------------------------
# SCREENS 2-6: CREATE, HISTORY, CLIENTS, REPORTS
# ----------------------------------------------------
elif "Create Invoice" in navigation:
    st.markdown("<h2>Create Invoice</h2>", unsafe_allow_html=True)
    if "line_items" not in st.session_state:
        st.session_state.line_items = [{"item": "", "qty": 1, "price": 0.0}]
        
    f_col, p_col = st.columns([1.7, 1.3], gap="large")
    with f_col:
        st.markdown("<div class='workspace-panel'>", unsafe_allow_html=True)
        inv_no = st.text_input("Invoice Identifier")
        vendor_name = st.text_input("Vendor Entity Name")
        client_name = st.text_input("Target Client/Customer")
        inv_date = st.date_input("Accounting Date", datetime.now())
        
        for i, item in enumerate(st.session_state.line_items):
            c1, c2, c3 = st.columns([3, 1, 1.5])
            with c1: st.session_state.line_items[i]["item"] = st.text_input(f"Description #{i+1}", value=item["item"], key=f"i_{i}")
            with c2: st.session_state.line_items[i]["qty"] = st.number_input(f"Qty", min_value=1, value=item["qty"], key=f"q_{i}")
            with c3: st.session_state.line_items[i]["price"] = st.number_input(f"Price ($)", min_value=0.0, value=item["price"], key=f"p_{i}")
            
        b1, b2 = st.columns(2)
        if b1.button("➕ Add Row"):
            st.session_state.line_items.append({"item": "", "qty": 1, "price": 0.0})
            st.rerun()
        if len(st.session_state.line_items) > 1 and b2.button("❌ Pop Last"):
            st.session_state.line_items.pop()
            st.rerun()
            
        subtotal = sum(item["qty"] * item["price"] for item in st.session_state.line_items)
        tax = subtotal * 0.10
        grand = subtotal + tax
        payment_opt = st.selectbox("Document Status", ["Pending", "Paid"])
        
        if st.button("🔒 Process & Post Immutably", use_container_width=True):
            if inv_no and vendor_name:
                payload = {
                    "invoice_number": inv_no, "vendor_name": vendor_name, "customer_name": client_name,
                    "invoice_date": str(inv_date), "due_date": str(inv_date), "tax_amount": tax,
                    "total_amount": grand, "currency": "USD", "payment_status": payment_opt, "validation_status": "Valid"
                }
                add_invoice(payload)
                st.success("Synchronized with Secure Storage System Layer!")
                st.session_state.line_items = [{"item": "", "qty": 1, "price": 0.0}]
            else:
                st.error("Fields cannot be empty.")
        st.markdown("</div>", unsafe_allow_html=True)

    with p_col:
        st.markdown("<div class='workspace-panel' style='background-color:#111115 !important;'>", unsafe_allow_html=True)
        st.markdown("<h4 style='color:#0D9488;'>👁️ Real-time Preview</h4>", unsafe_allow_html=True)
        st.markdown(f"**Entity Header:** {vendor_name if vendor_name else 'Vendor DRAFT Co.'}")
        st.markdown(f"**Invoice ID:** {inv_no if inv_no else 'DRAFT-XXXX'}")
        st.markdown(f"---")
        for item in st.session_state.line_items:
            if item["item"]:
                st.markdown(f"• *{item['item']}* (x{item['qty']}) — **${item['qty']*item['price']:,.2f}**")
        st.markdown("---")
        st.markdown(f"### **Total (with 10% Tax): ${grand:,.2f}**")
        st.markdown("</div>", unsafe_allow_html=True)

elif "Invoice History" in navigation:
    st.markdown("<h2>Invoice History Ledger</h2>", unsafe_allow_html=True)
    st.markdown("<div class='workspace-panel'>", unsafe_allow_html=True)
    st.dataframe(df_master, use_container_width=True, hide_index=True)
    st.markdown("</div>", unsafe_allow_html=True)

elif "Clients" in navigation:
    st.markdown("<h2>Clients Registry</h2>", unsafe_allow_html=True)
    st.markdown("<div class='workspace-panel'>", unsafe_allow_html=True)
    if not df_master.empty:
        st.dataframe(pd.DataFrame({"Client Corporates": df_master['vendor_name'].unique()}), use_container_width=True, hide_index=True)
    else:
        st.info("Directory empty.")
    st.markdown("</div>", unsafe_allow_html=True)

elif "Reports" in navigation:
    st.markdown("<h2>Analytical Export Control</h2>", unsafe_allow_html=True)
    st.markdown("<div class='workspace-panel'>", unsafe_allow_html=True)
    
    r1, r2 = st.columns(2)
    with r1:
        st.markdown("### Export CSV Master Report")
        csv_p = FinancialReporter.generate_csv_report(conn)
        if csv_p and os.path.exists(csv_p):
            with open(csv_p, "rb") as f:
                st.download_button("📥 Download Master CSV File", f, file_name="all_invoices.csv", use_container_width=True)
                
    with r2:
        st.markdown("### Export Advanced Business Excel Book")
        xl_p = FinancialReporter.generate_excel_report(conn)
        if xl_p and os.path.exists(xl_p):
            with open(xl_p, "rb") as f:
                st.download_button("📥 Download Multi-sheet Excel File", f, file_name="financial_analytics.xlsx", use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

elif "Settings" in navigation:
    st.markdown("<h2>Core Architecture Preferences</h2>", unsafe_allow_html=True)
    st.markdown("<div class='workspace-panel'>", unsafe_allow_html=True)
    st.toggle("Enforce strict verification matrices parsing", value=True)
    st.selectbox("Native Pipeline Currency Mode", ["USD ($)", "EUR (€)", "PKR (Rs.)"])
    st.markdown("</div>", unsafe_allow_html=True)

conn.close()