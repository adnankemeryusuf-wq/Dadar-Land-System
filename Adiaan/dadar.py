import streamlit as st
import pandas as pd
import os
import io
from datetime import datetime
from fpdf import FPDF
import plotly.express as px

# ================= 1. CONFIGURATION & DIRECTORIES =================
DATA_FILE = "dadar_final_report.txt"
BACKUP_DIR = "backups"
NAGAHEE_DIR = "nagahee_scan"

for folder in [BACKUP_DIR, NAGAHEE_DIR]:
    if not os.path.exists(folder): os.makedirs(folder)

st.set_page_config(page_title="Dadar Land Admin", page_icon="🏢", layout="wide")

# CSS Style
st.markdown("""
    <style>
    #MainMenu, footer, header {visibility: hidden;}
    .stApp { background: #f4f7f9; }
    div.stForm { background: white; border-radius: 12px; padding: 20px; border: 1px solid #ddd; }
    .card { background: white; padding: 15px; border-radius: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); text-align: center; border-top: 4px solid #006400; }
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
    # Main Save
    df_to_save[COL_NAMES].to_csv(DATA_FILE, sep="|", index=False, header=False, encoding="utf-8")
    # Automatic Backup
    ts = datetime.now().strftime('%Y%m%d_%H%M%S')
    df_to_save[COL_NAMES].to_csv(f"{BACKUP_DIR}/backup_{ts}.txt", sep="|", index=False, header=False)

# --- PDF GENERATOR (Sartifiikeeta & Clearance) ---
def create_pdf(title, content, name, logo_l=None, logo_r=None, is_cert=True):
    pdf = FPDF(orientation='L' if is_cert else 'P', unit='mm', format='A4')
    pdf.add_page()
    
    # Border
    pdf.set_draw_color(0, 100, 0); pdf.set_line_width(1.5)
    pdf.rect(5, 5, 287 if is_cert else 200, 200 if is_cert else 287)

    # Logos
    if logo_l:
        with open("l_temp.png", "wb") as f: f.write(logo_l.getbuffer())
        pdf.image("l_temp.png", 10, 10, 25)
    if logo_r:
        with open("r_temp.png", "wb") as f: f.write(logo_r.getbuffer())
        pdf.image("r_temp.png", 260 if is_cert else 170, 10, 25)

    pdf.set_y(40)
    pdf.set_font('Arial', 'B', 24); pdf.cell(0, 15, title, 0, 1, 'C')
    pdf.set_font('Arial', '', 18); pdf.cell(0, 15, f"Maqaa: {name}", 0, 1, 'C')
    pdf.set_font('Arial', '', 14); pdf.multi_cell(0, 10, content, align='C')
    
    pdf.set_y(-40 if is_cert else -60)
    pdf.line(20, pdf.get_y(), 80, pdf.get_y())
    pdf.cell(60, 10, "Mallattoo Itti Gaafatamaa", 0, 0, 'C')
    
    return pdf.output(dest='S').encode('latin-1', 'replace')

# ================= 3. NAVIGATION & LOGIN =================
if 'logged_in' not in st.session_state: st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("🔐 Dadar Land Administration Login")
    u = st.text_input("Username")
    p = st.text_input("Password", type="password")
    if st.button("Seeni"):
        if u == "DAD" and p == "2026":
            st.session_state.logged_in = True
            st.session_state.role = "admin"
            st.rerun()
        elif u == "ogeessa" and p == "1234":
            st.session_state.logged_in = True
            st.session_state.role = "user"
            st.rerun()
else:
    df = load_data()
    menu_list = ["📊 Dashboard", "📝 Galmee Haaraa", "🏆 Badhaasa", "📈 Gabaasa", "🔍 Barbaadi/Edit"]
    if st.session_state.role == "user": menu_list = ["📝 Galmee Haaraa", "🔍 Barbaadi/Edit"]
    
    menu = st.sidebar.radio("FILANNOO", menu_list)
    if st.sidebar.button("Ba'i (Logout)"):
        st.session_state.logged_in = False
        st.rerun()

    # --- 1. DASHBOARD ---
    if menu == "📊 Dashboard":
        st.header("📊 Dashboard Gabaasaa")
        df_tot = df[df['Gosa_Tajajjilaa'].str.contains('TOT', case=False, na=False)]
        c1, c2, c3 = st.columns(3)
        c1.metric("Waliigala Galii", f"{df['Kafaltii_Taj'].sum():,.2f} ETB")
        c2.metric("Galii TOT", f"{df_tot['Kafaltii_Taj'].sum():,.2f} ETB")
        c3.metric("Maamiltoota", len(df))
        
        st.plotly_chart(px.bar(df, x='Araddaa', y='Kafaltii_Taj', color='Maqaa_Ogeessa'), use_container_width=True)
        
        # Excel Download
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False)
        st.download_button("📥 Gabaasa Excel Buufadhu", output.getvalue(), "Gabaasa_Dadar.xlsx")

    # --- 2. REGISTRATION (With TOT & Clearance) ---
    elif menu == "📝 Galmee Haaraa":
        st.header("📝 Galmee Tajaajilaa")
        with st.form("reg_form"):
            col1, col2 = st.columns(2)
            name = col1.text_input("Maqaa Abbaa Dhimmaa")
            ara = col1.text_input("Araddaa")
            gosa = col2.selectbox("Gosa Tajaajilaa", ["Jijjiirraa Maqaa", "Waraqaa Qulqullummaa", "Kaartaa Haaraa", "TOT Gurgurtaa"])
            gatii = col2.number_input("Gatii/Kaffaltii (ETB)", min_value=0.0)
            ogeessa = col1.text_input("Ogeessa Raawwate")
            
            # TOT Calculation if Sales
            final_fee = gatii
            if "TOT" in gosa or "Gurgurtaa" in gosa:
                final_fee = gatii * 0.02
                st.info(f"TOT (2%) herregameera: {final_fee} ETB")

            if st.form_submit_button("💾 Galmeessi"):
                new_row = [datetime.now().strftime('%d/%m/%Y'), name, ara, "-", gosa, ogeessa, final_fee]
                df = pd.concat([df, pd.DataFrame([new_row], columns=COL_NAMES)], ignore_index=True)
                save_data(df)
                st.success("Milkaa'inaan Galmeeffameera!")

    # --- 3. BADHAASA (Certificates) ---
    elif menu == "🏆 Badhaasa":
        st.header("🏆 Sartiifiikeeta Ogeeyyii")
        l_l = st.file_uploader("Logo Bitaa", type=['png','jpg'])
        l_r = st.file_uploader("Logo Mirgaa", type=['png','jpg'])
        
        if not df.empty:
            top_3 = df['Maqaa_Ogeessa'].value_counts().head(3)
            cols = st.columns(3)
            for i, (name, count) in enumerate(top_3.items()):
                with cols[i]:
                    st.markdown(f"<div class='card'><h3>{name}</h3><p>Tajaajila: {count}</p></div>", unsafe_allow_html=True)
                    cert_pdf = create_pdf("SARTIIFIKEETA BEEKAMTII", f"Waggaa 2026 keessatti tajaajila {count} kennuun sadarkaa {i+1}ffaa qabatteera.", name, l_l, l_r, True)
                    st.download_button(f"📥 Download PDF", cert_pdf, f"Cert_{name}.pdf")

    # --- 4. SEARCH / EDIT / CLEARANCE ---
    elif menu == "🔍 Barbaadi/Edit":
        st.header("🔍 Barbaadi fi Waraqaa Ragaa")
        q = st.text_input("Maqaa Maamilaa...")
        if q and not df.empty:
            res = df[df['Maqaa_Abbaa_Dhimmaa'].str.contains(q, case=False, na=False)]
            for idx, row in res.iterrows():
                with st.expander(f"📄 {row['Maqaa_Abbaa_Dhimmaa']} - {row['Gosa_Tajajjilaa']}"):
                    st.write(f"Araddaa: {row['Araddaa']} | Kaffaltii: {row['Kafaltii_Taj']} ETB")
                    
                    # Clearance Generator
                    if st.button(f"Generate Clearance for {row['Maqaa_Abbaa_Dhimmaa']}", key=idx):
                        clear_pdf = create_pdf("WARAQAA QULQULLUMMAA (CLEARANCE)", f"Maamilli kun tajaajila {row['Gosa_Tajajjilaa']} xumuruun kaffaltii {row['Kafaltii_Taj']} ETB raawwatanii jiru.", row['Maqaa_Abbaa_Dhimmaa'], None, None, False)
                        st.download_button("📥 Buufadhu (Download)", clear_pdf, f"Clearance_{row['Maqaa_Abbaa_Dhimmaa']}.pdf")
                    
                    if st.session_state.role == "admin":
                        if st.button("🗑 Haqi", key=f"del_{idx}"):
                            df = df.drop(idx); save_data(df); st.rerun()
