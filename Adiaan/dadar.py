import streamlit as st
import pandas as pd
import os
import io
import requests
from datetime import datetime
import plotly.express as px
from reportlab.lib.pagesizes import A4, landscape
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.lib.colors import gold, silver, hexColor, green, black, white

# ================= 1. CONFIGURATION & STYLE =================
LOGO_PATH = "Adiaan/logo.png"
DATA_FILE = "dadar_final_report.txt"
BOT_TOKEN = "8357193631:AAHCuSnXzjZTQaglkmcS0gq-EvqnkIQLDBI"
CHAT_ID_MANAGER = "7329587700"

st.set_page_config(page_title="Dadar Land Administration", page_icon="🏢", layout="wide")

# Folder uumuu
if not os.path.exists("Adiaan"): os.makedirs("Adiaan")

# Style CSS bareedinaaf
st.markdown("""
    <style>
    .stApp { background-color: #f4f7f6; }
    [data-testid="stSidebar"] { background-color: #1b5e20 !important; }
    [data-testid="stSidebar"] * { color: white !important; }
    .card { 
        background: white; 
        padding: 20px; 
        border-radius: 15px; 
        box-shadow: 0 4px 15px rgba(0,0,0,0.1); 
        text-align: center; 
        border-top: 8px solid #2e7d32;
    }
    .metric-value { font-size: 28px; font-weight: bold; color: #2e7d32; }
    .stButton>button { width: 100%; border-radius: 8px; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# ================= 2. CORE FUNCTIONS =================
COL_NAMES = ['Guyyaa', 'Maqaa_Abbaa_Dhimmaa', 'Araddaa', 'Qaxana', 'Gosa_Tajajjilaa', 'Maqaa_Ogeessa', 'Kafaltii_Taj']

def load_data():
    if not os.path.exists(DATA_FILE) or os.stat(DATA_FILE).st_size == 0:
        return pd.DataFrame(columns=COL_NAMES)
    return pd.read_csv(DATA_FILE, sep="|", names=COL_NAMES, header=None, encoding='utf-8')

def save_data(df_to_save):
    df_to_save[COL_NAMES].to_csv(DATA_FILE, sep="|", index=False, header=False, encoding="utf-8")

def send_telegram(msg):
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        requests.post(url, data={"chat_id": CHAT_ID_MANAGER, "text": msg, "parse_mode": "HTML"})
    except: pass

def create_certificate(name, count, rank):
    packet = io.BytesIO()
    c = canvas.Canvas(packet, pagesize=landscape(A4))
    w, h = landscape(A4)
    
    # Halluu sadarkaa (1st=Gold, 2nd=Silver, 3rd=Bronze)
    color = {1: gold, 2: silver, 3: hexColor("#CD7F32")}.get(rank, green)
    
    # Design Border
    c.setStrokeColor(color); c.setLineWidth(8*mm); c.rect(5*mm, 5*mm, w-10*mm, h-10*mm)
    c.setStrokeColor(white); c.setLineWidth(1*mm); c.rect(8*mm, 8*mm, w-16*mm, h-16*mm)
    
    # Barreeffama
    c.setFont("Helvetica-Bold", 45); c.setFillColor(color)
    c.drawCentredString(w/2, h-60*mm, "SARTIIFIKEETA BEEKAMTII")
    
    c.setFont("Helvetica-Bold", 35); c.setFillColor(black)
    c.drawCentredString(w/2, h-100*mm, str(name).upper())
    
    c.setFont("Helvetica", 22)
    c.drawCentredString(w/2, h-130*mm, f"Tajaajilamtoota {count} saffisaan tajaajiluun waggaa 2026")
    c.drawCentredString(w/2, h-145*mm, f"sadarkaa {rank}ffaa waan qabataniif beekamtiin kun kennameef.")
    
    c.setFont("Helvetica-Bold", 14)
    c.drawString(30*mm, 35*mm, f"Guyyaa: {datetime.now().strftime('%d/%m/%Y')}")
    c.drawRightString(w-30*mm, 35*mm, "Mallattoo Hoogganaa: ________________")
    
    c.save(); packet.seek(0)
    return packet.getvalue()

# ================= 3. MAIN APPLICATION =================
if 'logged_in' not in st.session_state: st.session_state.logged_in = False

if not st.session_state.logged_in:
    _, col_mid, _ = st.columns([1, 1.2, 1])
    with col_mid:
        st.markdown("<h2 style='text-align:center;'>🏢 Dadar Land System</h2>", unsafe_allow_html=True)
        with st.form("login_form"):
            u = st.text_input("Username")
            p = st.text_input("Password", type="password")
            if st.form_submit_button("Seeni"):
                if u == "DAD" and p == "2026":
                    st.session_state.logged_in = True; st.rerun()
                else: st.error("Maqaa ykn Password dogoggora!")
else:
    df = load_data()
    menu = st.sidebar.radio("FILANNOO", ["📊 Dashboard", "📝 Galmee Haaraa", "📈 Gabaasa Bal'aa", "🏆 Badhaasa Ogeeyyii", "🔍 Barbaadi/Edit"])

    if menu == "📊 Dashboard":
        st.header("📊 Dashboard")
        
        if not df.empty:
            c1, c2, c3 = st.columns(3)
            with c1: st.markdown(f"<div class='card'><p>💰 Galii</p><p class='metric-value'>{df['Kafaltii_Taj'].sum():,.2f}</p></div>", unsafe_allow_html=True)
            with c2: st.markdown(f"<div class='card'><p>👥 Maamiltoota</p><p class='metric-value'>{len(df)}</p></div>", unsafe_allow_html=True)
            with c3: st.markdown(f"<div class='card'><p>👷 Ogeeyyii</p><p class='metric-value'>{df['Maqaa_Ogeessa'].nunique()}</p></div>", unsafe_allow_html=True)
            
            fig = px.area(df, x='Guyyaa', y='Kafaltii_Taj', title="Sochi Galii Guyyaa", color_discrete_sequence=['#2e7d32'])
            st.plotly_chart(fig, use_container_width=True)
        else: st.info("Data'n galmaa'e hin jiru.")

    elif menu == "📝 Galmee Haaraa":
        st.header("📝 Galmee Tajaajilaa")
        GATII_DICT = {
            "Gibira": ["Baaxii Gooroo", "Lafa Qonnaa"],
            "Liizii": ["Liizii Waggaa", "Jijjiirraa Maqaa", "Kafaltii Duraa"],
            "Kaartaa": ["Kaartaa Lafa", "Kaartaa Kadastaara"]
        }
        
        selected_main = st.multiselect("🟢 Gosa Tajaajilaa", list(GATII_DICT.keys()))
        details, total_fee = [], 0
        if selected_main:
            for g in selected_main:
                subs = st.multiselect(f"Tajaajila {g}:", GATII_DICT[g])
                for s in subs:
                    fee = st.number_input(f"Kafaltii {s} (ETB)", min_value=0.0)
                    details.append(f"{g}({s})")
                    total_fee += fee

        with st.form("reg_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            maqaa = col1.text_input("Maqaa Abbaa Dhimmaa *")
            ara = col2.text_input("Araddaa *")
            qax = col1.text_input("Qaxana *")
            ogeessa = col2.text_input("Maqaa Ogeessaa *")
            
            if st.form_submit_button("💾 Galmeessi"):
                if maqaa and ogeessa and details:
                    new_row = [datetime.now().strftime('%d/%m/%Y'), maqaa, ara, qax, ", ".join(details), ogeessa, total_fee]
                    df = pd.concat([df, pd.DataFrame([new_row], columns=COL_NAMES)], ignore_index=True)
                    save_data(df)
                    send_telegram(f"🔔 <b>Galmee Haaraa</b>\n👤 Maamila: {maqaa}\n👷 Ogeessa: {ogeessa}\n💰 Kafaltii: {total_fee} ETB")
                    st.success("✅ Milkaa'inaan Galmeeffameera!"); st.balloons()
                else: st.error("Maaloo, bakka mallattoo (*) qaban guuti!")

    elif menu == "📈 Gabaasa Bal'aa":
        st.header("📈 Gabaasa guutuu")
        if not df.empty:
            st.dataframe(df, use_container_width=True)
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                df.to_excel(writer, index=False, sheet_name='Sheet1')
            st.download_button("📥 Excel Buufadhu", output.getvalue(), "Gabaasa_Full.xlsx")

    elif menu == "🏆 Badhaasa Ogeeyyii":
        st.header("🏆 Sadarkaa fi Badhaasa Ogeeyyii")
        
        if not df.empty:
            top_3 = df['Maqaa_Ogeessa'].value_counts().head(3)
            cols = st.columns(3)
            for i, (name, count) in enumerate(top_3.items(), 1):
                with cols[i-1]:
                    st.markdown(f"<div class='card'><h2>{i}ffaa</h2><h3>{name}</h3><p>Hojii: {count}</p></div>", unsafe_allow_html=True)
                    cert_pdf = create_certificate(name, count, i)
                    st.download_button(f"📥 PDF Buusi ({i})", cert_pdf, f"Cert_{name}.pdf", key=f"d_{i}")
        else: st.info("Hojii ogeessaa hin jiru.")

    elif menu == "🔍 Barbaadi/Edit":
        st.header("🔍 Barbaadi fi Sirreessi")
        q = st.text_input("Maqaa barbaduuf asitti barreessi...")
        if q and not df.empty:
            res = df[df['Maqaa_Abbaa_Dhimmaa'].str.contains(q, case=False, na=False)]
            for idx, row in res.iterrows():
                with st.expander(f"📄 {row['Maqaa_Abbaa_Dhimmaa']}"):
                    new_n = st.text_input("Maqaa Sirreessi", row['Maqaa_Abbaa_Dhimmaa'], key=f"ed_{idx}")
                    if st.button("Update", key=f"up_{idx}"):
                        df.at[idx, 'Maqaa_Abbaa_Dhimmaa'] = new_n
                        save_data(df); st.success("Sirreeffameera!"); st.rerun()
                    if st.button("Haqi", key=f"del_{idx}"):
                        df = df.drop(idx); save_data(df); st.warning("Haqameera!"); st.rerun()

    if st.sidebar.button("🚪 Ba'i"):
        st.session_state.logged_in = False; st.rerun()
