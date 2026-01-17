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
DATA_FILE = "dadar_final_report.txt"
COL_NAMES = ['Guyyaa', 'Maqaa_Abbaa_Dhimmaa', 'Araddaa', 'Qaxana', 'Gosa_Tajajjilaa', 'Maqaa_Ogeessa', 'Kafaltii_Taj']

# --- TELEGRAM CONFIG ---
BOT_TOKEN = "8357193631:AAHCuSnXzjZTQaglkmcS0gq-EvqnkIQLDBI" 
CHAT_ID = "7329587700" 

st.set_page_config(page_title="Dadar Land System", page_icon="🏢", layout="wide")

st.markdown("""
    <style>
    [data-testid="stHeader"] {display: none !important;}
    header {visibility: hidden !important;}
    .stAppToolbar {display: none !important;}
    .stDeployButton {display: none !important;}
    #MainMenu {visibility: hidden !important;}
    footer {visibility: hidden !important;}
    .block-container { padding-top: 1rem !important; }
    .stApp { background: linear-gradient(135deg, #f1f8e9 0%, #ffffff 100%); }
    [data-testid="stSidebar"] { background-color: #1b5e20 !important; }
    [data-testid="stSidebar"] * { color: #ffffff !important; }
    .card { 
        background: white; padding: 20px; border-radius: 12px; 
        box-shadow: 0 4px 6px rgba(0,0,0,0.1); text-align: center; 
        border-top: 8px solid #2e7d32; margin-bottom: 10px; 
    }
    .metric-value { font-size: 24px; font-weight: bold; color: #2e7d32; }
    </style>
    """, unsafe_allow_html=True)

# ================= 2. CORE FUNCTIONS =================
def load_data():
    if not os.path.exists(DATA_FILE) or os.stat(DATA_FILE).st_size == 0:
        return pd.DataFrame(columns=COL_NAMES)
    return pd.read_csv(DATA_FILE, sep="|", names=COL_NAMES, header=None, encoding='utf-8')

def save_data(df_to_save):
    df_to_save.to_csv(DATA_FILE, sep="|", index=False, header=False, encoding="utf-8")

def send_telegram_msg(msg):
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        payload = {"chat_id": CHAT_ID, "text": msg, "parse_mode": "HTML"}
        requests.post(url, data=payload)
    except: pass

def create_certificate(name, count, rank):
    pdf = FPDF(orientation='L', unit='mm', format='A4')
    pdf.add_page()
    colors = {1: (255, 215, 0), 2: (192, 192, 192), 3: (205, 127, 50)}
    r_color = colors.get(rank, (0, 80, 0))
    pdf.set_draw_color(0, 80, 0); pdf.set_line_width(3); pdf.rect(10, 10, 277, 190)
    pdf.set_draw_color(*r_color); pdf.set_line_width(1.2); pdf.rect(13, 13, 271, 184)
    if os.path.exists(LOGO_PATH):
        pdf.image(LOGO_PATH, x=20, y=18, w=25)
        pdf.image(LOGO_PATH, x=250, y=18, w=25)
    pdf.set_y(55); pdf.set_text_color(*r_color); pdf.set_font('Arial', 'B', 40)
    pdf.cell(0, 15, "SARTIIFIKETA BEEKAMTII", ln=True, align='C')
    pdf.set_y(95); pdf.set_text_color(0, 0, 0); pdf.set_font('Arial', 'B', 35)
    pdf.cell(0, 20, str(name).upper(), ln=True, align='C')
    pdf.set_y(125); pdf.set_font('Arial', '', 20)
    pdf.cell(0, 10, f"Tajaajilamtoota {count} saffisaan tajaajiluun waggaa 2026", ln=True, align='C')
    pdf.cell(0, 10, f"sadarkaa {rank}ffaa waan qabataniif beekamtiin kun kennameef.", ln=True, align='C')
    pdf.set_y(165); pdf.set_font('Arial', 'B', 12)
    pdf.cell(100, 10, f"Guyyaa: {datetime.now().strftime('%d/%m/%Y')}", ln=0, align='C')
    pdf.cell(150, 10, "Mallattoo Hoogganaa: ________________", ln=1, align='C')
    return pdf.output(dest='S').encode('latin-1')

# ================= 3. MAIN APPLICATION =================
if 'logged_in' not in st.session_state: st.session_state.logged_in = False

if not st.session_state.logged_in:
    _, col_mid, _ = st.columns([1, 1, 1])
    with col_mid:
        st.markdown("<h2 style='text-align:center;'>Admin Login</h2>", unsafe_allow_html=True)
        with st.form("login"):
            u = st.text_input("Username")
            p = st.text_input("Password", type="password")
            if st.form_submit_button("Seeni"):
                if u == "DAD" and p == "2026":
                    st.session_state.logged_in = True; st.rerun()
                else: st.error("Koodii dogoggora!")
else:
    df = load_data()
    with st.sidebar:
        st.title("🏢 Dadar Land")
        menu = st.radio("FILANNOO", ["📊 Dashboard", "📝 Galmee Haaraa", "🏆 Badhaasa Ogeeyyii"])
        if st.button("🚪 Log Out"):
            st.session_state.logged_in = False; st.rerun()

    if menu == "📊 Dashboard":
        st.title("📊 Dashboard Gabaasaa")
        if not df.empty:
            c1, c2, c3 = st.columns(3)
            with c1: st.markdown(f"<div class='card'><p style='color:gray;'>💰 Galii</p><p class='metric-value'>{df['Kafaltii_Taj'].sum():,.2f} ETB</p></div>", unsafe_allow_html=True)
            with c2: st.markdown(f"<div class='card'><p style='color:gray;'>👥 Maamiltoota</p><p class='metric-value'>{len(df)}</p></div>", unsafe_allow_html=True)
            with c3: st.markdown(f"<div class='card'><p style='color:gray;'>👷 Ogeeyyii</p><p class='metric-value'>{df['Maqaa_Ogeessa'].nunique()}</p></div>", unsafe_allow_html=True)
            
            st.write("---")
            col_l, col_r = st.columns([2, 1])
            with col_l:
                st.subheader("📈 Sochi Galii Guyyaan")
                daily_rev = df.groupby('Guyyaa')['Kafaltii_Taj'].sum().reset_index()
                fig_line = px.line(daily_rev, x='Guyyaa', y='Kafaltii_Taj', markers=True, color_discrete_sequence=['#2e7d32'])
                st.plotly_chart(fig_line, use_container_width=True)
            with col_r:
                st.subheader("🏘️ Araddaaleen")
                ar_counts = df['Araddaa'].value_counts().reset_index()
                ar_counts.columns = ['Araddaa', 'Count']
                fig_bar = px.bar(ar_counts, x='Araddaa', y='Count', color='Araddaa')
                st.plotly_chart(fig_bar, use_container_width=True)

            st.write("---")
            col_pie, col_tbl = st.columns([1, 1])
            with col_pie:
                st.subheader("🍕 Qoodinsa Galii (%)")
                service_data = df.groupby('Gosa_Tajajjilaa')['Kafaltii_Taj'].sum().reset_index()
                fig_pie = px.pie(service_data, values='Kafaltii_Taj', names='Gosa_Tajajjilaa', hole=0.5, color_discrete_sequence=px.colors.sequential.Greens_r)
                st.plotly_chart(fig_pie, use_container_width=True)
            with col_tbl:
                st.subheader("📋 Galmee Dhumaa")
                st.dataframe(df.tail(5), use_container_width=True)

            # Excel Download
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                df.to_excel(writer, index=False, sheet_name='Gabaasa')
            st.download_button("📊 Download Excel Report", output.getvalue(), f"Gabaasa_{datetime.now().strftime('%d_%m')}.xlsx")
        else: st.info("Data'n hin jiru.")

    elif menu == "📝 Galmee Haaraa":
        st.header("📝 Galmee Tajaajilaa Haaraa")
        with st.form("reg_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            maqaa = col1.text_input("Maqaa Abbaa Dhimmaa")
            araddaa = col2.text_input("Araddaa")
            qaxana = col1.text_input("Qaxana")
            ogeessa = col2.text_input("Maqaa Ogeessaa")
            gosa_taj = st.selectbox("Gosa Tajaajilaa", ["Gibira Lafa Qonnaa", "Gibira Baaxii Gooroo", "Kaartaa Haaraa", "Jijjiirraa Maqaa", "Liizii Waggaa"])
            kafalltii = st.number_input("Kafaltii (ETB)", min_value=0.0)
            
            if st.form_submit_button("💾 Galmeessi"):
                if maqaa and ogeessa:
                    new_data = [datetime.now().strftime('%d/%m/%Y'), maqaa, araddaa, qaxana, gosa_taj, ogeessa, kafalltii]
                    df = pd.concat([df, pd.DataFrame([new_data], columns=COL_NAMES)], ignore_index=True)
                    save_data(df)
                    
                    # Telegram Notification
                    tlg_msg = f"🔔 <b>GALMEE HAARAA</b>\n👤 Maamila: {maqaa}\n🏘️ Araddaa: {araddaa}\n🛠️ Tajaajila: {gosa_taj}\n👷 Ogeessa: {ogeessa}\n💰 Kafaltii: {kafalltii:,.2f} ETB"
                    send_telegram_msg(tlg_msg)
                    
                    st.success("Milkaa'inaan Galmeeffameera! Gabaasni gara Telegram ergameera.")
                    st.balloons()
                else: st.error("Maaloo, maqaa maamilaa fi ogeessaa guuti.")

    elif menu == "🏆 Badhaasa Ogeeyyii":
        st.header("🏆 Sadarkaa Ogeeyyii")
        if not df.empty:
            top_3 = df['Maqaa_Ogeessa'].value_counts().head(3)
            cols = st.columns(3)
            for i, (name, count) in enumerate(top_3.items()):
                with cols[i]:
                    st.markdown(f"<div class='card'><h2>{i+1}FFAA</h2><h3>{name}</h3><p>Hojii: {count}</p></div>", unsafe_allow_html=True)
                    pdf_data = create_certificate(name, count, i+1)
                    st.download_button(f"📥 Cert {i+1}", pdf_data, f"Cert_{name}.pdf", "application/pdf")
        else: st.info("Data'n hin jiru.")
