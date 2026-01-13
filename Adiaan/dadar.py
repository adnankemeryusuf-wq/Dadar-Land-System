import streamlit as st
import os
import pandas as pd
import requests
import io
from datetime import datetime
from fpdf import FPDF

# --- 1. QINDAYYII BU'URAA ---
st.set_page_config(page_title="Dadar Land Admin Pro", layout="wide", page_icon="🏢")

USER_NAME = "Lafa"
PASS_WORD = "1234"
DATA_FILE = "dadar_final_report.txt"
LOGO_FILE = "logo.png"

# Tarree ragaa (11 Columns) - Kan sirreeffame
COL_NAMES = ['Yeroo', 'Maqaa', 'Araddaa', 'Qaxana', 'Gosa', 'Ogeessa', 'Kafaltii_Taj', 'Kafaltii_Wal', 'C1', 'C2', 'C3']

# Telegram API
TELEGRAM_TOKEN = "8357193631:AAHCuSnXzjZTQaglkmcS0gq-EvqnkIQLDBI"
TELEGRAM_CHAT_ID = "7329587700"

# --- 2. FUNKSHINOOTA (DATA & LOGIC) ---
def load_data():
    if not os.path.exists(DATA_FILE) or os.stat(DATA_FILE).st_size == 0:
        return pd.DataFrame(columns=COL_NAMES)
    try:
        df = pd.read_csv(DATA_FILE, sep="|", names=COL_NAMES, header=None, on_bad_lines='skip', encoding='utf-8')
        return df
    except:
        return pd.DataFrame(columns=COL_NAMES)

def save_data(df):
    df.to_csv(DATA_FILE, sep="|", index=False, header=False, encoding="utf-8")

# --- 3. REPORT GENERATORS ---
def create_excel(df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Gabaasa_Dadar')
    return output.getvalue()

def create_pdf_report(df):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, "GABAASA WAAJJIRA LAFAA MAGAALAA DADAR", ln=True, align='C')
    pdf.set_font("Arial", '', 10)
    pdf.cell(0, 10, f"Guyyaa: {datetime.now().strftime('%Y-%m-%d')}", ln=True, align='R')
    pdf.ln(5)
    
    # Table Header
    pdf.set_fill_color(200, 220, 255)
    pdf.set_font("Arial", 'B', 9)
    h = ["Maqaa", "Araddaa", "Gosa", "K.Taj", "K.Wal"]
    for col in h:
        pdf.cell(38, 8, col, 1, 0, 'C', True)
    pdf.ln()

    pdf.set_font("Arial", '', 8)
    for _, row in df.iterrows():
        pdf.cell(38, 7, str(row['Maqaa'])[:18], 1)
        pdf.cell(38, 7, str(row['Araddaa']), 1)
        pdf.cell(38, 7, str(row['Gosa']), 1)
        pdf.cell(38, 7, str(row['Kafaltii_Taj']), 1)
        pdf.cell(38, 7, str(row['Kafaltii_Wal']), 1, 1)
    
    return pdf.output(dest='S').encode('latin-1')

# --- 4. SARTIIFIKETA (Professional) ---
def generate_certificate(expert_name, total_served):
    pdf = FPDF(orientation='L', unit='mm', format='A4')
    pdf.add_page()
    pdf.set_line_width(2); pdf.set_draw_color(184, 134, 11)
    pdf.rect(5, 5, 287, 200) # Border
    
    if os.path.exists(LOGO_FILE): pdf.image(LOGO_FILE, x=130, y=10, w=35)
    
    pdf.ln(35)
    pdf.set_font('Times', 'B', 40); pdf.set_text_color(30, 58, 138)
    pdf.cell(0, 20, "SARTIIFIKETA BEEKAMTII", ln=True, align='C')
    
    pdf.ln(5); pdf.set_font('Arial', 'I', 16); pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 10, "Waajjira Lafaa Bulchiinsa Magaalaa Dadar", ln=True, align='C')
    
    pdf.ln(10); pdf.set_font('Arial', '', 20)
    pdf.cell(0, 10, "Gootummaa Hojii Waggaa kan kennameef:", ln=True, align='C')
    
    pdf.ln(5); pdf.set_font('Times', 'B', 32); pdf.set_text_color(21, 128, 61)
    pdf.cell(0, 15, f"Obbo/Adde: {expert_name.upper()}", ln=True, align='C')
    
    pdf.ln(10); pdf.set_font('Arial', '', 14); pdf.set_text_color(60, 60, 60)
    msg = (f"Waggaa kanatti tajaajila saffisaa, iftoomina qabuu fi amannamaa ta'een Abbootii Dhimmaa {total_served} "
           "tajaajiluun bu'aa qabeessa ta'anii waan argamaniif beekamtii kanaan badhaafamaniiru.")
    pdf.multi_cell(0, 10, msg, align='C')
    
    # Signature Section
    pdf.set_y(172)
    pdf.set_font('Arial', 'B', 12); pdf.set_text_color(0, 0, 0)
    pdf.cell(100, 8, "__________________________", ln=0, align='C')
    pdf.cell(87, 8, "", ln=0)
    pdf.cell(100, 8, "__________________________", ln=1, align='C')
    pdf.cell(100, 5, "Aqiil Abdujaaliil", ln=0, align='C')
    pdf.cell(87, 5, "", ln=0)
    pdf.cell(100, 5, datetime.now().strftime("%d/%m/%Y"), ln=1, align='C')
    pdf.set_font('Arial', '', 10)
    pdf.cell(100, 5, "Itti Gaafatamaa Waajjiraa", ln=0, align='C')
    pdf.cell(87, 5, "", ln=0)
    pdf.cell(100, 5, "Guyyaa", ln=1, align='C')
    
    return pdf.output(dest='S').encode('latin-1')

# --- 5. MAIN APP UI ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    _, col_mid, _ = st.columns([1, 1.2, 1])
    with col_mid:
        st.markdown("<h2 style='text-align:center;'>🏢 Dadar Land Login</h2>", unsafe_allow_html=True)
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")
        if st.button("SEENI", use_container_width=True):
            if u == USER_NAME and p == PASS_WORD:
                st.session_state.logged_in = True
                st.rerun()
            else: st.error("Maqaa ykn Password dogoggora!")
else:
    # Sidebar Navigation
    with st.sidebar:
        st.image("https://cdn-icons-png.flaticon.com/512/609/609803.png", width=100)
        st.title("Admin Menu")
        menu = ["🏠 Dashboard", "📝 Galmee Haaraa", "🔍 Barbaaduu & Sirreessu", "📊 Gabaasa Telegr_Pro", "🏆 Sartiifiketa", "🚪 Logout"]
        choice = st.selectbox("Filannoowwan", menu)

    df = load_data()

    # --- PAGE: DASHBOARD ---
    if choice == "🏠 Dashboard":
        st.header("Dashboard - Gabaasa Gabaabaa")
        if not df.empty:
            c1, c2, c3 = st.columns(3)
            c1.metric("Waligala Galmee", len(df))
            # Convert to numeric to sum
            df['Kafaltii_Wal'] = pd.to_numeric(df['Kafaltii_Wal'], errors='coerce').fillna(0)
            c2.metric("Galii Waliigalaa", f"{df['Kafaltii_Wal'].sum():,.2f} ETB")
            c3.metric("Tajaajila Hardhaa", len(df[pd.to_datetime(df['Yeroo'], errors='coerce').dt.date == datetime.now().date()]))
            st.divider()
            st.subheader("Ragaalee dhiyoo galmeeffaman")
            st.table(df.tail(5)[['Yeroo', 'Maqaa', 'Gosa', 'Kafaltii_Wal']])
        else: st.info("Ragaan galmeeffame hin jiru.")

    # --- PAGE: REGISTRY ---
    elif choice == "📝 Galmee Haaraa":
        st.header("📝 Galmee Haaraa Galchi")
        with st.form("reg_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                ad = st.text_input("Maqaa Abbaa Dhimmaa")
                ar = st.text_input("Araddaa")
                qx = st.text_input("Qaxana")
            with col2:
                gs = st.selectbox("Gosa Tajaajilaa", ["Ittii Fayyaddam", "Kartaa", "Jijjirra Maqaa", "Dangaa", "Mana Murttii", "Liqii Bankii"])
                og = st.text_input("Maqaa Ogeessaa")
                kf_t = st.number_input("Kafaltii Tajaajilaa (ETB)", min_value=0.0)
                kf_d = st.number_input("Kafaltii Biroo (ETB)", min_value=0.0)
            
            if st.form_submit_button("✅ GALMEESSI"):
                if ad and og:
                    total = kf_t + kf_d
                    yeroo = datetime.now().strftime('%Y-%m-%d %H:%M')
                    # Record line: 11 columns
                    line = f"{yeroo}|{ad}|{ar}|{qx}|{gs}|{og}|{kf_t}|{total}|0|0|0\n"
                    with open(DATA_FILE, "a", encoding="utf-8") as f: f.write(line)
                    st.success(f"Galmeen {ad} milkaa'inaan raawwatameera!")
                    st.rerun()
                else: st.warning("Maqaa fi Ogeessa guutuu qabda!")

    # --- PAGE: SEARCH & EDIT & DELETE ---
    elif choice == "🔍 Barbaaduu & Sirreessu":
        st.header("🔍 Barbaadi, Fooyyessi ykn Haqui")
        query = st.text_input("Maqaa abbaa dhimmaa barreessi...")
        if not df.empty:
            results = df[df['Maqaa'].str.contains(query, case=False, na=False)]
            st.dataframe(results, use_container_width=True)
            
            if not results.empty:
                name_list = results['Maqaa'].tolist()
                selected_name = st.selectbox("Ragaa sirreessuuf nama filadhu:", name_list)
                idx = df[df['Maqaa'] == selected_name].index[0]
                
                with st.expander(f"🛠️ Galmee {selected_name} Sirreessi"):
                    c1, c2 = st.columns(2)
                    new_gs = c1.selectbox("Gosa Tajaajilaa Sirreessi", ["Ittii Fayyaddam", "Kartaa", "Jijjirra Maqaa", "Dangaa", "Mana Murttii", "Liqii Bankii"], key="edit_gosa")
                    new_kf = c2.number_input("Kafaltii Waliigalaa Sirreessi", value=float(df.at[idx, 'Kafaltii_Wal']))
                    
                    col_b1, col_b2 = st.columns(2)
                    if col_b1.button("💾 FOOYYEESSI", use_container_width=True):
                        df.at[idx, 'Gosa'] = new_gs
                        df.at[idx, 'Kafaltii_Wal'] = new_kf
                        save_data(df)
                        st.success("Sirreeffameera!")
                        st.rerun()
                    
                    if col_b2.button("🗑️ HAQI (DELETE)", type="primary", use_container_width=True):
                        df = df.drop(idx)
                        save_data(df)
                        st.warning("Galmeen sun guutummatti haqameera!")
                        st.rerun()

    # --- PAGE: REPORTS ---
    elif choice == "📊 Gabaasa Telegr_Pro":
        st.header("📊 Gabaasa Guutuu & Ergaa")
        if not df.empty:
            st.dataframe(df, use_container_width=True)
            c1, c2, c3 = st.columns(3)
            
            ex_data = create_excel(df)
            c1.download_button("📥 Excel Buufadhu", ex_data, "Gabaasa_Dadar.xlsx", use_container_width=True)
            
            pdf_data = create_pdf_report(df)
            c2.download_button("📥 PDF Buufadhu", pdf_data, "Gabaasa_Dadar.pdf", use_container_width=True)
            
            if c3.button("🚀 Telegram-itti Ergi", use_container_width=True):
                total_galii = pd.to_numeric(df['Kafaltii_Wal'], errors='coerce').sum()
                msg = f"📊 *GABAASA WAAJJIRA LAFAA*\n👤 Namoota: {len(df)}\n💰 Galii Waliigalaa: {total_galii:,.2f} ETB\n📅 Guyyaa: {datetime.now().strftime('%Y-%m-%d')}"
                requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage", data={"chat_id": TELEGRAM_CHAT_ID, "text": msg, "parse_mode": "Markdown"})
                st.success("Gabaasni Telegram-itti ergameera!")

    # --- PAGE: CERTIFICATE ---
    elif choice == "🏆 Sartiifiketa":
        st.header("🏆 Beekamtii Ogeessaa")
        if not df.empty:
            best_og = df['Ogeessa'].value_counts().idxmax()
            count = df['Ogeessa'].value_counts().max()
            st.success(f"Ogeessa Waggaa kan ta'e: **{best_og}** ({count} tajaajile)")
            
            if st.button("📜 SARTIIFIKETA MIIDHAGAA QOPHEESSI"):
                cert = generate_certificate(best_og, count)
                st.download_button("📥 Sartiifiketa PDF Buufadhu", cert, f"Cert_{best_og}.pdf")
        else: st.info("Ragaan hin jiru.")

    # --- LOGOUT ---
    elif choice == "🚪 Logout":
        st.session_state.logged_in = False
        st.rerun()
