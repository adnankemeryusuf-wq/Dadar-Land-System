import streamlit as st
import pandas as pd
import os
import io
import requests
from datetime import datetime
from reportlab.lib.pagesizes import A4, landscape
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.lib.colors import gold, silver, hexColor, green, black, white

# ================= 1. QINDEESSA (CONFIG) =================
LOGO_PATH = "Adiaan/logo.png"
DATA_FILE = "dadar_final_report.txt"
BOT_TOKEN = "8357193631:AAHCuSnXzjZTQaglkmcS0gq-EvqnkIQLDBI"
CHAT_ID_MANAGER = "7329587700"

st.set_page_config(page_title="Dadar Land System", page_icon="🏢", layout="wide")

# Folder-oota uumuu
for folder in ["Adiaan", "Adiaan/nagahee"]:
    if not os.path.exists(folder): os.makedirs(folder)

# ================= 2. FUNKSIYOONOTA (FUNCTIONS) =================
COL_NAMES = ['Guyyaa', 'Maqaa_Abbaa_Dhimmaa', 'Araddaa', 'Qaxana', 'Gosa_Tajajjilaa', 'Maqaa_Ogeessa', 'Kafaltii_Taj']

def load_data():
    if not os.path.exists(DATA_FILE) or os.stat(DATA_FILE).st_size == 0:
        return pd.DataFrame(columns=COL_NAMES)
    return pd.read_csv(DATA_FILE, sep="|", names=COL_NAMES, header=None, encoding='utf-8')

def save_data(df):
    df[COL_NAMES].to_csv(DATA_FILE, sep="|", index=False, header=False, encoding="utf-8")

def send_telegram(msg):
    try:
        requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", 
                      data={"chat_id": CHAT_ID_MANAGER, "text": msg, "parse_mode": "HTML"})
    except: pass

def create_certificate(name, count, rank):
    packet = io.BytesIO()
    c = canvas.Canvas(packet, pagesize=landscape(A4))
    w, h = landscape(A4)
    color = {1: gold, 2: silver, 3: hexColor("#CD7F32")}.get(rank, green)
    c.setStrokeColor(color); c.setLineWidth(5); c.rect(10*mm, 10*mm, w-20*mm, h-20*mm)
    c.setFont("Helvetica-Bold", 40); c.setFillColor(color)
    c.drawCentredString(w/2, h-60*mm, "SARTIIFIKEETA BEEKAMTII")
    c.setFont("Helvetica-Bold", 30); c.setFillColor(black)
    c.drawCentredString(w/2, h-100*mm, str(name).upper())
    c.setFont("Helvetica", 18)
    c.drawCentredString(w/2, h-130*mm, f"Tajaajilamtoota {count} saffisaan tajaajiluun waggaa 2026 keessa")
    c.drawCentredString(w/2, h-140*mm, f"sadarkaa {rank}ffaa waan qabataniif beekamtiin kun kennameef.")
    c.save(); packet.seek(0)
    return packet.getvalue()

# ================= 3. LOGIN INTERFACE =================
if 'login' not in st.session_state: st.session_state.login = False

if not st.session_state.login:
    st.markdown("""
        <style>
        .login-box { background-color: #f0f2f6; padding: 50px; border-radius: 15px; border-top: 5px solid #2e7d32; box-shadow: 0 4px 10px rgba(0,0,0,0.1); }
        </style>
        """, unsafe_allow_html=True)
    _, col, _ = st.columns([1, 1, 1])
    with col:
        st.markdown('<div class="login-box">', unsafe_allow_html=True)
        if os.path.exists(LOGO_PATH): st.image(LOGO_PATH, width=100)
        st.header("🏢 Seensa Systemii")
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")
        if st.button("Seeni"):
            if u == "DAD" and p == "2026":
                st.session_state.login = True; st.rerun()
            else: st.error("Dogoggora!")
        st.markdown('</div>', unsafe_allow_html=True)

# ================= 4. MAIN APP =================
else:
    df = load_data()
    st.sidebar.image(LOGO_PATH if os.path.exists(LOGO_PATH) else None, width=100)
    menu = st.sidebar.selectbox("FILANNOO", ["📊 Dashboard", "📝 Galmee Haaraa", "🏆 Sartiifiikeeta", "🔍 Foyyessi/Haqii"])

    # --- DASHBOARD ---
    if menu == "📊 Dashboard":
        st.title("📊 Dashboard Gabaasaa")
        c1, c2, c3 = st.columns(3)
        c1.metric("💰 Galii Guutuu", f"{df['Kafaltii_Taj'].sum():,.2f} ETB")
        c2.metric("👥 Maamiltoota", len(df))
        c3.metric("👷 Ogeeyyii", df['Maqaa_Ogeessa'].nunique())
        
        # Excel Export
        out = io.BytesIO()
        with pd.ExcelWriter(out, engine='openpyxl') as w: df.to_excel(w, index=False)
        st.download_button("📥 Gabaasa Excel Buufadhu", out.getvalue(), "Gabaasa.xlsx")
        st.line_chart(df.groupby('Guyyaa')['Kafaltii_Taj'].sum())

    # --- GALMEE HAARAA ---
    elif menu == "📝 Galmee Haaraa":
        st.title("📝 Galmee Tajaajilaa Haaraa")
        with st.form("galmee"):
            m = st.text_input("Maqaa Abbaa Dhimmaa")
            a = st.text_input("Araddaa")
            o = st.text_input("Maqaa Ogeessaa")
            k = st.number_input("Kafaltii", min_value=0.0)
            t = st.multiselect("Tajaajila", ["Gibira", "Liizii", "Kaartaa", "Jijjiirraa Maqaa"])
            if st.form_submit_button("Galmeessi"):
                new = [datetime.now().strftime('%d/%m/%Y'), m, a, "-", ", ".join(t), o, k]
                df = pd.concat([df, pd.DataFrame([new], columns=COL_NAMES)], ignore_index=True)
                save_data(df); st.success("Galmeeffameera!")
                send_telegram(f"<b>🔔 Galmee Haaraa</b>\n👤: {m}\n💰: {k} ETB\n👷: {o}")

    # --- SARTIIFIIKEETA ---
    elif menu == "🏆 Sartiifiikeeta":
        st.title("🏆 Badhaasa Ogeeyyii")
        
        if not df.empty:
            top = df['Maqaa_Ogeessa'].value_counts().head(3)
            for i, (name, count) in enumerate(top.items(), 1):
                st.subheader(f"Rank {i}: {name} ({count} hojii)")
                st.download_button(f"📥 PDF {i}ffaa Buusi", create_certificate(name, count, i), f"Cert_{name}.pdf")

    # --- FOYYESSI/HAQII ---
    elif menu == "🔍 Foyyessi/Haqii":
        st.title("🔍 Data Sirreessi ykn Haqi")
        q = st.text_input("Maqaa Barbaadi...")
        if q:
            res = df[df['Maqaa_Abbaa_Dhimmaa'].str.contains(q, case=False, na=False)]
            for idx, row in res.iterrows():
                with st.expander(f"📄 {row['Maqaa_Abbaa_Dhimmaa']}"):
                    new_n = st.text_input("Maqaa Sirreessi", row['Maqaa_Abbaa_Dhimmaa'], key=f"n{idx}")
                    new_k = st.number_input("Kafaltii", float(row['Kafaltii_Taj']), key=f"k{idx}")
                    if st.button("Update", key=f"u{idx}"):
                        df.at[idx, 'Maqaa_Abbaa_Dhimmaa'] = new_n
                        df.at[idx, 'Kafaltii_Taj'] = new_k
                        save_data(df); st.success("Sirreeffameera!"); st.rerun()
                    if st.button("Haqi", key=f"h{idx}"):
                        df = df.drop(idx); save_data(df); st.warning("Haqameera!"); st.rerun()

    if st.sidebar.button("🚪 Ba'i"):
        st.session_state.login = False; st.rerun()
