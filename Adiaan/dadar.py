import streamlit as st
import pandas as pd
import os, io, requests
from datetime import datetime
from fpdf import FPDF
import plotly.express as px

# --- CONFIG ---
DATA_FILE = "dadar_land_data.txt"
CLR_FILE = "clearance_history.txt"
BOT_TOKEN = "8357193631:AAHCuSnXzjZTQaglkmcS0gq-EvqnkIQLDBI"
CHAT_ID = "7329587700"
COL_NAMES = ['Guyyaa', 'Maqaa', 'Araddaa', 'Qaxana', 'Tajaajila', 'Ogeessa', 'Kafaltii']

# --- DATA FUNCTIONS ---
def load_data(f, cols):
    if not os.path.exists(f) or os.stat(f).st_size == 0: return pd.DataFrame(columns=cols)
    return pd.read_csv(f, sep="|", names=cols, header=None)

def save_data(df, f): df.to_csv(f, sep="|", index=False, header=False)

# --- PDF GENERATOR (ITEMIZED RECEIPT) ---
def create_receipt(data, items):
    pdf = FPDF(unit='mm', format=(100, 160))
    pdf.add_page()
    pdf.rect(5, 5, 90, 150)
    pdf.set_font('Arial', 'B', 12); pdf.cell(0, 10, "NAGAHEE KAFFALTII", ln=True, align='C')
    pdf.set_font('Arial', '', 8); pdf.cell(0, 5, f"Maqaa: {data['maqaa']}", ln=True)
    pdf.cell(0, 5, f"Guyyaa: {data['guyyaa']}", ln=True); pdf.ln(5)
    # Table
    pdf.set_fill_color(200); pdf.cell(55, 7, " Tajaajila", 1, 0, 'L', True); pdf.cell(25, 7, " ETB", 1, 1, 'C', True)
    for k, v in items.items():
        pdf.cell(55, 7, f" {k[:25]}", 1); pdf.cell(25, 7, f" {v:,.2f}", 1, 1, 'R')
    pdf.set_font('Arial', 'B', 9); pdf.cell(55, 8, " Total", 1); pdf.cell(25, 8, f" {data['total']:,.2f}", 1, 1, 'R')
    return pdf.output(dest='S').encode('latin-1')

# --- MAIN APP ---
st.set_page_config(page_title="Dadar Land System", layout="wide")
if 'auth' not in st.session_state: st.session_state.auth = False

if not st.session_state.auth:
    st.title("🔐 Login")
    if st.text_input("Username") == "admin" and st.text_input("Password", type="password") == "123":
        if st.button("Seeni"): st.session_state.auth = True; st.rerun()
else:
    menu = st.sidebar.radio("MENU", ["📊 Dashboard", "📝 Galmee", "📄 Clearance", "🏆 Badhaasa"])
    
    if menu == "📊 Dashboard":
        df = load_data(DATA_FILE, COL_NAMES)
        if not df.empty:
            df['Kafaltii'] = pd.to_numeric(df['Kafaltii'])
            st.metric("💰 Waliigala Galii", f"{df['Kafaltii'].sum():,.2f} ETB")
            # Top 5 Analytics
            top5 = df.groupby('Tajaajila')['Kafaltii'].sum().sort_values(ascending=False).head(5).reset_index()
            st.plotly_chart(px.bar(top5, x='Kafaltii', y='Tajaajila', orientation='h', title="Top 5 Services"))
            st.dataframe(df)

    elif menu == "📝 Galmee":
        GATII_DICT = {"Gibira": ["Gibira Manaa", "Gibira Lafa"], "Liizii": ["Liizii Waggaa", "TOT"]}
        with st.form("reg"):
            m, a, q = st.text_input("Maqaa"), st.text_input("Araddaa"), st.text_input("Qaxana")
            sel = st.multiselect("Gosa Tajaajilaa", list(GATII_DICT.keys()))
            items = {}
            if sel:
                for g in sel:
                    subs = st.multiselect(f"Tajaajila {g}", GATII_DICT[g])
                    for s in subs: items[s] = st.number_input(f"Kafaltii {s}", min_value=0.0)
            if st.form_submit_button("💾 Galmeessi"):
                total = sum(items.values())
                new = [datetime.now().strftime('%d/%m/%Y'), m, a, q, ", ".join(items.keys()), "Admin", total]
                df = load_data(DATA_FILE, COL_NAMES)
                save_data(pd.concat([df, pd.DataFrame([new], columns=COL_NAMES)]), DATA_FILE)
                pdf = create_receipt({"maqaa": m, "guyyaa": new[0], "total": total, "ogeessa": "Admin"}, items)
                st.download_button("📥 Nagahee Buufadhu", pdf, f"Nagahee_{m}.pdf")

    # (Clearance fi Badhaasa kutaalee duraan uumne itti dabaluu dandeessa)

    if st.sidebar.button("🚀 Gabaasa Telegram"):
        df = load_data(DATA_FILE, COL_NAMES)
        out = io.BytesIO()
        with pd.ExcelWriter(out) as wr: df.to_excel(wr, index=False)
        requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendDocument", data={'chat_id': CHAT_ID}, files={'document': out.getvalue()})
        st.sidebar.success("Ergameera!")
