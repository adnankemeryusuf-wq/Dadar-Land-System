import streamlit as st
import os
import pandas as pd
import requests
import plotly.express as px
from datetime import datetime
from fpdf import FPDF

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="Dadar Land Admin Pro", layout="wide", page_icon="🏢")

USER_NAME = "Lafa"
PASS_WORD = "1234"
DATA_FILE = "dadar_final_report.txt"
LOGO_FILE = "logo.png"
COL_NAMES = ['Yeroo', 'Maqaa', 'Araddaa', 'Qaxana', 'Gosa', 'Ogeessa', 'Status', 'C1', 'C2', 'C3', 'Kafaltii']

# Telegram API Config
TELEGRAM_TOKEN = "8357193631:AAHCuSnXzjZTQaglkmcS0gq-EvqnkIQLDBI"
TELEGRAM_CHAT_ID = "7329587700"

# --- 2. DATA FUNCTIONS ---
def load_data():
    if not os.path.exists(DATA_FILE) or os.stat(DATA_FILE).st_size == 0:
        return pd.DataFrame(columns=COL_NAMES)
    try:
        df = pd.read_csv(DATA_FILE, sep="|", names=COL_NAMES, header=None, on_bad_lines='skip', encoding='utf-8')
        return df
    except:
        return pd.DataFrame(columns=COL_NAMES)

def save_data(df):
    """Dataframe gara faayilaatti deebisanii barreessuuf"""
    df.to_csv(DATA_FILE, sep="|", index=False, header=False, encoding="utf-8")

# --- 3. CERTIFICATE (Compact Layout) ---
def generate_certificate(expert_name, total_served, year):
    pdf = FPDF(orientation='L', unit='mm', format='A4')
    pdf.add_page()
    pdf.set_line_width(1.2); pdf.set_draw_color(184, 134, 11)
    pdf.rect(5, 5, 287, 200); pdf.set_line_width(0.4); pdf.rect(8, 8, 281, 194)
    
    if os.path.exists(LOGO_FILE): pdf.image(LOGO_FILE, x=130, y=10, w=35)
    
    pdf.ln(35)
    pdf.set_font('Arial', 'B', 38); pdf.set_text_color(30, 58, 138)
    pdf.cell(0, 20, "SARTIIFIKETA BEEKAMTII", ln=True, align='C')
    
    pdf.set_font('Arial', 'I', 15); pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 8, "Waajjira Lafaa Bulchiinsa Magaalaa Dadar", ln=True, align='C')
    
    pdf.ln(10); pdf.set_font('Arial', '', 18)
    pdf.cell(0, 10, "Sartiifiketiin Gootummaa Hojii kun kan kennameef:", ln=True, align='C')
    
    pdf.ln(2); pdf.set_font('Arial', 'B', 30); pdf.set_text_color(21, 128, 61)
    pdf.cell(0, 15, f"Obbo/Adde: {expert_name.upper()}", ln=True, align='C')
    
    pdf.ln(8); pdf.set_font('Arial', '', 14); pdf.set_text_color(50, 50, 50)
    text = (f"Waggaa {year} keessatti tajaajila saffisaa, iftoomina qabuu fi "
            f"amannamaa ta'een Abbootii Dhimmaa {total_served} tajaajiluun "
            "bu'aa qabeessa ta'anii waan argamaniif beekamtii kanaan badhaafamaniiru.")
    pdf.multi_cell(0, 8, text, align='C')
    
    pdf.ln(15) # Spacing compact godhameera
    pdf.set_font('Arial', 'B', 12); pdf.set_text_color(0, 0, 0)
    pdf.cell(100, 8, "__________________________", ln=0, align='C')
    pdf.cell(87, 8, "", ln=0)
    pdf.cell(100, 8, "__________________________", ln=1, align='C')
    
    pdf.cell(100, 5, "Aqiil Abdujaaliil", ln=0, align='C')
    pdf.cell(87, 5, "", ln=0)
    pdf.cell(100, 5, datetime.now().strftime("%d/%m/%Y"), ln=1, align='C')
    
    pdf.set_font('Arial', '', 11)
    pdf.cell(100, 5, "Itti Gaafatamaa Waajjiraa", ln=0, align='C')
    pdf.cell(87, 5, "", ln=0)
    pdf.cell(100, 5, "Guyyaa", ln=1, align='C')
    
    return pdf.output(dest='S').encode('latin-1')

# --- 4. APP LOGIC ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    _, center, _ = st.columns([1, 1, 1])
    with center:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.subheader("Sistama Galmee Dadar")
        u = st.text_input("Maqaa Seensaa")
        p = st.text_input("Fungula", type="password")
        if st.button("SEENI"):
            if u == USER_NAME and p == PASS_WORD:
                st.session_state.logged_in = True
                st.rerun()
            else: st.error("Maqaa ykn Password dogoggora!")
else:
    # --- SIDEBAR & UI REFINE ---
    with st.sidebar:
        st.title("Admin Panel")
        menu = ["🏠 Dashboard", "📝 Galmee Haaraa", "🔍 Barbaaduu & Sirreessu", "📊 Gabaasa Telegr_Pro", "🏆 Sartiifiketa", "🚪 Logout"]
        choice = st.selectbox("Filannoo", menu)
        st.divider()
        st.info("Sistama Bulchiinsa Lafaa v3.7")

    st.markdown('<h1 style="text-align:center; color:#1e3a8a;">Waajjira Lafaa Magaalaa Dadar</h1>', unsafe_allow_html=True)
    df = load_data()

    # --- DASHBOARD ---
    if choice == "🏠 Dashboard":
        if not df.empty:
            c1, c2, c3 = st.columns(3)
            c1.metric("Waligala Galmee", len(df))
            c2.metric("Galii (ETB)", f"{pd.to_numeric(df['Kafaltii'], errors='coerce').sum():,.2f}")
            c3.metric("Hardha", len(df[pd.to_datetime(df['Yeroo'], errors='coerce').dt.date == datetime.now().date()]))
            st.plotly_chart(px.pie(df, names='Gosa', title="Tajaajila Gosaan"), use_container_width=True)
        else: st.info("Ragaan hin jiru.")

    # --- REGISTRATION ---
    elif choice == "📝 Galmee Haaraa":
        with st.form("reg_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            ad = col1.text_input("Maqaa Abbaa Dhimmaa")
            ar = col1.text_input("Araddaa")
            qx = col1.text_input("Qaxana / Lakk. Manaa")
            gs = col2.selectbox("Gosa Tajaajilaa", ["Ittii Fayyaddam", "Kartaa", "Jijjirra Maqaa", "Dangaa", "Mana Murttii", "Liqii Bankii"])
            og = col2.text_input("Maqaa Ogeessaa")
            kf = col2.number_input("Kafaltii", min_value=0.0)
            if st.form_submit_button("✅ GALMEESSI"):
                if ad and og:
                    line = f"{datetime.now().strftime('%Y-%m-%d %H:%M')}|{ad}|{ar}|{qx}|{gs}|{og}|Active|0|0|0|{kf}\n"
                    with open(DATA_FILE, "a", encoding="utf-8") as f: f.write(line)
                    st.success("Galmeeffameera!")
                    st.rerun()

    # --- SEARCH, EDIT & DELETE ---
    elif choice == "🔍 Barbaaduu & Sirreessu":
        st.subheader("🔍 Barbaaduu fi Sirreessu")
        search_query = st.text_input("Maqaa Abbaa Dhimmaa Barbaadi:")
        
        if not df.empty:
            filtered_df = df[df['Maqaa'].str.contains(search_query, case=False, na=False)]
            st.dataframe(filtered_df, use_container_width=True)
            
            if not filtered_df.empty:
                selected_name = st.selectbox("Namni sirreeffamu ykn haquuf filatame:", filtered_df['Maqaa'].tolist())
                idx = df[df['Maqaa'] == selected_name].index[0]
                
                with st.expander("🛠️ Sirreessu ykn Haquu"):
                    col1, col2 = st.columns(2)
                    new_ar = col1.text_input("Araddaa Sirreessi", df.at[idx, 'Araddaa'])
                    new_gs = col1.selectbox("Gosa Tajaajilaa Sirreessi", ["Ittii Fayyaddam", "Kartaa", "Jijjirra Maqaa", "Dangaa", "Mana Murttii", "Liqii Bankii"], index=["Ittii Fayyaddam", "Kartaa", "Jijjirra Maqaa", "Dangaa", "Mana Murttii", "Liqii Bankii"].index(df.at[idx, 'Gosa']))
                    new_kf = col2.number_input("Kafaltii Sirreessi", value=float(df.at[idx, 'Kafaltii']))
                    
                    btn1, btn2 = st.columns(2)
                    if btn1.button("💾 FOOYYEESSI"):
                        df.at[idx, 'Araddaa'] = new_ar
                        df.at[idx, 'Gosa'] = new_gs
                        df.at[idx, 'Kafaltii'] = new_kf
                        save_data(df)
                        st.success("Sirreeffamni milkaa'eera!")
                        st.rerun()
                    
                    if btn2.button("🗑️ HAQI (DELETE)", type="secondary"):
                        df = df.drop(idx)
                        save_data(df)
                        st.warning("Galmeen sun haqameera!")
                        st.rerun()

    # --- REPORTS & CERTIFICATES (Same as previous v3.6 logic) ---
    elif choice == "📊 Gabaasa Telegr_Pro":
        st.dataframe(df)
        if st.button("🚀 GABAASA ERGI"):
            msg = f"📊 *GABAASA DADAR*\n👤 Namoota: {len(df)}\n💰 Galii: {pd.to_numeric(df['Kafaltii'], errors='coerce').sum():,.2f} ETB"
            requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage", data={"chat_id": TELEGRAM_CHAT_ID, "text": msg, "parse_mode": "Markdown"})
            st.success("Ergameera!")

    elif choice == "🏆 Sartiifiketa":
        if not df.empty:
            counts = df['Ogeessa'].value_counts()
            if not counts.empty:
                w_name = counts.idxmax()
                st.success(f"🏆 Ogeessa Waggaa: {w_name}")
                if st.button("📜 SARTIIFIKETA QOPHEESSI"):
                    cert = generate_certificate(w_name, counts.max(), datetime.now().year)
                    st.download_button("📥 Buufadhu (PDF)", cert, f"Cert_{w_name}.pdf")

    elif choice == "🚪 Logout":
        st.session_state.logged_in = False
        st.rerun()
