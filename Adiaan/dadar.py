import streamlit as st
import pandas as pd
import os
import io
import requests
from datetime import datetime
from fpdf import FPDFimport streamlit as st
import pandas as pd
import os
import io
import requests
from datetime import datetime
from fpdf import FPDF
import plotly.express as px

# ================= 1. CONFIG & STYLE =================
DATA_FILE = "dadar_final_report.txt"
COL_NAMES = ['Guyyaa', 'Maqaa_Abbaa_Dhimmaa', 'Araddaa', 'Qaxana', 'Gosa_Tajajjilaa', 'Maqaa_Ogeessa', 'Kafaltii_Taj']
BOT_TOKEN = "8357193631:AAHCuSnXzjZTQaglkmcS0gq-EvqnkIQLDBI"
CHAT_ID_MANAGER = "7329587700"

st.set_page_config(page_title="Dadar Land Admin Pro", layout="wide", page_icon="🏢")

st.markdown("""
    <style>
    .stApp { background: #f4f7f9; }
    div.stForm { background: white; border-radius: 12px; padding: 25px; border: 1px solid #2e7d32; }
    .card { background: white; padding: 20px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); text-align: center; border-top: 5px solid #2e7d32; }
    </style>
    """, unsafe_allow_html=True)

# ================= 2. CORE FUNCTIONS =================
def load_data():
    if not os.path.exists(DATA_FILE) or os.stat(DATA_FILE).st_size == 0:
        return pd.DataFrame(columns=COL_NAMES)
    df = pd.read_csv(DATA_FILE, sep="|", names=COL_NAMES, header=None, encoding='utf-8')
    df['Kafaltii_Taj'] = pd.to_numeric(df['Kafaltii_Taj'], errors='coerce').fillna(0)
    return df

def save_data(df_to_save):
    df_to_save[COL_NAMES].to_csv(DATA_FILE, sep="|", index=False, header=False, encoding="utf-8")

def send_telegram(msg):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    try: requests.post(url, data={"chat_id": CHAT_ID_MANAGER, "text": msg, "parse_mode": "HTML"})
    except: pass

def create_pdf(name, count, rank, logo_l=None):
    pdf = FPDF(orientation='L', unit='mm', format='A4')
    pdf.add_page()
    pdf.set_draw_color(46, 125, 50); pdf.set_line_width(3); pdf.rect(10, 10, 277, 190)
    if logo_l:
        with open("tmp_logo.png", "wb") as f: f.write(logo_l.getvalue())
        pdf.image("tmp_logo.png", 20, 15, 30)
    pdf.set_y(60); pdf.set_font('Arial', 'B', 30); pdf.cell(0, 20, "SARTIIFIKETA BEEKAMTII", 0, 1, 'C')
    pdf.set_font('Arial', 'B', 22); pdf.cell(0, 15, f"Obbo/Adde: {name.upper()}", 0, 1, 'C')
    pdf.set_font('Arial', '', 16); pdf.multi_cell(0, 10, f"Waggaa 2026 keessatti tajaajilamtoota {count} tajaajiluun sadarkaa {rank}ffaa argataniiru.", align='C')
    return pdf.output(dest='S').encode('latin-1', 'replace')

# ================= 3. APP NAVIGATION =================
if 'logged_in' not in st.session_state: st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("🔐 Dadar Land Admin Login")
    u, p = st.text_input("Username"), st.text_input("Password", type="password")
    if st.button("Seeni"):
        if u == "admin" and p == "123": st.session_state.logged_in = True; st.rerun()
        else: st.error("Dogoggora!")
else:
    df = load_data()
    menu = st.sidebar.radio("FILANNOO", ["📊 Dashboard", "📝 Galmee Haaraa", "📈 Gabaasa", "🏆 Badhaasa", "🔍 Barbaadi/Haqi", "Ba'i"])

    if menu == "📊 Dashboard":
        st.header("📊 Dashboard")
        c1, c2, c3 = st.columns(3)
        c1.metric("💰 Galii Waliigalaa", f"{df['Kafaltii_Taj'].sum():,.2f} ETB")
        c2.metric("👥 Maamiltoota", len(df))
        c3.metric("👷 Ogeeyyii", df['Maqaa_Ogeessa'].nunique())
        if not df.empty:
            st.plotly_chart(px.pie(df, names='Maqaa_Ogeessa', values='Kafaltii_Taj', title="Galii Ogeeyyiin"), use_container_width=True)

    elif menu == "📝 Galmee Haaraa":
        st.header("📝 Galmee Haaraa")
        GATII_DICT = {"🏷 Gibira": ["Gibira Baaxii Gooroo", "Gibira Lafa Qonnaa"], "📜 Kaartaa": ["Kaartaa Haaraa", "Kaartaa Kadastaara"], "⚖️ Seera": ["TOT", "Jijjiirraa Maqaa"]}
        
        selected_cats = st.multiselect("Ramaddii:", list(GATII_DICT.keys()))
        total_fee, selected_subs, is_tot = 0, [], False
        
        for cat in selected_cats:
            subs = st.multiselect(f"Tajaajiloota {cat}:", GATII_DICT[cat])
            for s in subs:
                gatii = st.number_input(f"Gatii {s}:", min_value=0.0, key=f"f_{s}")
                if s == "TOT": 
                    is_tot = True
                    gatii = gatii * 0.02 # TOT %2 herregama
                total_fee += gatii
                selected_subs.append(s)

        with st.form("reg_form"):
            if is_tot:
                c1, c2 = st.columns(2)
                name = f"G: {c1.text_input('Maqaa Gurguraa')} / B: {c2.text_input('Maqaa Bitataa')}"
                ara, qax = c1.text_input("Araddaa"), c2.text_input("Qaxana")
            else:
                name = st.text_input("Maqaa Abbaa Dhimmaa")
                c1, c2 = st.columns(2)
                ara, qax = c1.text_input("Araddaa"), c2.text_input("Qaxana")
            
            og = st.text_input("Maqaa Ogeessaa")
            if st.form_submit_button("💾 GALMEESSI"):
                if name and selected_subs and og:
                    new_row = [datetime.now().strftime('%d/%m/%Y'), name, ara, qax, ", ".join(selected_subs), og, total_fee]
                    df = pd.concat([df, pd.DataFrame([new_row], columns=COL_NAMES)], ignore_index=True)
                    save_data(df)
                    send_telegram(f"✅ <b>Galmee Haaraa</b>\nMaamila: {name}\nKaffaltii: {total_fee} ETB\nOgeessa: {og}")
                    st.success(f"Milkaa'inaan galmeeffameera! Gatii: {total_fee}")
                else: st.error("Odeeffannoo guuti!")

    elif menu == "📈 Gabaasa":
        st.header("📈 Gabaasa")
        st.dataframe(df[COL_NAMES], use_container_width=True)
        buf = io.BytesIO()
        df.to_excel(buf, index=False)
        st.download_button("📥 Excel Buufadhu", buf.getvalue(), "Gabaasa.xlsx")

    elif menu == "🏆 Badhaasa":
        st.header("🏆 Sartiifiikeeta")
        logo = st.file_uploader("Logo Filadhu")
        if not df.empty:
            top = df['Maqaa_Ogeessa'].value_counts().head(3)
            for i, (n, c) in enumerate(top.items()):
                st.write(f"**{i+1}. {n}** ({c} tajaajile)")
                pdf = create_pdf(n, c, i+1, logo)
                st.download_button(f"📥 PDF {n}", pdf, f"Cert_{n}.pdf")

    elif menu == "🔍 Barbaadi/Haqi":
        q = st.text_input("Maqaa Barbaadi...")
        if q:
            res = df[df['Maqaa_Abbaa_Dhimmaa'].str.contains(q, case=False, na=False)]
            st.table(res)
            idx = st.number_input("Index galmee haquu barbaadduu galchi:", min_value=0, max_value=len(df)-1, step=1)
            if st.button("🗑 Haqi"):
                df = df.drop(idx)
                save_data(df)
                st.warning("Galmeen haqameera!")
                st.rerun()

    elif menu == "Ba'i":
        st.session_state.logged_in = False
        st.rerun()
import plotly.express as px

# ================= 1. CONFIGURATION =================
DATA_FILE = "dadar_final_report.txt"
COL_NAMES = ['Guyyaa', 'Maqaa_Abbaa_Dhimmaa', 'Araddaa', 'Qaxana', 'Gosa_Tajajjilaa', 'Maqaa_Ogeessa', 'Kafaltii_Taj']
BOT_TOKEN = "8357193631:AAHCuSnXzjZTQaglkmcS0gq-EvqnkIQLDBI"
CHAT_ID_MANAGER = "7329587700"

st.set_page_config(page_title="Dadar Land Admin Pro", layout="wide", page_icon="🏢")

# Styling
st.markdown("""
    <style>
    .stApp { background: #f4f7f9; }
    div.stForm { background: white; border-radius: 12px; padding: 25px; border: 1px solid #2e7d32; box-shadow: 0px 4px 10px rgba(0,0,0,0.05); }
    .card { background: white; padding: 20px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); text-align: center; border-top: 5px solid #2e7d32; margin-bottom: 15px; }
    </style>
    """, unsafe_allow_html=True)

# ================= 2. CORE FUNCTIONS =================
def load_data():
    if not os.path.exists(DATA_FILE) or os.stat(DATA_FILE).st_size == 0:
        return pd.DataFrame(columns=COL_NAMES)
    df = pd.read_csv(DATA_FILE, sep="|", names=COL_NAMES, header=None, encoding='utf-8')
    df['Kafaltii_Taj'] = pd.to_numeric(df['Kafaltii_Taj'], errors='coerce').fillna(0)
    return df

def save_data(df_to_save):
    df_to_save[COL_NAMES].to_csv(DATA_FILE, sep="|", index=False, header=False, encoding="utf-8")

def send_telegram_msg(msg):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID_MANAGER, "text": msg, "parse_mode": "HTML"}
    try: requests.post(url, data=payload)
    except: pass

def create_advanced_pdf(name, count, rank, logo_l=None, logo_r=None):
    pdf = FPDF(orientation='L', unit='mm', format='A4')
    pdf.add_page()
    pdf.set_draw_color(46, 125, 50)
    pdf.set_line_width(3)
    pdf.rect(10, 10, 277, 190)
    if logo_l: 
        with open("t_l.png", "wb") as f: f.write(logo_l.getvalue())
        pdf.image("t_l.png", 20, 15, 30)
    pdf.set_y(60); pdf.set_font('Arial', 'B', 30); pdf.cell(0, 20, "SARTIIFIKETA BEEKAMTII", 0, 1, 'C')
    pdf.set_font('Arial', 'B', 22); pdf.cell(0, 15, f"Obbo/Adde: {name.upper()}", 0, 1, 'C')
    pdf.ln(10); pdf.set_font('Arial', '', 16)
    pdf.multi_cell(0, 10, f"Waggaa 2026 keessatti tajaajilamtoota {count} tajaajiluun sadarkaa {rank}ffaa argataniiru.", align='C')
    return pdf.output(dest='S').encode('latin-1', 'replace')

# ================= 3. APP LOGIC =================
if 'logged_in' not in st.session_state: st.session_state.logged_in = False

if not st.session_state.logged_in:
    _, center, _ = st.columns([1,1,1])
    with center:
        st.title("🔐 Login")
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")
        if st.button("Seeni"):
            if u == "admin" and p == "123":
                st.session_state.logged_in = True
                st.rerun()
            else: st.error("Dogoggora!")
else:
    df = load_data()
    menu = st.sidebar.radio("FILANNOO", ["📊 Dashboard", "📝 Galmee Haaraa", "📈 Gabaasa", "🏆 Badhaasa", "🔍 Barbaadi/Sirreessi", "Ba'i"])

    if menu == "📊 Dashboard":
        st.header("📊 Dashboard")
        c1, c2, c3 = st.columns(3)
        c1.metric("💰 Galii", f"{df['Kafaltii_Taj'].sum():,.2f} ETB")
        c2.metric("👥 Maamiltoota", len(df))
        c3.metric("👷 Ogeeyyii", df['Maqaa_Ogeessa'].nunique())
        if not df.empty:
            st.plotly_chart(px.bar(df.groupby('Maqaa_Ogeessa')['Kafaltii_Taj'].sum().reset_index(), x='Maqaa_Ogeessa', y='Kafaltii_Taj', color='Maqaa_Ogeessa'), use_container_width=True)

    elif menu == "📝 Galmee Haaraa":
        st.header("📝 Galmee Haaraa")
        GATII_DICT = {"🏷 Gibira": ["Gibira Baaxii Gooroo", "Gibira Lafa Qonnaa"], "📜 Kaartaa": ["Kaartaa Haaraa", "Kaartaa Kadastaara"], "⚖️ Seera": ["TOT", "Jijjiir

