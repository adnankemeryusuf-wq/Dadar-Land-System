import streamlit as st
import os
import pandas as pd
import requests
import plotly.express as px
from datetime import datetime, timedelta
from fpdf import FPDF
from ethiopian_date import EthiopianDateConverter

# --- 1. QINDAA'INA BU'URAA (CONFIG) ---
st.set_page_config(page_title="Dadar Land Administration", layout="wide", page_icon="🏢")

USER_NAME = "Lafa2026"
PASS_WORD = "Dadar@2026"
DATA_FILE = "dadar_final_report.txt"

# Telegram Config (Token fi Chat ID kee)
TELEGRAM_TOKEN = "8357193631:AAHCuSnXzjZTQaglkmcS0gq-EvqnkIQLDBI"
TELEGRAM_CHAT_ID = "7329587700"

def send_telegram_msg(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "Markdown"}
    try:
        r = requests.post(url, data=payload)
        return r.status_code == 200
    except Exception:
        return False

# --- 2. MIIDHAGSITUU (PROFESSIONAL CSS) ---
st.markdown("""
    <style>
    .stApp { background-color: #f8fafc; }
    .header-box { 
        text-align: center; padding: 30px; 
        background: linear-gradient(135deg, #1e3a8a 0%, #15803d 100%); 
        color: white; border-radius: 20px; margin-bottom: 25px;
        box-shadow: 0 10px 20px rgba(0,0,0,0.1);
    }
    .metric-card {
        background: white; padding: 25px; border-radius: 15px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        border-top: 5px solid #1e3a8a;
        text-align: center; transition: 0.3s;
    }
    .metric-card:hover { transform: translateY(-5px); }
    .metric-label { color: #64748b; font-size: 1rem; font-weight: 600; }
    .metric-value { color: #1e3a8a; font-size: 2rem; font-weight: 800; }
    
    /* Login Box */
    .login-container {
        max-width: 450px; margin: auto; padding: 40px;
        background: white; border-radius: 20px;
        box-shadow: 0 15px 35px rgba(0,0,0,0.1);
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. SEENSA (AUTHENTICATION) ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.markdown('<br><br>', unsafe_allow_html=True)
    _, col, _ = st.columns([1, 1.2, 1])
    with col:
        st.markdown('<div class="login-container">', unsafe_allow_html=True)
        st.image("https://cdn-icons-png.flaticon.com/512/619/619153.png", width=80)
        st.header("Login - Dadar Land")
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")
        if st.button("SEENI"):
            if u == USER_NAME and p == PASS_WORD:
                st.session_state.logged_in = True
                st.rerun()
            else: st.error("Maqaa ykn Password dogoggora!")
        st.markdown('</div>', unsafe_allow_html=True)
else:
    # --- 4. NAVIGATION ---
    with st.sidebar:
        st.markdown("### 🏢 Bulchiinsa Lafaa")
        menu = ["🏠 Dashboard", "📝 Galmee Haaraa", "📊 Gabaasa & Telegram", "🚪 Logout"]
        choice = st.selectbox("Menu Filadhu", menu)
        st.divider()
        st.info(f"📅 Hardha: {datetime.now().strftime('%Y-%m-%d')}")

    st.markdown('<div class="header-box"><h1>Waajjira Lafaa Bulchiinsa Magaalaa Dadar</h1><p>Sistama Bulchiinsa Ragaa Ammayyaa</p></div>', unsafe_allow_html=True)

    # --- 5. PAGES ---
    
    # --- PAGE: DASHBOARD ---
    if choice == "🏠 Dashboard":
        if os.path.exists(DATA_FILE):
            df = pd.read_csv(DATA_FILE, sep="|", header=None)
            df.columns = ['Yeroo', 'Maqaa', 'Araddaa', 'Qaxana', 'Bilbila', 'Gosa', 'Ogeessa', 'Lakk_Galmee', 'Status', 'C1', 'C2', 'C3', 'Kafaltii']
            df['Kafaltii'] = pd.to_numeric(df['Kafaltii'], errors='coerce').fillna(0)
            
            # Metrics
            m1, m2, m3, m4 = st.columns(4)
            with m1: st.markdown(f'<div class="metric-card"><div class="metric-label">👥 Abbootii Dhimmaa</div><div class="metric-value">{len(df)}</div></div>', unsafe_allow_html=True)
            with m2: st.markdown(f'<div class="metric-card"><div class="metric-label">💰 Galii Waligalaa</div><div class="metric-value">{df["Kafaltii"].sum():,.0f} <small style="font-size:1rem;">ETB</small></div></div>', unsafe_allow_html=True)
            with m3: 
                ground_count = len(df[df['Gosa'] == "Ground"])
                st.markdown(f'<div class="metric-card"><div class="metric-label">🏗️ Ground Service</div><div class="metric-value">{ground_count}</div></div>', unsafe_allow_html=True)
            with m4:
                daily_count = len(df[pd.to_datetime(df['Yeroo']).dt.date == datetime.now().date()])
                st.markdown(f'<div class="metric-card"><div class="metric-label">📅 Galmee Hardhaa</div><div class="metric-value">{daily_count}</div></div>', unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)
            
            # Charts
            c1, c2 = st.columns([1.5, 1])
            with c1:
                st.subheader("📈 Gosa Tajaajilaa")
                fig = px.pie(df, names='Gosa', hole=0.4, template="plotly_white", color_discrete_sequence=px.colors.qualitative.Pastel)
                st.plotly_chart(fig, use_container_width=True)
            with c2:
                st.subheader("🕒 Galmeewwan Dhiyoo")
                st.dataframe(df[['Maqaa', 'Gosa', 'Kafaltii']].tail(8), use_container_width=True)
        else:
            st.warning("Ragaan galmaa'e hin jiru.")

    # --- PAGE: GALMEE HAARAA ---
    elif choice == "📝 Galmee Haaraa":
        with st.form("form_registration", clear_on_submit=True):
            st.subheader("📝 Ragaa Abbaa Dhimmaa Galmeessi")
            col1, col2 = st.columns(2)
            with col1:
                ad = st.text_input("👤 Maqaa Abbaa Dhimmaa")
                ar = st.text_input("📍 Araddaa")
                qx = st.text_input("🔢 Qaxana / Lakk. Manaa")
                bl = st.text_input("📞 Lakkoofsa Bilbilaa")
            with col2:
                gs = st.selectbox("🛠️ Gosa Tajaajilaa", ["Kartaa", "Jij_Maqaa", "Lizi", "TOT", "Ground", "Gibira"])
                og = st.text_input("👨‍💼 Maqaa Ogeessa Tajaajila Kennu")
                lk = st.text_input("🆔 Reference / Lakk. Galmee")
                k_wal = st.number_input("💵 Kafaltii Waligalaa (ETB)", min_value=0.0)
            
            if st.form_submit_button("✅ GALMEE MIRKANEEESSI"):
                if ad and ar and bl:
                    now = datetime.now().strftime("%Y-%m-%d %H:%M")
                    line = f"{now}|{ad}|{ar}|{qx}|{bl}|{gs}|{og}|{lk}|Hardha|0|0|0|{k_wal}\n"
                    with open(DATA_FILE, "a", encoding="utf-8") as f:
                        f.write(line)
                    st.success(f"Ragaan '{ad}' milkiin galmaa'eera!")
                    st.balloons()
                else:
                    st.error("Maaloo ragaalee barbaachisoo (Maqaa, Araddaa, Bilbila) guuti!")

    # --- PAGE: GABAASA & TELEGRAM ---
    elif choice == "📊 Gabaasa & Telegram":
        st.subheader("📊 To'annoo fi Gabaasa Yeroo")
        if os.path.exists(DATA_FILE):
            df = pd.read_csv(DATA_FILE, sep="|", header=None)
            df.columns = ['Yeroo', 'Maqaa', 'Araddaa', 'Qaxana', 'Bilbila', 'Gosa', 'Ogeessa', 'Lakk_Galmee', 'Status', 'C1', 'C2', 'C3', 'Kafaltii']
            df['Yeroo'] = pd.to_datetime(df['Yeroo'])
            df['Kafaltii'] = pd.to_numeric(df['Kafaltii'], errors='coerce').fillna(0)

            # Time Filters
            yeroo_radio = st.radio("Filtara Yeroo:", ["Hunda", "Hardha", "Torban", "Ji'a", "Kurmaana", "Waggaa"], horizontal=True)
            
            now = datetime.now()
            if yeroo_radio == "Hardha": df_f = df[df['Yeroo'].dt.date == now.date()]
            elif yeroo_radio == "Torban": df_f = df[df['Yeroo'] >= (now - timedelta(days=7))]
            elif yeroo_radio == "Ji'a": df_f = df[df['Yeroo'].dt.month == now.month]
            elif yeroo_radio == "Kurmaana": df_f = df[df['Yeroo'] >= (now - timedelta(days=90))]
            elif yeroo_radio == "Waggaa": df_f = df[df['Yeroo'].dt.year == now.year]
            else: df_f = df

            st.dataframe(df_f, use_container_width=True)

            # Telegram & Download
            c1, c2 = st.columns(2)
            with c1:
                if st.button("🚀 GABAASA FILATAME TELEGRAM-ITTI ERGI"):
                    t_cust = len(df_f)
                    t_money = df_f['Kafaltii'].sum()
                    t_ground = len(df_f[df_f['Gosa'] == "Ground"])
                    
                    msg = (f"📊 *Gabaasa Waajjira Lafaa Dadar*\n"
                           f"━━━━━━━━━━━━━━━━━━\n"
                           f"📅 Yeroo: *{yeroo_radio}*\n"
                           f"👤 Abbootii Dhimmaa: `{t_cust}`\n"
                           f"🏗️ Tajaajila Ground: `{t_ground}`\n"
                           f"💰 Galii Waligalaa: *{t_money:,.2f} ETB*\n"
                           f"━━━━━━━━━━━━━━━━━━\n"
                           f"🕒 Ergame: {now.strftime('%Y-%m-%d %H:%M')}")
                    
                    if send_telegram_msg(msg): st.success("Gabaasni Telegram-itti ergameera!")
                    else: st.error("Erguun hin danda'amne!")
            
            with c2:
                csv = df_f.to_csv(index=False).encode('utf-8')
                st.download_button("📥 EXCEL BUUFADHU (CSV)", csv, f"gabaasa_{yeroo_radio}.csv", "text/csv")
        else:
            st.info("Ragaan gabaasni irraa hojjetamu hin jiru.")

    # --- LOGOUT ---
    elif choice == "🚪 Logout":
        st.session_state.logged_in = False
        st.rerun()
