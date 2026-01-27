import streamlit as st
import pandas as pd
import os
import requests
from datetime import datetime
import plotly.express as px

# ================= 1. CONFIGURATION =================
# Folder 'Adiaan' jedhu uumi, suuraa logo.png jedhu keessa galchi
LOGO_PATH = "Adiaan/logo.png" 
DATA_FILE = "dadar_final_report.txt"
BOT_TOKEN = "8357193631:AAHCuSnXzjZTQaglkmcS0gq-EvqnkIQLDBI"
CHAT_ID_MANAGER = "7329587700"
COL_NAMES = ['Guyyaa', 'Maqaa_Abbaa_Dhimmaa', 'Araddaa', 'Qaxana', 'Gosa_Tajajjilaa', 'Maqaa_Ogeessa', 'Kafaltii_Taj']

# ================= 2. FUNCTIONS =================
def send_telegram(msg):
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        params = {"chat_id": CHAT_ID_MANAGER, "text": msg, "parse_mode": "Markdown"}
        requests.get(url, params=params)
    except: pass

def load_data():
    if not os.path.exists(DATA_FILE) or os.stat(DATA_FILE).st_size == 0:
        return pd.DataFrame(columns=COL_NAMES)
    df = pd.read_csv(DATA_FILE, sep="|", names=COL_NAMES, header=None, encoding='utf-8')
    df['Kafaltii_Taj'] = pd.to_numeric(df['Kafaltii_Taj'], errors='coerce').fillna(0)
    return df

def save_data(df_to_save):
    df_to_save[COL_NAMES].to_csv(DATA_FILE, sep="|", index=False, header=False, encoding="utf-8")

# ================= 3. UI SETUP =================
st.set_page_config(page_title="Dadar Land Admin", page_icon="🏢", layout="wide")

# Logo Sidebar irratti agarsiisuu
with st.sidebar:
    if os.path.exists(LOGO_PATH):
        st.image(LOGO_PATH, use_container_width=True)
    else:
        st.warning("Logo.png hin argamne! Folder 'Adiaan' keessa galchi.")
    
    st.divider()
    menu = st.radio("FILANNOO", ["📊 Dashboard", "📝 Galmee Haaraa", "📈 Gabaasa", "Logout"])

# ================= 4. APP LOGIC =================
if 'logged_in' not in st.session_state: st.session_state.logged_in = False

if not st.session_state.logged_in:
    # --- LOGIN PAGE ---
    _, col, _ = st.columns([1, 1, 1])
    with col:
        if os.path.exists(LOGO_PATH):
            st.image(LOGO_PATH, width=150)
        st.title("🔐 Login")
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")
        if st.button("Seeni", use_container_width=True):
            if u == "DAD" and p == "2026":
                st.session_state.logged_in = True
                st.rerun()
            else: st.error("Dogoggora!")
else:
    df = load_data()
    
    if menu == "Logout":
        st.session_state.logged_in = False
        st.rerun()

    elif menu == "📝 Galmee Haaraa":
        st.title("📝 Galmee Tajaajilaa")
        
        SERVICE_STRUCTURE = {
            "🏷 Gibira & Kaffaltii": ["Gibira Baaxii Gooroo", "Gibira Lafa Qonnaa", "Kaffaltii Liizii Waggaa", "TOT"],
            "📜 Kaartaa & Qabiyyee": ["Kaartaa Haaraa", "Kaartaa Bakka Bu'aa", "Jijjiirraa Maqaa"],
            "🏗 Pilaanii & Ijaarsa": ["Pilaanii Magaalaa", "Itti Fayyadama Lafaa"],
            "⚖️ Adabbii & Seeressuu": ["Adabbii Ijaarsaa", "Kaffaltii Seeressuu"],
        }
        
        selected_cats = st.multiselect("Ramaddii Tajaajilaa:", list(SERVICE_STRUCTURE.keys()))
        
        with st.form("reg_form"):
            c1, c2 = st.columns(2)
            name = c1.text_input("Maqaa Abbaa Dhimmaa")
            ara = c2.text_input("Araddaa")
            ogeessa = c1.text_input("Ogeessa Raawwate")
            
            total_fee = 0
            final_services = []
            
            if selected_cats:
                for cat in selected_cats:
                    st.write(f"**{cat}**")
                    subs = st.multiselect(f"Gosa {cat}:", SERVICE_STRUCTURE[cat], key=f"s_{cat}")
                    if subs:
                        sub_cols = st.columns(len(subs))
                        for idx, s in enumerate(subs):
                            with sub_cols[idx]:
                                fee = st.number_input(f"Gatii {s}", min_value=0.0, key=f"f_{s}")
                                total_fee += fee
                                final_services.append(s)
            
            st.info(f"💰 Waliigala: {total_fee:,.2f} ETB")
            
            if st.form_submit_button("💾 GALMEESSI"):
                if name and final_services:
                    new_row = [datetime.now().strftime('%d/%m/%Y'), name, ara, "-", ", ".join(final_services), ogeessa, total_fee]
                    df = pd.concat([df, pd.DataFrame([new_row], columns=COL_NAMES)], ignore_index=True)
                    save_data(df)
                    
                    msg = f"🔔 *Galmee Haaraa*\n👤 {name}\n💰 {total_fee} ETB"
                    send_telegram(msg)
                    st.success("Galmeeffameera!")
                    st.balloons()

    elif menu == "📊 Dashboard":
        st.title("📊 Dashboard")
        if not df.empty:
            st.metric("💰 Galii Waliigalaa", f"{df['Kafaltii_Taj'].sum():,.2f} ETB")
            st.plotly_chart(px.bar(df, x='Guyyaa', y='Kafaltii_Taj', title="Kaffaltii Guyyaatti"))
        else: st.info("Ragaan hin jiru.")

    elif menu == "📈 Gabaasa":
        st.title("📈 Gabaasa Bal'aa")
        st.dataframe(df, use_container_width=True)
