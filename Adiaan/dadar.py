import streamlit as st
import pandas as pd
import os
import io
import requests
from datetime import datetime
from fpdf import FPDF
import plotly.express as px

# ================= 1. CONFIGURATION & STYLE =================
LOGO_PATH = "Adiaan/logo.png"
NAGAHEE_DIR = "nagahee_scan"
DATA_FILE = "dadar_final_report.txt"

if not os.path.exists(NAGAHEE_DIR):
    os.makedirs(NAGAHEE_DIR)

st.set_page_config(
    page_title="Dadar Land Admin Pro", 
    page_icon="🏢", 
    layout="wide"
)

# Halluu fi Style
st.markdown("""
    <style>
    .stApp { background: #f4f7f6; }
    div.stForm { background: white; border-radius: 12px; padding: 20px; border: 1px solid #ddd; }
    .card { background: white; padding: 15px; border-radius: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); text-align: center; }
    </style>
    """, unsafe_allow_html=True)

# ================= 2. SERVICE LIST (GOSA TAJAAJILAA) =================
# Gosa tajaajilaa hunda akka gosa gurguddaatti addaan baasuu
SERVICE_STRUCTURE = {
    "🏷️ Gibira & Kaffaltii": [
        "Gibira Baaxii Gooroo", "Gibira Lafa Qonnaa", "Kaffaltii Liizii Waggaa", 
        "Kaffaltii Liizii Duraa", "Gibira Milkii (Stamp Duty)", "TOT (Turnover Tax)"
    ],
    "📜 Kaartaa & Qabiyyee": [
        "Kaartaa Haaraa", "Kaartaa Bakka Bu'aa", "Kaartaa Kadastaaraa", 
        "Jijjiirraa Maqaa (Gift/Sale)", "Sirreeffama Daangaa", "Ganda Irraa gara Magaalaatti"
    ],
    "🏗️ Pilaanii & Ijaarsa": [
        "Hayyama Ijaarsaa", "Pilaanii Magaalaa", "Itti Fayyadama Lafaa (Land Use)", 
        "Mirkaneessa Sertifikeeta Ijaarsaa", "Humna Mahandisummaa"
    ],
    "⚖️ Dhimma Seeraa": [
        "Ugura Mana Murtii", "Ugura Kaasuu", "Waliigaltee Liqii Baankii", 
        "Waliigaltee Hiikuu", "Dhimma Dhala (Inheritance)"
    ],
    "📂 Tajaajila Biroo": [
        "Waraqaa Ragaa (Clearance)", "Deebii Iyyannoo", "Tajaajila Koppii (Photocopy)"
    ]
}


# Halluu fi Style
st.markdown("""
    <style>
    .stApp { background: #f4f7f6; }
    div.stForm { background: white; border-radius: 12px; padding: 20px; border: 1px solid #ddd; }
    .card { background: white; padding: 15px; border-radius: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); text-align: center; }
    </style>
    """, unsafe_allow_html=True)

# ================= 2. SERVICE LIST (GOSA TAJAAJILAA) =================
# Gosa tajaajilaa hunda akka gosa gurguddaatti addaan baasuu
SERVICE_STRUCTURE = {
    "🏷️ Gibira & Kaffaltii": [
        "Gibira Baaxii Gooroo", "Gibira Lafa Qonnaa", "Kaffaltii Liizii Waggaa", 
        "Kaffaltii Liizii Duraa", "Gibira Milkii (Stamp Duty)", "TOT (Turnover Tax)"
    ],
    "📜 Kaartaa & Qabiyyee": [
        "Kaartaa Haaraa", "Kaartaa Bakka Bu'aa", "Kaartaa Kadastaaraa", 
        "Jijjiirraa Maqaa (Gift/Sale)", "Sirreeffama Daangaa", "Ganda Irraa gara Magaalaatti"
    ],
    "🏗️ Pilaanii & Ijaarsa": [
        "Hayyama Ijaarsaa", "Pilaanii Magaalaa", "Itti Fayyadama Lafaa (Land Use)", 
        "Mirkaneessa Sertifikeeta Ijaarsaa", "Humna Mahandisummaa"
    ],
    "⚖️ Dhimma Seeraa": [
        "Ugura Mana Murtii", "Ugura Kaasuu", "Waliigaltee Liqii Baankii", 
        "Waliigaltee Hiikuu", "Dhimma Dhala (Inheritance)"
    ],
    "📂 Tajaajila Biroo": [
        "Waraqaa Ragaa (Clearance)", "Deebii Iyyannoo", "Tajaajila Koppii (Photocopy)"
    ]
}

COL_NAMES = ['Guyyaa', 'Maqaa_Abbaa_Dhimmaa', 'Araddaa', 'Qaxana', 'Gosa_Tajajjilaa', 'Maqaa_Ogeessa', 'Kafaltii_Taj']

# ================= 3. CORE FUNCTIONS =================
def load_data():
    if not os.path.exists(DATA_FILE) or os.stat(DATA_FILE).st_size == 0:
        return pd.DataFrame(columns=COL_NAMES)
    return pd.read_csv(DATA_FILE, sep="|", names=COL_NAMES, header=None, encoding='utf-8')

def save_data(df_to_save):
    df_to_save[COL_NAMES].to_csv(DATA_FILE, sep="|", index=False, header=False, encoding="utf-8")

def create_certificate(name, count, rank, l_l, l_r, sig):
    pdf = FPDF(orientation='L', unit='mm', format='A4')
    pdf.add_page()
    
    # Border
    pdf.set_draw_color(0, 100, 0); pdf.set_line_width(2); pdf.rect(10, 10, 277, 190)
    
    # Logo
    if l_l: 
        with open("tmp_l.png", "wb") as f: f.write(l_l.getbuffer())
        pdf.image("tmp_l.png", 20, 15, 30)
    
    pdf.set_y(50); pdf.set_font('Arial', 'B', 30); pdf.cell(0, 10, "SARTIIFIKEETA BEEKAMTII", 0, 1, 'C')
    pdf.set_font('Arial', '', 20); pdf.cell(0, 20, f"Obbo/Adde: {name}", 0, 1, 'C')
    pdf.set_font('Arial', '', 14); pdf.multi_cell(0, 10, f"Waggaa 2026 keessatti maamiltoota {count} tajaajiluun sadarkaa {rank}ffaa argataniiru.", align='C')
    
    # Signature
    if sig:
        with open("tmp_sig.png", "wb") as f: f.write(sig.getbuffer())
        pdf.image("tmp_sig.png", 50, 160, 30)
    
    pdf.line(40, 180, 100, 180); pdf.set_xy(40, 182); pdf.cell(60, 10, "Itti Gaafatamaa", align='C')
    return pdf.output(dest='S').encode('latin-1', 'replace')

# ================= 4. MAIN NAVIGATION =================
if 'logged_in' not in st.session_state: st.session_state.logged_in = False

if not st.session_state.logged_in:
    # Login Section
    st.title("🔐 Dadar Land Admin Login")
    u = st.text_input("Username")
    p = st.text_input("Password", type="password")
    if st.button("Seeni"):
        if u == "DAD" and p == "2026": 
            st.session_state.logged_in = True
            st.rerun()
# ================= 4. NAVIGATION & PAGES =================
if 'logged_in' not in st.session_state: st.session_state.logged_in = False

if not st.session_state.logged_in:
    _, col_mid, _ = st.columns([1, 1, 1])
    with col_mid:
        st.header("🏢 Admin Login")
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")
        if st.button("Seeni"):
            if u == "admin" and p == "123":
                st.session_state.logged_in = True
                st.rerun()
            else:
                st.error("Username ykn Password dogoggora!")
else:
    df = load_data()
    menu = st.sidebar.radio("FILANNOO", ["📊 Dashboard", "📝 Galmee Haaraa", "📈 Gabaasa", "🏆 Badhaasa", "🔍 Barbaadi", "Ba'i"])

    if menu == "📊 Dashboard":
        st.header("📊 Dashboard Overview")
        if not df.empty:
            c1, c2, c3 = st.columns(3)
            c1.metric("💰 Galii Waliigalaa", f"{df['Kafaltii_Taj'].sum():,.2f} ETB")
            c2.metric("👥 Maamiltoota", len(df))
            c3.metric("👷 Ogeeyyii", df['Maqaa_Ogeessa'].nunique())
            st.area_chart(df.groupby('Ji\'a')['Kafaltii_Taj'].sum().reindex(MONTH_ORDER).fillna(0))

    elif menu == "📝 Galmee Haaraa":
        st.header("📝 Galmee Tajaajilaa")
        GATII_DICT = {
            "Gibira": ["Gibira Baaxii Gooroo", "Gibira Lafa Qonnaa", "Gibira Manaa"],
            "Liizii": ["Liizii Waggaa", "Jijjiirraa Maqaa", "TOT"],
            "Kaartaa": ["Kaartaa Haaraa", "Kaartaa Haaromsuu"]
        }
        
        selected_main = st.multiselect("Gosa Tajaajilaa:", list(GATII_DICT.keys()))
        details, fees = [], 0
        
        if selected_main:
            for g in selected_main:
                subs = st.multiselect(f"Tajaajila {g}:", GATII_DICT[g])
                for s in subs:
                    details.append(f"{g}-{s}")
                    f_val = st.number_input(f"Kaffaltii {s}:", min_value=0.0)
                    fees += f_val

        with st.form("main_form"):
            name = st.text_input("Maqaa Maamilaa")
            ara = st.text_input("Araddaa")
            ogeessa = st.text_input("Maqaa Ogeessaa")
            nagahee = st.file_uploader("Nagahee (Scan)", type=['jpg','png'])
            
            if st.form_submit_button("💾 Galmeessi"):
                if name and details and ogeessa:
                    if nagahee:
                        f_name = f"{name}_{datetime.now().strftime('%H%M%S')}.jpg"
                        with open(os.path.join(NAGAHEE_DIR, f_name), "wb") as f:
                            f.write(nagahee.getbuffer())
                    
                    new_row = [datetime.now().strftime('%d/%m/%Y'), name, ara, "-", ", ".join(details), ogeessa, fees]
                    df = pd.concat([df, pd.DataFrame([new_row], columns=COL_NAMES)], ignore_index=True)
                    save_data(df)
                    st.success("Galmeeffameera!")
                else:
                    st.error("Odeeffannoo guuti!")

    elif menu == "🏆 Badhaasa":
        st.header("🏆 Beekamtii Ogeeyyii")
        l_l = st.file_uploader("Logo Bitaa", type=['png','jpg'])
        l_r = st.file_uploader("Logo Mirgaa", type=['png','jpg'])
        
        if not df.empty:
            top_3 = df['Maqaa_Ogeessa'].value_counts().head(3)
            for i, (name, count) in enumerate(top_3.items(), 1):
                st.write(f"**{i}. {name}** - {count} Hojii")
                pdf_bytes = create_advanced_pdf(name, count, i, l_l, l_r)
                st.download_button(f"📥 PDF {name}", pdf_bytes, f"Cert_{name}.pdf")

    elif menu == "Ba'i":
        st.session_state.logged_in = False
        st.rerun()



import streamlit as st
import pandas as pd
import os
import io
import requests
from datetime import datetime
from fpdf import FPDF
import plotly.express as px

# ================= 1. CONFIGURATION & STYLE =================
LOGO_PATH = "Adiaan/logo.png"
NAGAHEE_DIR = "nagahee_scan"
DATA_FILE = "dadar_final_report.txt"

if not os.path.exists(NAGAHEE_DIR):
    os.makedirs(NAGAHEE_DIR)

st.set_page_config(
    page_title="Dadar Land Admin Pro", 
    page_icon="🏢", 
    layout="wide"
)

# Halluu fi Style
st.markdown("""
    <style>
    .stApp { background: #f4f7f6; }
    div.stForm { background: white; border-radius: 12px; padding: 20px; border: 1px solid #ddd; }
    .card { background: white; padding: 15px; border-radius: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); text-align: center; }
    </style>
    """, unsafe_allow_html=True)

# ================= 2. SERVICE LIST (GOSA TAJAAJILAA) =================
# Gosa tajaajilaa hunda akka gosa gurguddaatti addaan baasuu
SERVICE_STRUCTURE = {
    "🏷️ Gibira & Kaffaltii": [
        "Gibira Baaxii Gooroo", "Gibira Lafa Qonnaa", "Kaffaltii Liizii Waggaa", 
        "Kaffaltii Liizii Duraa", "Gibira Milkii (Stamp Duty)", "TOT (Turnover Tax)"
    ],
    "📜 Kaartaa & Qabiyyee": [
        "Kaartaa Haaraa", "Kaartaa Bakka Bu'aa", "Kaartaa Kadastaaraa", 
        "Jijjiirraa Maqaa (Gift/Sale)", "Sirreeffama Daangaa", "Ganda Irraa gara Magaalaatti"
    ],
    "🏗️ Pilaanii & Ijaarsa": [
        "Hayyama Ijaarsaa", "Pilaanii Magaalaa", "Itti Fayyadama Lafaa (Land Use)", 
        "Mirkaneessa Sertifikeeta Ijaarsaa", "Humna Mahandisummaa"
    ],
    "⚖️ Dhimma Seeraa": [
        "Ugura Mana Murtii", "Ugura Kaasuu", "Waliigaltee Liqii Baankii", 
        "Waliigaltee Hiikuu", "Dhimma Dhala (Inheritance)"
    ],
    "📂 Tajaajila Biroo": [
        "Waraqaa Ragaa (Clearance)", "Deebii Iyyannoo", "Tajaajila Koppii (Photocopy)"
    ]
}

COL_NAMES = ['Guyyaa', 'Maqaa_Abbaa_Dhimmaa', 'Araddaa', 'Qaxana', 'Gosa_Tajajjilaa', 'Maqaa_Ogeessa', 'Kafaltii_Taj']

# ================= 3. CORE FUNCTIONS =================
def load_data():
    if not os.path.exists(DATA_FILE) or os.stat(DATA_FILE).st_size == 0:
        return pd.DataFrame(columns=COL_NAMES)
    return pd.read_csv(DATA_FILE, sep="|", names=COL_NAMES, header=None, encoding='utf-8')

def save_data(df_to_save):
    df_to_save[COL_NAMES].to_csv(DATA_FILE, sep="|", index=False, header=False, encoding="utf-8")

def create_certificate(name, count, rank, l_l, l_r, sig):
    pdf = FPDF(orientation='L', unit='mm', format='A4')
    pdf.add_page()
    
    # Border
    pdf.set_draw_color(0, 100, 0); pdf.set_line_width(2); pdf.rect(10, 10, 277, 190)
    
    # Logo
    if l_l: 
        with open("tmp_l.png", "wb") as f: f.write(l_l.getbuffer())
        pdf.image("tmp_l.png", 20, 15, 30)
    
    pdf.set_y(50); pdf.set_font('Arial', 'B', 30); pdf.cell(0, 10, "SARTIIFIKEETA BEEKAMTII", 0, 1, 'C')
    pdf.set_font('Arial', '', 20); pdf.cell(0, 20, f"Obbo/Adde: {name}", 0, 1, 'C')
    pdf.multi_cell(0, 10, f"Waggaa 2026 keessatti maamiltoota {count} tajaajiluun sadarkaa {rank}ffaa argataniiru.", align='C')
    
    # Signature
    if sig:
        with open("tmp_sig.png", "wb") as f: f.write(sig.getbuffer())
        pdf.image("tmp_sig.png", 50, 160, 30)
    
    pdf.line(40, 180, 100, 180); pdf.set_xy(40, 182); pdf.cell(60, 10, "Itti Gaafatamaa", align='C')
    return pdf.output(dest='S').encode('latin-1', 'replace')

# ================= 4. MAIN NAVIGATION =================
if 'logged_in' not in st.session_state: st.session_state.logged_in = False

if not st.session_state.logged_in:
    # Login Section
    st.title("🔐 Dadar Land Admin Login")
    u = st.text_input("Username")
    p = st.text_input("Password", type="password")
    if st.button("Seeni"):
        if u == "DAD" and p == "2026": 
            st.session_state.logged_in = True
            st.rerun()
else:
    df = load_data()
    menu = st.sidebar.radio("FILANNOO", ["📊 Dashboard", "📝 Galmee Haaraa", "🏆 Badhaasa", "📈 Gabaasa"])

    # --- REGISTRATION ---
    if menu == "📝 Galmee Haaraa":
        st.header("📝 Galmee Tajaajilaa Haaraa")
        
        # Filannoo Tajaajilaa
        st.subheader("🟢 Gosa Tajaajilaa Filadhu")
        selected_cats = st.multiselect("Ramaddii Tajaajilaa:", list(SERVICE_STRUCTURE.keys()))
        
        final_services = []
        total_fee = 0
        
        if selected_cats:
            cols = st.columns(len(selected_cats))
            for i, cat in enumerate(selected_cats):
                with cols[i]:
                    st.write(f"**{cat}**")
                    subs = st.multiselect(f"Tajaajiloota {cat}:", SERVICE_STRUCTURE[cat], key=cat)
                    for s in subs:
                        fee = st.number_input(f"Kaffaltii {s}:", min_value=0.0, key=f"fee_{s}")
                        final_services.append(s)
                        total_fee += fee

        st.divider()
        
        with st.form("reg_form"):
            c1, c2 = st.columns(2)
            name = c1.text_input("Maqaa Maamilaa")
            ara = c2.text_input("Araddaa")
            qax = c1.text_input("Qaxana")
            ogeessa = c2.text_input("Ogeessa Raawwate")
            
            # Nagahee Upload
            nagahee = st.file_uploader("Nagahee Scan (Image)", type=['jpg','png','jpeg'])
            
            if st.form_submit_button("💾 Galmeessi"):
                if name and final_services:
                    # Save Image
                    if nagahee:
                        f_path = os.path.join(NAGAHEE_DIR, f"{name}_{datetime.now().strftime('%H%M%S')}.jpg")
                        with open(f_path, "wb") as f: f.write(nagahee.getbuffer())
                    
                    # Save Data
                    new_row = [datetime.now().strftime('%d/%m/%Y'), name, ara, qax, ", ".join(final_services), ogeessa, total_fee]
                    df = pd.concat([df, pd.DataFrame([new_row], columns=COL_NAMES)], ignore_index=True)
                    save_data(df)
                    st.success(f"✅ Galmeeffameera! Waliigala: {total_fee} ETB")
                else:
                    st.error("Maaloo odeeffannoo guutuu galchi!")

    # --- DASHBOARD ---
    elif menu == "📊 Dashboard":
        st.title("📊 Dashboard")
        if not df.empty:
            c1, c2, c3 = st.columns(3)
            c1.metric("💰 Waliigala Galii", f"{df['Kafaltii_Taj'].sum():,.2f} ETB")
            c2.metric("👥 Baay'ina Maamiltootaa", len(df))
            c3.metric("👷 Ogeeyyii", df['Maqaa_Ogeessa'].nunique())
            
            st.subheader("Trendii Kaffaltii")
            fig = px.bar(df, x='Guyyaa', y='Kafaltii_Taj', color='Maqaa_Ogeessa')
            st.plotly_chart(fig, use_container_width=True)

    # --- BADHAASA ---
    elif menu == "🏆 Badhaasa":
        st.header("🏆 Beekamtii Ogeeyyii")
        sig = st.file_uploader("Mallattoo Itti Gaafatamaa (PNG)", type=['png'])
        if not df.empty:
            top = df['Maqaa_Ogeessa'].value_counts().head(3)
            for i, (n, c) in enumerate(top.items(), 1):
                st.write(f"**{i}. {n}** ({c} tajaajila)")
                pdf = create_certificate(n, c, i, None, None, sig)
                st.download_button(f"📥 Sartiifikeeta {n}", pdf, f"Cert_{n}.pdf")

    # --- GABAASA ---
    elif menu == "📈 Gabaasa":
        st.header("📋 Galmeewwan Hundi")
        st.dataframe(df, use_container_width=True)
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Excel/CSV Buusi", csv, "Gabaasa.csv", "text/csv")

# --- GALMEE & CLEARANCE ---
elif menu == "📝 Galmee & Clearance":
    st.header("📝 Galmee fi Qophii Clearance")}
    
    # Logo Configuration in Sidebar
    st.sidebar.subheader("⚙️ Qindaa'ina Mallattoo")
    up_bitta = st.sidebar.file_uploader("Logo Bittaa", type=['png', 'jpg'])
    if up_bitta:
        img_b = Image.open(up_bitta).convert("RGB").save("logo_bitta.jpg")
    
    up_mirga = st.sidebar.file_uploader("Logo Mirgaa", type=['png', 'jpg'])
    if up_mirga:
        img_m = Image.open(up_mirga).convert("RGB").save("logo_mirga.jpg")

    if st.session_state.pdf_to_download:
        st.success("📄 Clearance qophaa'eera!")
        st.download_button("📥 PDF BUUFADHU", st.session_state.pdf_to_download, st.session_state.pdf_name)
        if st.button("Galmee Haaraa"): 
            st.session_state.pdf_to_download = None
            st.rerun()

    with st.form("clearance_form"):
        c1, c2 = st.columns(2)
        m_maqaa = c1.text_input("Maqaa Maamilaa *")
        m_ogeessa = c2.text_input("Maqaa Ogeessa Galmeessu *")
        m_araddaa = c1.text_input("Araddaa *")
        m_qaxana = c2.text_input("Qaxana")
        m_kaartaa = c1.text_input("Lakk. Kaartaa")
        m_bara = c2.text_input("Bara Gibiraa (Fkn: 2017)")
        m_dhimma = st.selectbox("Dhimma Maaliif?", ["Gurgurtaa", "Liqii Bankii", "Kennaa", "Waliigaltee"])
        m_kaffaltii = st.number_input("Kaffaltii Tajaajilaa (ETB)", min_value=0.0)
        m_dhorkaa = st.checkbox("Dhorkaa irraa bilisa ta'uu nan mirkaneessa")

        if st.form_submit_button("💾 GALMEESSI FI PDF UUMI"):
            if m_maqaa and m_ogeessa and m_dhorkaa:
                # Save to Data
                new_row = [get_ethiopian_date_str(), m_maqaa, m_araddaa, m_qaxana, "Clearance", m_ogeessa, m_kaffaltii]
                df = pd.concat([df, pd.DataFrame([new_row], columns=COL_NAMES)], ignore_index=True)
                save_data(df)
                
                # Generate PDF
                data_map = {'maqaa': m_maqaa, 'araddaa': m_araddaa, 'qaxana': m_qaxana, 'kaartaa': m_kaartaa, 'bara_gibiraa': m_bara, 'dhimma': m_dhimma}
                st.session_state.pdf_to_download = create_clearance_pdf(data_map)
                st.session_state.pdf_name = f"Clearance_{m_maqaa.replace(' ', '_')}.pdf"
                st.rerun()
            else: st.error("Maaloo odeeffannoo guutuu galchi!")

# --- GABAASA ---
elif menu == "📈 Gabaasa":
    st.header("📈 Gabaasa Galmee Waliigalaa")
    st.dataframe(df, use_container_width=True)
    
    if st.button("🚀 Excel Gara Telegram-itti Ergi"):
        # (Asitti logic Telegram kee itti fufi)
        st.info("Gabaasni gara maanjaraatti ergamaa jira...")

# --- BADHAASA ---
elif menu == "🏆 Badhaasa":
    st.header("🏆 Ogeeyyii Baay'ee Hojjetan")
    if not df.empty:
        st.bar_chart(df['Maqaa_Ogeessa'].value_counts())












