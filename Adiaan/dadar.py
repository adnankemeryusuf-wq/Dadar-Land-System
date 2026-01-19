import streamlit as st
import pandas as pd
import os
import io
from datetime import datetime
from fpdf import FPDF
import plotly.express as px

# ================= 1. CONFIGURATION & STYLE =================
DATA_FILE = "dadar_final_report.txt"
BACKUP_DIR = "backups"
NAGAHEE_DIR = "nagahee_scan"

# Folders uumuu
for folder in [BACKUP_DIR, NAGAHEE_DIR]:
    if not os.path.exists(folder): os.makedirs(folder)

st.set_page_config(page_title="Dadar Land Admin System", page_icon="🏢", layout="wide")

# CSS for a professional look
st.markdown("""
    <style>
    #MainMenu, footer, header {visibility: hidden;}
    .stApp { background: #f4f7f9; }
    div.stForm { background: white; border-radius: 12px; padding: 25px; border: 1px solid #ddd; }
    .card { background: white; padding: 20px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); text-align: center; border-top: 5px solid #006400; }
    </style>
""", unsafe_allow_html=True)

# ================= 2. CORE FUNCTIONS =================
COL_NAMES = ['Guyyaa', 'Maqaa_Abbaa_Dhimmaa', 'Araddaa', 'Qaxana', 'Gosa_Tajajjilaa', 'Maqaa_Ogeessa', 'Kafaltii_Taj']

def load_data():
    if not os.path.exists(DATA_FILE) or os.stat(DATA_FILE).st_size == 0:
        return pd.DataFrame(columns=COL_NAMES)
    df = pd.read_csv(DATA_FILE, sep="|", names=COL_NAMES, header=None, encoding='utf-8')
    df['Kafaltii_Taj'] = pd.to_numeric(df['Kafaltii_Taj'], errors='coerce').fillna(0)
    return df

def save_data(df_to_save):
    df_to_save[COL_NAMES].to_csv(DATA_FILE, sep="|", index=False, header=False, encoding="utf-8")
    ts = datetime.now().strftime('%Y%m%d_%H%M%S')
    df_to_save[COL_NAMES].to_csv(f"{BACKUP_DIR}/backup_{ts}.txt", sep="|", index=False, header=False)

# --- PDF GENERATOR (Clearance & Certificates) ---
def create_pdf_report(type, name, content, logo_l=None):
    pdf = FPDF(orientation='P' if type == "Clearance" else 'L', unit='mm', format='A4')
    pdf.add_page()
    
    # Professional Borders
    pdf.set_draw_color(0, 80, 0); pdf.set_line_width(1)
    pdf.rect(10, 10, 190 if type == "Clearance" else 277, 277 if type == "Clearance" else 190)

    if logo_l:
        with open("temp_logo.png", "wb") as f: f.write(logo_l.getbuffer())
        pdf.image("temp_logo.png", 90 if type == "Clearance" else 130, 15, 30)

    pdf.set_y(50)
    pdf.set_font('Arial', 'B', 16); pdf.cell(0, 10, "BULCHIINSA MAGAALAA DADAR", 0, 1, 'C')
    pdf.set_font('Arial', 'B', 14); pdf.cell(0, 10, "WAJJIRA LAFA FI MANAA", 0, 1, 'C')
    
    pdf.set_y(80 if type == "Clearance" else 70)
    pdf.set_text_color(200, 0, 0)
    pdf.set_font('Arial', 'B', 15); pdf.cell(0, 10, title := "WARAQAA RAGAA QULQULLUMMAA" if type == "Clearance" else "SARTIIFIKEETA BEEKAMTII", 0, 1, 'C')
    
    pdf.set_text_color(0, 0, 0); pdf.set_y(110 if type == "Clearance" else 90)
    pdf.set_font('Arial', 'B', 13); pdf.cell(0, 10, f"Maqaa: {name}", 0, 1, 'C')
    pdf.set_font('Arial', '', 12); pdf.multi_cell(0, 10, content, align='C')

    pdf.set_y(-50); pdf.line(30, pdf.get_y(), 80, pdf.get_y()); pdf.line(130, pdf.get_y(), 180, pdf.get_y())
    pdf.set_font('Arial', 'B', 10); pdf.cell(90, 10, "Mallattoo Ogeessaa", 0, 0, 'C'); pdf.cell(90, 10, "Mallattoo Itti Gaafatamaa", 0, 1, 'C')
    
    return pdf.output(dest='S').encode('latin-1', 'replace')

# ================= 3. LOGIN LOGIC =================
if 'logged_in' not in st.session_state: st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.markdown("<h1 style='text-align: center;'>🔐 Dadar Land Admin</h1>", unsafe_allow_html=True)
    with st.form("Login"):
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")
        if st.form_submit_button("SEENI", use_container_width=True):
            if u == "DAD" and p == "2026":
                st.session_state.logged_in, st.session_state.role = True, "admin"
                st.rerun()
            elif u == "ogeessa" and p == "1234":
                st.session_state.logged_in, st.session_state.role = True, "user"
                st.rerun()
            else: st.error("Dogoggora!")
else:
    df = load_data()
    
    # Sidebar Navigation
    with st.sidebar:
        st.title("🏢 Deder System")
        st.write(f"Role: **{st.session_state.role.upper()}**")
        menu_items = ["📊 Dashboard", "📝 Galmee Haaraa", "🏆 Badhaasa", "🔍 Barbaadi/Edit"]
        if st.session_state.role == "user": menu_items = ["📝 Galmee Haaraa", "🔍 Barbaadi/Edit"]
        menu = st.radio("FILANNOO", menu_items)
        if st.button("Log Out"):
            st.session_state.logged_in = False
            st.rerun()

    # --- 1. DASHBOARD ---
    if menu == "📊 Dashboard":
        st.header("📊 Dashboard Herregaa fi Gali")
        if not df.empty:
            df_tot = df[df['Gosa_Tajajjilaa'].str.contains('TOT', case=False, na=False)]
            c1, c2, c3 = st.columns(3)
            c1.metric("💰 Waliigala Galii", f"{df['Kafaltii_Taj'].sum():,.2f} ETB")
            c2.metric("📈 Galii TOT (2%)", f"{df_tot['Kafaltii_Taj'].sum():,.2f} ETB")
            c3.metric("👥 Maamiltoota", len(df))
            
            st.plotly_chart(px.pie(df, values='Kafaltii_Taj', names='Araddaa', hole=0.4, title="Galii Araddaadhaan"), use_container_width=True)
            
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                df.to_excel(writer, index=False)
            st.download_button("📥 Excel Download", output.getvalue(), "Gabaasa_Full.xlsx")

    # --- 2. REGISTRATION ---
    elif menu == "📝 Galmee Haaraa":
        st.header("📝 Galmee Tajaajilaa fi TOT")
        with st.form("RegForm"):
            col1, col2 = st.columns(2)
            name = col1.text_input("Maqaa Abbaa Dhimmaa")
            ara = col1.text_input("Araddaa")
            gosa = col2.selectbox("Gosa Tajaajilaa", ["Jijjiirraa Maqaa (Sale)", "Kaartaa Haaraa", "Waraqaa Qulqullummaa", "Adabbii", "TOT 2%"])
            base_fee = col2.number_input("Kaffaltii (ETB)", min_value=0.0)
            ogeessa = col1.text_input("Maqaa Ogeessaa")
            
            if st.form_submit_button("💾 GALMEESSI"):
                if name and ogeessa:
                    final_fee = base_fee * 0.02 if "TOT" in gosa else base_fee
                    new_data = [datetime.now().strftime('%d/%m/%Y'), name, ara, "-", gosa, ogeessa, final_fee]
                    df = pd.concat([df, pd.DataFrame([new_data], columns=COL_NAMES)], ignore_index=True)
                    save_data(df)
                    st.success(f"Galmeeffameera! Kaffaltii: {final_fee} ETB")

    # --- 3. BADHAASA ---
    elif menu == "🏆 Badhaasa":
        st.header("🏆 Sartifiikeeta Ogeeyyii")
        logo = st.file_uploader("Logo Upload", type=['png','jpg','jpeg'])
        if not df.empty:
            top_og = df['Maqaa_Ogeessa'].value_counts().head(3)
            cols = st.columns(3)
            for i, (og_name, count) in enumerate(top_og.items()):
                with cols[i]:
                    st.markdown(f"<div class='card'><h3>{og_name}</h3><p>Tajaajila: {count}</p></div>", unsafe_allow_html=True)
                    txt = f"Waggaa 2026 keessatti tajaajila {count} kennuun beekamtii argataniiru."
                    cert_pdf = create_pdf_report("Cert", og_name, txt, logo)
                    st.download_button(f"📥 Download Cert", cert_pdf, f"Cert_{og_name}.pdf")

    # --- 4. SEARCH / EDIT / CLEARANCE ---
    elif menu == "🔍 Barbaadi/Edit":
        st.header("🔍 Barbaadi & Clearance")
        q = st.text_input("Maqaa Barbaadi...")
        if q and not df.empty:
            res = df[df['Maqaa_Abbaa_Dhimmaa'].str.contains(q, case=False, na=False)]
            for idx, row in res.iterrows():
                with st.expander(f"📄 {row['Maqaa_Abbaa_Dhimmaa']} ({row['Gosa_Tajajjilaa']})"):
                    st.write(f"Kaffaltii: {row['Kafaltii_Taj']} ETB | Ogeessa: {row['Maqaa_Ogeessa']}")
                    
                    # Clearance PDF
                    clear_txt = f"Maamilli kun tajaajila {row['Gosa_Tajajjilaa']} xumuruun kaffaltii Birrii {row['Kafaltii_Taj']} raawwatanii jiru."
                    c_pdf = create_pdf_report("Clearance", row['Maqaa_Abbaa_Dhimmaa'], clear_txt)
                    st.download_button("📥 Download Clearance", c_pdf, f"Clearance_{idx}.pdf")
                    
                    if st.session_state.role == "admin":
                        if st.button("🗑 Haqi", key=f"del_{idx}"):
                            df = df.drop(idx); save_data(df); st.rerun()
