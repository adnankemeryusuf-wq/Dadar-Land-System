import streamlit as st
import pandas as pd
import os
import io
import requests
from datetime import datetime

# --- CONFIGURATION TELEGRAM ---
BOT_TOKEN = "8357193631:AAHCuSnXzjZTQaglkmcS0gq-EvqnkIQLDBI"
CHAT_ID_MANAGER = "7329587700"

# ================= 1. CONFIG & STYLING =================
st.set_page_config(page_title="Dadar Land Admin Pro", layout="wide", page_icon="🏢")

st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #f1f8e9 0%, #ffffff 100%); }
    [data-testid="stSidebar"] { background-color: #1b5e20 !important; }
    [data-testid="stSidebar"] * { color: #ffffff !important; }
    
    /* Login Box Styling */
    .login-box {
        background-color: white;
        padding: 40px;
        border-radius: 15px;
        border: 2px solid #2e7d32;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        max-width: 400px;
        margin: auto;
    }

    div.stForm { background: white; border-radius: 15px; padding: 25px; border: 2px solid #2e7d32; }
    .stButton>button { background: linear-gradient(90deg, #4caf50, #2e7d32); color: white; border-radius: 8px; font-weight: bold; width: 100%; height: 45px; }
    </style>
    """, unsafe_allow_html=True)

# ================= 2. DATA LOAD/SAVE =================
DATA_FILE = "dadar_final_report.txt"
COL_NAMES = ['Guyyaa', 'Maqaa_Abbaa_Dhimmaa', 'Araddaa', 'Qaxana', 'Gosa_Tajajjilaa', 'Maqaa_Ogeessa', 'Kafaltii_Taj']

GATII_DICT = {
    "Gibira": ["Gibira Baaxii Gooroo", "Gibira Lafa Qonnaa", "Gibira Manaa"],
    "Liizii": ["Liizii Waggaa", "Jijjiirraa Maqaa", "Kafaltii Liizii Duraa", "TOT"],
    "Ittii Fayyaddam": ["Hayyama Itti Fayyadama Lafaa", "Humna Mahandiisaa"],
    "Kaartaa": ["Kaartaa Manaa", "Kaartaa Kadastaara", "Kaartaa Lafa Qonna Magaalaa", "Kaartaa Haaromsuu"],
    "Dhimma Dangaa": ["Kafaltii Humna Mandisaa"],
    "Dhimma Mana Murtii": ["Ugura Mana Murtii", "Uguraa Mana Murtii Kaasuu"],
    "Liqii Bankii": ["Dorkka Liqii Bankii", "Dorkkaa Liqii Bankii Kaasuu"]
}

MONTH_ORDER = ["Fulbaana", "Onkololeessa", "Sadaasa", "Muddee", "Amajjii", "Guraandhala", "Bitootessa", "Eebila", "Caamsaa", "Waxabajjii", "Adooleessa", "Hagayya"]
MONTH_MAP = {9: "Fulbaana", 10: "Onkololeessa", 11: "Sadaasa", 12: "Muddee", 1: "Amajjii", 2: "Guraandhala", 3: "Bitootessa", 4: "Eebila", 5: "Caamsaa", 6: "Waxabajjii", 7: "Adooleessa", 8: "Hagayya"}
WEEKDAY_MAP = {0: "Wixata", 1: "Filatama", 2: "Roobii", 3: "Kamisa", 4: "Jimmata", 5: "Sanbata", 6: "Dilbata"}

def load_data():
    if not os.path.exists(DATA_FILE) or os.stat(DATA_FILE).st_size == 0:
        return pd.DataFrame(columns=COL_NAMES)
    df = pd.read_csv(DATA_FILE, sep="|", names=COL_NAMES, header=None, encoding='utf-8')
    df['Date_Obj'] = pd.to_datetime(df['Guyyaa'], format='%d/%m/%Y', errors='coerce')
    df['Waggaa'] = df['Date_Obj'].dt.year
    df['Ji\'a'] = df['Date_Obj'].dt.month.map(MONTH_MAP)
    df['Torbee'] = (df['Date_Obj'].dt.day - 1) // 7 + 1
    df['Guyyaa_Torbee'] = df['Date_Obj'].dt.dayofweek.map(WEEKDAY_MAP)
    df['Kurmaana'] = df['Date_Obj'].dt.month.apply(lambda x: 1 if x in [9,10,11,12] else (2 if x in [1,2,3] else (3 if x in [4,5,6] else 4)))
    return df

def save_data(df_to_save):
    df_to_save[COL_NAMES].to_csv(DATA_FILE, sep="|", index=False, header=False, encoding="utf-8")

def send_to_telegram(file_data, file_name, caption):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendDocument"
    files = {'document': (file_name, file_data)}
    data = {'chat_id': CHAT_ID_MANAGER, 'caption': caption}
    try: return requests.post(url, files=files, data=data).status_code == 200
    except: return False

# ================= 3. LOGIN & MAIN APP =================
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

# --- Bakka Username fi Password itti galu ---
if not st.session_state.logged_in:
    st.markdown("<br><br>", unsafe_allow_html=True)
    _, col_mid, _ = st.columns([1, 1.5, 1])
    
    with col_mid:
        st.markdown("""
            <div style="text-align: center;">
                <h1 style="color: #1b5e20;">🏢 Dadar Land System</h1>
                <p style="color: #666;">Maaloo seenuuf odeeffannoo kee galchi</p>
            </div>
        """, unsafe_allow_html=True)
        
        with st.container():
            st.markdown('<div class="login-box">', unsafe_allow_html=True)
            username = st.text_input("👤 Username", placeholder="Maqaa kee asitti galchi")
            password = st.text_input("🔑 Password", type="password", placeholder="Password asitti galchi")
            
            if st.button("SEENI (LOGIN)"):
                if username == "admin" and password == "123":
                    st.session_state.logged_in = True
                    st.success("✅ Gara sirnaatti nagaala seenaniiru!")
                    st.rerun()
                else:
                    st.error("❌ Username ykn Password dogoggora!")
            st.markdown('</div>', unsafe_allow_html=True)

# --- APP KEESSA (Yoo Login Ta'e) ---
else:
    with st.sidebar:
        st.markdown("### 🏢 DADAR LAND SYSTEM")
        st.write(f"Logged in as: **admin**")
        menu = st.sidebar.radio("FILANNOO", ["📊 Dashboard", "📝 Galmee Haaraa", "📈 Gabaasa Bal'aa", "🔍 Barbaadi/Edit", "🚪 Ba'i"])

    df = load_data()

    # --- DASHBOARD ---
    if menu == "📊 Dashboard":
        st.markdown("<h1 style='text-align: center; color: #1b5e20;'>📊 Dashboard Waliigalaa</h1>", unsafe_allow_html=True)
        if not df.empty:
            t_income = df['Kafaltii_Taj'].sum()
            t_clients = len(df)
            avg_inc = t_income / t_clients if t_clients > 0 else 0

            # Cards
            c1, c2, c3 = st.columns(3)
            c1.metric("💰 WALIIGALA GALII", f"{t_income:,.2f} ETB")
            c2.metric("👥 TAJAAJILAMTOOTA", f"{t_clients}")
            c3.metric("📈 GIDDU-GALEESSA", f"{avg_inc:,.2f} ETB")

            st.divider()
            col_l, col_r = st.columns([2, 1])
            with col_l:
                st.markdown("### 📈 Hiikkaa Galii Ji'aan")
                chart_data = df.groupby('Ji\'a')['Kafaltii_Taj'].sum().reindex(MONTH_ORDER).fillna(0)
                st.area_chart(chart_data, color="#2e7d32")
            with col_r:
                st.markdown("### 🔝 Gosa Tajaajilaa")
                top_services = df['Gosa_Tajajjilaa'].str.split(',').explode().str.strip().value_counts().head(5)
                st.bar_chart(top_services)
        else:
            st.info("Data'n Dashboard irratti mul'atu hin jiru.")

    # --- GALMEE HAARAA ---
    elif menu == "📝 Galmee Haaraa":
        st.header("📝 Galmee Tajaajilaa")
        selected_main = st.multiselect("🟢 Gosa Tajaajilaa", list(GATII_DICT.keys()))
        details, d_fees, is_tot = [], {}, False
        
        if selected_main:
            for g in selected_main:
                subs = st.multiselect(f"Filannoo {g}:", GATII_DICT[g], key=f"m_{g}")
                for s in subs:
                    details.append(f"{g}({s})")
                    d_fees[f"{g}_{s}"] = st.number_input(f"Kafaltii {s}", min_value=0.0, key=f"f_{g}_{s}")
                    if s == "TOT": is_tot = True
        
        with st.form("entry", clear_on_submit=True):
            if is_tot:
                c1, c2 = st.columns(2)
                maqaa_f = f"G: {c1.text_input('Maqaa Gurguraa')} / B: {c2.text_input('Maqaa Bitataa')}"
                ara_f = f"G: {c1.text_input('Araddaa (G)')} / B: {c2.text_input('Araddaa (B)')}"
                qax_f = f"G: {c1.text_input('Qaxana (G)')} / B: {c2.text_input('Qaxana (B)')}"
            else:
                c1, c2 = st.columns(2)
                maqaa_f, ara_f, qax_f = c1.text_input("Maqaa Abbaa Dhimmaa"), c2.text_input("Araddaa"), c1.text_input("Qaxana")
            
            ogeessa = st.text_input("Maqaa Ogeessaa")
            if st.form_submit_button("💾 Galmeessi"):
                if maqaa_f and details:
                    new = [datetime.now().strftime('%d/%m/%Y'), maqaa_f, ara_f, qax_f, ", ".join(details), ogeessa, sum(d_fees.values())]
                    df = pd.concat([df, pd.DataFrame([new], columns=COL_NAMES)], ignore_index=True)
                    save_data(df); st.success("Galmeeffameera!")
                else: st.error("Maaloo guuti!")

    # --- GABAASA ---
    elif menu == "📈 Gabaasa Bal'aa":
        st.header("📈 Gabaasa Calalame")
        if not df.empty:
            f_type = st.sidebar.radio("Calali:", ["Waggaa", "Kurmaana", "Ji'a", "Torbee"])
            sel_y = st.sidebar.selectbox("Waggaa", sorted(df['Waggaa'].dropna().unique(), reverse=True))
            filtered = df[df['Waggaa'] == sel_y]
            
            if f_type == "Kurmaana": filtered = filtered[filtered['Kurmaana'] == st.sidebar.selectbox("Q", [1,2,3,4])]
            elif f_type == "Ji'a": filtered = filtered[filtered['Ji\'a'] == st.sidebar.selectbox("Ji'a", MONTH_ORDER)]
            
            st.dataframe(filtered[COL_NAMES], use_container_width=True)
            t_f = filtered['Kafaltii_Taj'].sum()
            st.metric("Galii Filtarii", f"{t_f:,.2f} ETB")
            
            buf = io.BytesIO()
            with pd.ExcelWriter(buf, engine='xlsxwriter') as wr: filtered[COL_NAMES].to_excel(wr, index=False)
            if st.button("✈️ Telegram-itti Ergi"):
                if send_to_telegram(buf.getvalue(), "Gabaasa.xlsx", f"Gabaasa: {t_f} ETB"): st.success("Ergameera!")
        else: st.info("Data'n hin jiru.")

    # --- EDIT ---
    elif menu == "🔍 Barbaadi/Edit":
        q = st.text_input("Maqaa Barbaadi...")
        if q:
            res = df[df['Maqaa_Abbaa_Dhimmaa'].str.contains(q, case=False, na=False)]
            for idx, row in res.iterrows():
                with st.expander(f"📄 {row['Maqaa_Abbaa_Dhimmaa']}"):
                    ce1, ce2 = st.columns(2)
                    up_name = ce1.text_input("Maqaa", row['Maqaa_Abbaa_Dhimmaa'], key=f"n_{idx}")
                    up_fee = ce2.number_input("Kafaltii", float(row['Kafaltii_Taj']), key=f"f_{idx}")
                    if st.button("💾 Save", key=f"s_{idx}"):
                        df.at[idx, 'Maqaa_Abbaa_Dhimmaa'], df.at[idx, 'Kafaltii_Taj'] = up_name, up_fee
                        save_data(df); st.success("Fooyyeffameera!"); st.rerun()
                    if st.button("🗑️ Haqi", key=f"d_{idx}"):
                        df = df.drop(idx); save_data(df); st.rerun()

    # --- EXIT ---
    elif menu == "🚪 Ba'i":
        st.session_state.logged_in = False
        st.rerun()
