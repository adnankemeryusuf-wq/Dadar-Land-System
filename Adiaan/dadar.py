import streamlit as st
import pandas as pd
import os
import io
from datetime import datetime
from fpdf import FPDF

# ================= 1. CONFIG & STYLING =================
st.set_page_config(page_title="Dadar Land Admin Pro", layout="wide", page_icon="🏢")

st.markdown("""
    <style>
    .stApp { background: #f8f9fa; }
    [data-testid="stSidebar"] { background-color: #1b5e20 !important; }
    div.stForm { background: white; border-radius: 12px; padding: 20px; border: 1px solid #ddd; }
    .metric-card { background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); text-align: center; border-top: 5px solid #1b5e20; }
    </style>
    """, unsafe_allow_html=True)

# ================= 2. DATA MANAGEMENT =================
DATA_FILE = "dadar_final_report.txt"
COL_NAMES = ['Guyyaa', 'Maqaa_Abbaa_Dhimmaa', 'Araddaa', 'Qaxana', 'Gosa_Tajajjilaa', 'Maqaa_Ogeessa', 'Kafaltii_Taj']

# ... (GATII_DICT fi MONTH_MAP koodii kee isa duraa irraa fudhatama)

def load_data():
    if not os.path.exists(DATA_FILE) or os.stat(DATA_FILE).st_size == 0:
        return pd.DataFrame(columns=COL_NAMES)
    df = pd.read_csv(DATA_FILE, sep="|", names=COL_NAMES, header=None, encoding='utf-8')
    df['Kafaltii_Taj'] = pd.to_numeric(df['Kafaltii_Taj'], errors='coerce').fillna(0)
    return df

def save_data(df_to_save):
    df_to_save[COL_NAMES].to_csv(DATA_FILE, sep="|", index=False, header=False, encoding="utf-8")

# ================= 3. PDF CERTIFICATE GENERATOR =================
def create_pdf_cert(name, count, rank):
    pdf = FPDF(orientation='L', unit='mm', format='A4')
    pdf.add_page()
    
    # Rank Colors: Gold, Silver, Bronze
    colors = {1: (212, 175, 55), 2: (192, 192, 192), 3: (205, 127, 50)}
    r, g, b = colors.get(rank, (27, 94, 32))

    # Border
    pdf.set_draw_color(r, g, b); pdf.set_line_width(3); pdf.rect(10, 10, 277, 190)
    pdf.set_line_width(1); pdf.rect(13, 13, 271, 184)

    # Text
    pdf.set_y(40); pdf.set_text_color(r, g, b); pdf.set_font('Arial', 'B', 40)
    pdf.cell(0, 20, "SARTIIFIKEETA BEEKAMTII", ln=True, align='C')
    
    pdf.ln(10); pdf.set_text_color(40, 40, 40); pdf.set_font('Arial', 'B', 25)
    pdf.cell(0, 20, f"Obbo/Adde: {name.upper()}", ln=True, align='C')
    
    pdf.ln(10); pdf.set_font('Arial', '', 16)
    msg = f"Waggaa 2026 keessatti abbootii dhimmaa {count} tajaajiluun sadarkaa {rank}ffaa argataniiru."
    pdf.multi_cell(0, 10, msg, align='C')
    
    return pdf.output(dest='S').encode('latin-1')

# ================= 4. APP INTERFACE =================
if 'logged_in' not in st.session_state: st.session_state.logged_in = False

if not st.session_state.logged_in:
    # --- Login ---
    _, mid, _ = st.columns([1,1,1])
    with mid:
        st.title("🔐 Login")
        u, p = st.text_input("User"), st.text_input("Pass", type="password")
        if st.button("Seeni"):
            if u == "admin" and p == "123": st.session_state.logged_in = True; st.rerun()
else:
    df = load_data()
    menu = st.sidebar.radio("FILANNOO", ["📊 Dashboard", "📝 Galmee Haaraa", "📈 Gabaasa", "🏆 Badhaasa", "🔍 Barbaadi/Edit", "Ba'i"])

    if menu == "📊 Dashboard":
        st.title("📊 Raawwii Waliigalaa")
        c1, c2 = st.columns(2)
        c1.markdown(f"<div class='metric-card'><h3>Galii</h3><h2>{df['Kafaltii_Taj'].sum():,.2f} ETB</h2></div>", unsafe_allow_html=True)
        c2.markdown(f"<div class='metric-card'><h3>Maamiltoota</h3><h2>{len(df)}</h2></div>", unsafe_allow_html=True)
        
        # Simple Chart
        if not df.empty:
            st.bar_chart(df.groupby('Maqaa_Ogeessa')['Kafaltii_Taj'].sum())

    elif menu == "📝 Galmee Haaraa":
        # ... (Koodii galmee kee isa duraa asitti itti fufa)
        st.header("📝 Galmee Haaraa")
        with st.form("reg"):
            m = st.text_input("Maqaa")
            a = st.text_input("Araddaa")
            o = st.text_input("Ogeessa")
            k = st.number_input("Kafaltii", min_value=0.0)
            if st.form_submit_button("💾 Save"):
                new = [datetime.now().strftime('%d/%m/%Y'), m, a, "-", "Tajaajila", o, k]
                df = pd.concat([df, pd.DataFrame([new], columns=COL_NAMES)], ignore_index=True)
                save_data(df); st.success("Galmeeffameera!")

    elif menu == "🏆 Badhaasa":
        st.header("🏆 Ogeeyyii Cimoos")
        top_3 = df['Maqaa_Ogeessa'].value_counts().head(3)
        cols = st.columns(3)
        for i, (name, count) in enumerate(top_3.items()):
            with cols[i]:
                st.info(f"Sadarkaa {i+1}: {name}")
                pdf_bytes = create_pdf_cert(name, count, i+1)
                st.download_button(f"📥 PDF {name}", pdf_bytes, f"Cert_{name}.pdf")

    elif menu == "🔍 Barbaadi/Edit":
        st.header("🔍 Search & Management")
        q = st.text_input("Maqaa Barbaadi")
        if q:
            res = df[df['Maqaa_Abbaa_Dhimmaa'].str.contains(q, case=False, na=False)]
            st.write(f"Bu'aa {len(res)} argameera.")
            for i, row in res.iterrows():
                with st.expander(f"{row['Maqaa_Abbaa_Dhimmaa']} - {row['Guyyaa']}"):
                    st.write(row)
                    if st.button("Haqi", key=f"del_{i}"):
                        df = df.drop(i)
                        save_data(df); st.rerun()

    elif menu == "Ba'i": st.session_state.logged_in = False; st.rerun()
