import streamlit as st
import pandas as pd
import os
import requests
import io
from datetime import datetime, timedelta
from fpdf import FPDF

# ================= 1. TELEGRAM CONFIG =================
BOT_TOKEN = "8357193631:AAHCuSnXzjZTQaglkmcS0gq-EvqnkIQLDBI"
CHAT_ID = "7329587700"

def send_telegram_report(title, total_money, total_people, details_text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    message = (
        f"📊 {title}\n"
        f"📅 Guyyaa: {datetime.now().strftime('%d/%m/%Y')}\n"
        f"━━━━━━━━━━━━━━━\n"
        f"👥 Maamiltoota: {total_people}\n"
        f"💰 Galii: {total_money:,.2f} ETB\n"
        f"━━━━━━━━━━━━━━━\n"
        f"📝 TARREEFFAMA:\n{details_text}\n"
        f"━━━━━━━━━━━━━━━\n"
        f"🏢 Wajjira Lafa Dadar"
    )
    try:
        requests.post(url, data={"chat_id": CHAT_ID, "text": message})
    except:
        st.error("Gabaasa Telegram irratti erguun hin danda'amne!")

# ================= 2. CORE DATA FUNCTIONS =================
DATA_FILE = "dadar_final_report.txt"
COL_NAMES = ['Guyyaa', 'Maqaa_Abbaa_Dhimmaa', 'Araddaa', 'Gosa_Tajajjilaa', 'Maqaa_Ogeessa', 'Kafaltii_Taj']

def load_data():
    if not os.path.exists(DATA_FILE) or os.stat(DATA_FILE).st_size == 0:
        return pd.DataFrame(columns=COL_NAMES)
    df = pd.read_csv(DATA_FILE, sep="|", names=COL_NAMES, header=None, encoding='utf-8')
    df['Guyyaa'] = pd.to_datetime(df['Guyyaa'], dayfirst=True)
    return df

def save_data(df_to_save):
    df_to_save.to_csv(DATA_FILE, sep="|", index=False, header=False, encoding="utf-8")

# ================= 3. APP INTERFACE =================
st.set_page_config(page_title="Dadar Land Admin", layout="wide")

if 'logged_in' not in st.session_state: st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("🔐 Login")
    u, p = st.text_input("Username"), st.text_input("Password", type="password")
    if st.button("Seeni"):
        if u == "DAD" and p == "2026":
            st.session_state.logged_in = True
            st.rerun()
else:
    df = load_data()
    
    with st.sidebar:
        st.header("🏢 DADAR ADMIN")
        menu = st.radio("FILANNOO:", 
            ["📊 Dashboard", "📝 Galmee Haaraa", "🔍 Barbaadi", "📄 Clearance", "📤 Gabaasa Telegram", "🚪 Logout"])

    # --- 1. DASHBOARD ---
    if menu == "📊 Dashboard":
        st.title("📊 Dashboard")
        c1, c2 = st.columns(2)
        c1.metric("Waliigala Galii", f"{df['Kafaltii_Taj'].sum():,.2f} ETB")
        c2.metric("Baay'ina Galmee", len(df))
        st.dataframe(df, use_container_width=True)

    # --- 2. GALMEE HAARAA ---
    elif menu == "📝 Galmee Haaraa":
        st.title("📝 Galmee Haaraa")
        with st.form("reg"):
            name = st.text_input("Maqaa Abbaa Dhimmaa")
            ara = st.text_input("Araddaa")
            gosa = st.selectbox("Gosa Tajaajilaa", ["Jijjiirraa Maqaa", "Kaartaa Haaraa", "Waraqaa Qulqullummaa", "Adabbii"])
            fee = st.number_input("Kaffaltii", min_value=0.0)
            ogeessa = st.text_input("Ogeessa")
            if st.form_submit_button("Galmeessi"):
                new_data = [[datetime.now().strftime('%d/%m/%Y'), name, ara, gosa, ogeessa, fee]]
                new_df = pd.DataFrame(new_data, columns=COL_NAMES)
                df = pd.concat([df, new_df], ignore_index=True)
                save_data(df)
                st.success("Galmeeffameera!")

    # --- 3. BARBAADI ---
    elif menu == "🔍 Barbaadi":
        st.title("🔍 Barbaadi")
        q = st.text_input("Maqaa galchi...")
        if q:
            res = df[df['Maqaa_Abbaa_Dhimmaa'].str.contains(q, case=False, na=False)]
            st.dataframe(res)

    # --- 4. CLEARANCE ---
    elif menu == "📄 Clearance":
        st.title("📄 Waraqaa Qulqullummaa")
        q = st.text_input("Maqaa Maamilaa...")
        if q:
            res = df[df['Maqaa_Abbaa_Dhimmaa'].str.contains(q, case=False, na=False)]
            for idx, row in res.iterrows():
                st.write(f"✅ {row['Maqaa_Abbaa_Dhimmaa']} - {row['Gosa_Tajajjilaa']}")
                if st.button(f"Uumi PDF ({idx})"):
                    st.info("PDF'n qophaa'eera. (Koodii PDF asitti dabalachuu dandeessa)")

    # --- 5. GABAASA TELEGRAM ---
    elif menu == "📤 Gabaasa Telegram":
        st.title("📤 Gabaasa Telegram")
        g_type = st.selectbox("Gosa Gabaasaa:", ["Guyyaa", "Torbee", "Ji'a", "Kurmaana", "Waggaa"])
        
        if st.button("🚀 Gabaasa Ergi"):
            now = datetime.now()
            if g_type == "Guyyaa":
                filtered = df[df['Guyyaa'].dt.date == now.date()]
            elif g_type == "Torbee":
                filtered = df[df['Guyyaa'] > (now - timedelta(days=7))]
            elif g_type == "Ji'a":
                filtered = df[df['Guyyaa'].dt.month == now.month]
            elif g_type == "Kurmaana":
                # Kurmaana (Quarter) 1, 2, 3, 4
                q_num = (now.month - 1) // 3 + 1
                filtered = df[(df['Guyyaa'].dt.month - 1) // 3 + 1 == q_num]
            else:
                filtered = df[df['Guyyaa'].dt.year == now.year]

            if not filtered.empty:
                total_money = filtered['Kafaltii_Taj'].sum()
                total_people = len(filtered)
                # Maqaalee fi Kaffaltii tarreessuu
                details = ""
                for i, r in filtered.iterrows():
                    details += f"• {r['Maqaa_Abbaa_Dhimmaa']}: {r['Kafaltii_Taj']} ETB\n"
                
                send_telegram_report(f"GABAASA {g_type.upper()}", total_money, total_people, details)
                st.success(f"Gabaasni {g_type} milkaa'inaan ergameera!")
            else:
                st.warning("Data'n gabaasa kanaaf ta'u hin argamne.")

    elif menu == "🚪 Logout":
        st.session_state.logged_in = False
        st.rerun()
