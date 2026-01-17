import streamlit as st
import pandas as pd
import os
import io
import base64
from datetime import datetime
from fpdf import FPDF

# ================= 1. CONFIGURATION =================
LOGO_PATH = "Adiaan/logo.png" 
DATA_FILE = "dadar_final_report.txt"
NAGAHEE_DIR = "nagahee_scan"

if not os.path.exists(NAGAHEE_DIR):
    os.makedirs(NAGAHEE_DIR)

st.set_page_config(page_title="Dadar Land Admin", page_icon="🏢", layout="wide")

# Logo gara Base64 jijjiiruuf (Streamlit irratti bifa kanaan mul'isuun gaariidha)
def get_base64_img(path):
    if os.path.exists(path):
        with open(path, "rb") as f:
            data = f.read()
        return base64.b64encode(data).decode()
    return ""

img_base64 = get_base64_img(LOGO_PATH)

# CSS - Header bareeduuf
st.markdown(f"""
    <style>
    .header-container {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        background-color: #ffffff;
        padding: 15px;
        border-radius: 10px;
        border-bottom: 4px solid #2e7d32;
        margin-bottom: 20px;
    }}
    .logo-img {{ width: 90px; height: 90px; object-fit: contain; }}
    .main-title {{ text-align: center; color: #1b5e20; flex-grow: 1; font-family: 'Arial'; }}
    </style>
    """, unsafe_allow_html=True)

# ================= 2. PDF FUNCTION =================
def create_certificate(name, service_or_count, date_str, cert_type="CUSTOMER", rank=None):
    pdf = FPDF(orientation='L', unit='mm', format='A4')
    pdf.add_page()
    b_color = (255, 215, 0) if rank == 1 else (27, 94, 32)
    pdf.set_draw_color(*b_color)
    pdf.set_line_width(2)
    pdf.rect(5, 5, 287, 200)
    pdf.rect(8, 8, 281, 194)
    
    if os.path.exists(LOGO_PATH):
        pdf.image(LOGO_PATH, 12, 12, 30) # Logo bitaa
        pdf.image(LOGO_PATH, 255, 12, 30) # Logo mirga
        
    pdf.set_y(50)
    pdf.set_font('Arial', 'B', 32)
    pdf.set_text_color(*b_color)
    title = "SARTIIFIKETA BEEKAMTII" if cert_type == "STAFF" else "WARAQAA RAGAA TAJAAJILAA"
    pdf.cell(0, 15, title, ln=True, align='C')
    
    pdf.set_font('Arial', '', 20)
    pdf.set_text_color(0, 0, 0)
    pdf.ln(25)
    
    if cert_type == "STAFF":
        msg = f"Obbo/Adde {str(name).upper()}\n\nTajaajilamtoota {service_or_count} saffisaan tajaajiluun sadarkaa {rank}ffaa\nwaggaa 2026 waan qabataniif beekamtiin kun kennameef."
    else:
        msg = f"Obbo/Adde {str(name).upper()}\n\nWaajjira Lafaa Bulchiinsa Magaalaa Dadar irraa tajaajila\n'{service_or_count}'\nguyyaa {date_str} argachuu keessaniif ragaa kenname."
    
    pdf.multi_cell(0, 12, msg, align='C')
    pdf.set_y(165)
    pdf.line(110, 175, 187, 175)
    pdf.set_xy(110, 177); pdf.set_font('Arial', 'I', 12)
    pdf.cell(77, 8, "Itti Gaafatamaa Waajjiraa", align='C')
    return pdf.output(dest='S').encode('latin-1')

# ================= 3. DATA LOAD =================
COL_NAMES = ['Guyyaa', 'Maqaa_Abbaa_Dhimmaa', 'Araddaa', 'Qaxana', 'Gosa_Tajajjilaa', 'Maqaa_Ogeessa', 'Kafaltii_Taj']

def load_data():
    if not os.path.exists(DATA_FILE) or os.stat(DATA_FILE).st_size == 0:
        return pd.DataFrame(columns=COL_NAMES)
    return pd.read_csv(DATA_FILE, sep="|", names=COL_NAMES, header=None, encoding='utf-8')

# ================= 4. MAIN APP =================
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.markdown("<h2 style='text-align:center;'>Seenaa Ka'i</h2>", unsafe_allow_html=True)
    with st.form("login"):
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")
        if st.form_submit_button("Seeni"):
            if u == "DAD" and p == "2026":
                st.session_state.logged_in = True
                st.rerun()
            else: st.error("Maqaa ykn Password dogoggora!")
else:
    # --- HEADER WITH ACTUAL LOGOS ---
    logo_src = f"data:image/png;base64,{img_base64}" if img_base64 else ""
    st.markdown(f"""
        <div class="header-container">
            <img src="{logo_src}" class="logo-img"> 
            <div class="main-title">
                <h1 style='margin:0;'>BULCHIINSA MAGAALAA DADAR</h1>
                <h3 style='margin:0; color: #4caf50;'>WAAJJIRA LAFAA</h3>
            </div>
            <img src="{logo_src}" class="logo-img">
        </div>
        """, unsafe_allow_html=True)
    
    df = load_data()
    menu = st.sidebar.radio("FILANNOO", ["📊 Dashboard", "📝 Galmee", "🏆 Badhaasa", "🔍 Barbaadi"])

    if menu == "📊 Dashboard":
        st.subheader("Dashboard")
        col1, col2 = st.columns(2)
        col1.metric("Galii Waliigalaa", f"{df['Kafaltii_Taj'].sum():,.2f} ETB")
        col2.metric("Baay'ina Maamiltootaa", len(df))
        st.dataframe(df, use_container_width=True)

    elif menu == "📝 Galmee":
        with st.form("reg", clear_on_submit=True):
            col1, col2 = st.columns(2)
            m = col1.text_input("Maqaa Maamilaa")
            o = col2.text_input("Maqaa Ogeessaa")
            t = col1.text_input("Gosa Tajaajilaa")
            k = col2.number_input("Kafaltii", min_value=0.0)
            if st.form_submit_button("Galmeessi"):
                if m and o:
                    new = [datetime.now().strftime('%d/%m/%Y'), m, "-", "-", t, o, k]
                    new_df = pd.DataFrame([new], columns=COL_NAMES)
                    df = pd.concat([df, new_df], ignore_index=True)
                    df[COL_NAMES].to_csv(DATA_FILE, sep="|", index=False, header=False, encoding="utf-8")
                    st.success("Galmee Haaraa Galmeeffameera!")
                    st.rerun()

    elif menu == "🏆 Badhaasa":
        st.subheader("🏆 Sadarkaa Ogeeyyii")
        if not df.empty:
            top_3 = df['Maqaa_Ogeessa'].value_counts().head(3)
            cols = st.columns(3)
            for i, (name, count) in enumerate(top_3.items()):
                with cols[i]:
                    st.success(f"Sadarkaa {i+1}ffaa")
                    st.write(f"**{name}**")
                    st.write(f"Hojii: {count}")
                    pdf_bytes = create_certificate(name, count, "", "STAFF", i+1)
                    st.download_button(f"📥 Buusi ({i+1})", pdf_bytes, f"Badhaasa_{name}.pdf", key=f"staff_{i}")

    elif menu == "🔍 Barbaadi":
        q = st.text_input("Maqaa Barbaadi")
        if q and not df.empty:
            res = df[df['Maqaa_Abbaa_Dhimmaa'].str.contains(q, case=False, na=False)]
            for idx, row in res.iterrows():
                with st.expander(f"📄 {row['Maqaa_Abbaa_Dhimmaa']}"):
                    st.write(f"Guyyaa: {row['Guyyaa']} | Tajaajila: {row['Gosa_Tajajjilaa']}")
                    pdf_m = create_certificate(row['Maqaa_Abbaa_Dhimmaa'], row['Gosa_Tajajjilaa'], row['Guyyaa'], "CUSTOMER")
                    st.download_button("📥 Sartifiikeetii Buusi", pdf_m, f"Ragaa_{idx}.pdf", key=f"d_{idx}")
import streamlit as st
import pandas as pd
import os
import io
import base64
from datetime import datetime
from fpdf import FPDF

# ================= 1. CONFIGURATION =================
LOGO_PATH = "Adiaan/logo.png" 
DATA_FILE = "dadar_final_report.txt"
NAGAHEE_DIR = "nagahee_scan"

if not os.path.exists(NAGAHEE_DIR):
    os.makedirs(NAGAHEE_DIR)

st.set_page_config(page_title="Dadar Land Admin", page_icon="🏢", layout="wide")

def get_base64_img(path):
    if os.path.exists(path):
        with open(path, "rb") as f:
            data = f.read()
        return base64.b64encode(data).decode()
    return ""

img_base64 = get_base64_img(LOGO_PATH)

# CSS - Logo bitaa qofaaf
st.markdown(f"""
    <style>
    .header-container {{
        display: flex;
        align-items: center; /* Sarara tokko irra kaa'uuf */
        background-color: #ffffff;
        padding: 15px;
        border-radius: 10px;
        border-bottom: 4px solid #2e7d32;
        margin-bottom: 20px;
    }}
    .logo-img {{ 
        width: 100px; 
        height: 100px; 
        object-fit: contain; 
        margin-right: 20px; /* Barruu irraa fageessuuf */
    }}
    .main-title {{ 
        color: #1b5e20; 
        font-family: 'Arial'; 
    }}
    </style>
    """, unsafe_allow_html=True)

# ================= 2. PDF FUNCTION (Logo Bitaa Qofa) =================
def create_certificate(name, service_or_count, date_str, cert_type="CUSTOMER", rank=None):
    pdf = FPDF(orientation='L', unit='mm', format='A4')
    pdf.add_page()
    b_color = (255, 215, 0) if rank == 1 else (27, 94, 32)
    pdf.set_draw_color(*b_color)
    pdf.set_line_width(2)
    pdf.rect(5, 5, 287, 200)
    pdf.rect(8, 8, 281, 194)
    
    if os.path.exists(LOGO_PATH):
        pdf.image(LOGO_PATH, 12, 12, 30) # Logo bitaa qofa PDF irratti
        
    pdf.set_y(50)
    pdf.set_font('Arial', 'B', 32)
    pdf.set_text_color(*b_color)
    title = "SARTIIFIKETA BEEKAMTII" if cert_type == "STAFF" else "WARAQAA RAGAA TAJAAJILAA"
    pdf.cell(0, 15, title, ln=True, align='C')
    
    pdf.set_font('Arial', '', 20)
    pdf.set_text_color(0, 0, 0)
    pdf.ln(25)
    
    msg = f"Obbo/Adde {str(name).upper()}\n\n"
    if cert_type == "STAFF":
        msg += f"Tajaajilamtoota {service_or_count} saffisaan tajaajiluun sadarkaa {rank}ffaa\nwaggaa 2026 waan qabataniif beekamtiin kun kennameef."
    else:
        msg += f"Waajjira Lafaa Bulchiinsa Magaalaa Dadar irraa tajaajila\n'{service_or_count}'\nguyyaa {date_str} argachuu keessaniif ragaa kenname."
    
    pdf.multi_cell(0, 12, msg, align='C')
    pdf.set_y(165)
    pdf.line(110, 175, 187, 175)
    pdf.set_xy(110, 177); pdf.set_font('Arial', 'I', 12)
    pdf.cell(77, 8, "Itti Gaafatamaa Waajjiraa", align='C')
    return pdf.output(dest='S').encode('latin-1')

# ================= 3. DATA LOAD =================
COL_NAMES = ['Guyyaa', 'Maqaa_Abbaa_Dhimmaa', 'Araddaa', 'Qaxana', 'Gosa_Tajajjilaa', 'Maqaa_Ogeessa', 'Kafaltii_Taj']

def load_data():
    if not os.path.exists(DATA_FILE) or os.stat(DATA_FILE).st_size == 0:
        return pd.DataFrame(columns=COL_NAMES)
    return pd.read_csv(DATA_FILE, sep="|", names=COL_NAMES, header=None, encoding='utf-8')

# ================= 4. MAIN APP =================
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.markdown("<h2 style='text-align:center;'>Seenaa Ka'i</h2>", unsafe_allow_html=True)
    with st.form("login"):
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")
        if st.form_submit_button("Seeni"):
            if u == "DAD" and p == "2026":
                st.session_state.logged_in = True
                st.rerun()
            else: st.error("Maqaa ykn Password dogoggora!")
else:
    # --- HEADER WITH ONE LOGO (LEFT SIDE) ---
    logo_src = f"data:image/png;base64,{img_base64}" if img_base64 else ""
    st.markdown(f"""
        <div class="header-container">
            <img src="{logo_src}" class="logo-img"> 
            <div class="main-title">
                <h1 style='margin:0;'>BULCHIINSA MAGAALAA DADAR</h1>
                <h3 style='margin:0; color: #4caf50;'>WAAJJIRA LAFAA</h3>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    df = load_data()
    menu = st.sidebar.radio("FILANNOO", ["📊 Dashboard", "📝 Galmee", "🏆 Badhaasa", "🔍 Barbaadi"])

    # --- DASHBOARD ---
    if menu == "📊 Dashboard":
        st.subheader("Dashboard")
        c1, c2 = st.columns(2)
        c1.metric("Galii Waliigalaa", f"{df['Kafaltii_Taj'].sum():,.2f} ETB")
        c2.metric("Maamiltoota", len(df))
        st.dataframe(df, use_container_width=True)

    # --- GALMEE ---
    elif menu == "📝 Galmee":
        with st.form("reg", clear_on_submit=True):
            m = st.text_input("Maqaa Maamilaa")
            o = st.text_input("Maqaa Ogeessaa")
            t = st.text_input("Gosa Tajaajilaa")
            k = st.number_input("Kafaltii", min_value=0.0)
            if st.form_submit_button("Galmeessi"):
                if m and o:
                    new = [datetime.now().strftime('%d/%m/%Y'), m, "-", "-", t, o, k]
                    df = pd.concat([df, pd.DataFrame([new], columns=COL_NAMES)], ignore_index=True)
                    df[COL_NAMES].to_csv(DATA_FILE, sep="|", index=False, header=False, encoding="utf-8")
                    st.success("Galmeeffameera!")
                    st.rerun()

    # --- BADHAASA ---
    elif menu == "🏆 Badhaasa":
        st.subheader("🏆 Sadarkaa Ogeeyyii")
        if not df.empty:
            top_3 = df['Maqaa_Ogeessa'].value_counts().head(3)
            for i, (name, count) in enumerate(top_3.items()):
                st.write(f"**{i+1}. {name}** (Hojii: {count})")
                pdf_bytes = create_certificate(name, count, "", "STAFF", i+1)
                st.download_button(f"📥 Sartifiikeetii {name}", pdf_bytes, f"Badhaasa_{name}.pdf", key=f"st_{i}")

    # --- BARBAADI ---
    elif menu == "🔍 Barbaadi":
        q = st.text_input("Maqaa Barbaadi")
        if q and not df.empty:
            res = df[df['Maqaa_Abbaa_Dhimmaa'].str.contains(q, case=False, na=False)]
            for idx, row in res.iterrows():
                with st.expander(f"📄 {row['Maqaa_Abbaa_Dhimmaa']}"):
                    pdf_m = create_certificate(row['Maqaa_Abbaa_Dhimmaa'], row['Gosa_Tajajjilaa'], row['Guyyaa'], "CUSTOMER")
                    st.download_button("📥 PDF Buusi", pdf_m, f"Ragaa_{idx}.pdf", key=f"d_{idx}")
