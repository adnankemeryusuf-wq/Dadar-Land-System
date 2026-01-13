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
    
    /* Metric Card Styling */
    .metric-card {
        background-color: #ffffff;
        border-left: 5px solid #2e7d32;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.1);
    }
    
    div.stForm {
        background: white;
        border-radius: 15px;
        padding: 25px;
        border: 2px solid #2e7d32;
    }
    
    .stButton>button {
        background: linear-gradient(90deg, #4caf50, #2e7d32);
        color: white; border-radius: 8px; font-weight: bold; width: 100%;
    }
    </style>
    """, unsafe_allow_html=True)

# ================= 2. DATA & SETTINGS =================
DATA_FILE = "dadar_final_report.txt"
COL_NAMES = ['Guyyaa', 'Maqaa_Abbaa_Dhimmaa', 'Araddaa', 'Qaxana', 'Gosa_Tajajjilaa', 'Maqaa_Ogeessa', 'Kafaltii_Taj']

GATII_DICT = {
    "Gibira": ["Gibira Baaxii Gooroo", "Gibira Lafa Qonnaa"],
    "Liizii": ["Liizii Waggaa", "Jijjiirraa Maqaa", "Kafaltii Liizii Duraa", "TOT"],
    "Ittii Fayyaddam": ["Hayyama Itti Fayyadama Lafaa", "Humna Mahandiisaa"],
    "Kaartaa": ["Kaartaa mana", "Kartaa Kadastaara", "Kaartaa lafa qonna magaalaa"]
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

# ================= 3. APP LOGIC =================
if 'logged_in' not in st.session_state: st.session_state.logged_in = False

if not st.session_state.logged_in:
    _, col_mid, _ = st.columns([1, 1.2, 1])
    with col_mid:
        st.markdown("<h2 style='text-align:center;'>🏢 Dadar Admin Login</h2>", unsafe_allow_html=True)
        u, p = st.text_input("Username"), st.text_input("Password", type="password")
        if st.button("Seeni"):
            if u == "admin" and p == "123":
                st.session_state.logged_in = True; st.rerun()
else:
    with st.sidebar:
        st.markdown("### 🏢 DADAR LAND")
        menu = st.radio("FILANNOO", ["📊 Dashboard", "📝 Galmee Haaraa", "📈 Gabaasa Bal'aa", "🔍 Barbaadi/Edit", "Ba'i"])

    df = load_data()

    # --- DASHBOARD ---
    if menu == "📊 Dashboard":
        st.markdown("<h2 style='color:#1b5e20;'>📊 Dashboard Waliigalaa</h2>", unsafe_allow_html=True)
        if not df.empty:
            total_income = df['Kafaltii_Taj'].sum()
            total_clients = len(df)
            
            # Top Metrics
            m1, m2, m3 = st.columns(3)
            m1.metric("💰 Waliigala Galii", f"{total_income:,.2f} ETB")
            m2.metric("👥 Tajaajilamtoota", f"{total_clients}")
            m3.metric("📈 Giddu-galeessa", f"{(total_income/total_clients):,.2f} ETB")
            
            st.divider()
            
            # Chart Section
            c_left, c_right = st.columns([2, 1])
            with c_left:
                st.markdown("### 📈 Galiin Ji'a Ji'aan")
                chart_data = df.groupby('Ji\'a')['Kafaltii_Taj'].sum().reindex(MONTH_ORDER).fillna(0)
                st.bar_chart(chart_data)
                

            with c_right:
                st.markdown("### 🏢 Top Araddaa")
                top_ar = df.groupby('Araddaa')['Kafaltii_Taj'].sum().sort_values(ascending=False).head(5)
                st.dataframe(top_ar)
        else:
            st.info("Data'n Dashboard irratti mul'atu hin jiru.")

    # --- GALMEE HAARAA ---
    elif menu == "📝 Galmee Haaraa":
        st.header("📝 Galmee Haaraa")
        selected_main = st.multiselect("🟢 Gosa Tajaajilaa", list(GATII_DICT.keys()))
        details_list, dynamic_fees, is_tot = [], {}, False
        
        if selected_main:
            for g in selected_main:
                subs = st.multiselect(f"Filannoo {g}:", GATII_DICT[g], key=f"s_{g}")
                for s in subs:
                    details_list.append(f"{g}({s})")
                    dynamic_fees[f"{g}_{s}"] = st.number_input(f"Kafaltii {s}", min_value=0.0, key=f"f_{g}_{s}")
                    if s == "TOT": is_tot = True
        
        with st.form("entry"):
            if is_tot:
                c1, c2 = st.columns(2)
                maqaa_f = f"G: {c1.text_input('Maqaa Gurguraa')} / B: {c2.text_input('Maqaa Bitataa')}"
                ara_f = f"G: {c1.text_input('Araddaa (G)')} / B: {c2.text_input('Araddaa (B)')}"
                qax_f = f"G: {c1.text_input('Qaxana (G)')} / B: {c2.text_input('Qaxana (B)')}"
            else:
                c1, c2 = st.columns(2)
                maqaa_f, ara_f, qax_f = c1.text_input("Maqaa Fullatti"), c2.text_input("Araddaa"), c1.text_input("Qaxana")
            
            ogeessa = st.text_input("Maqaa Ogeessaa")
            if st.form_submit_button("💾 Galmeessi"):
                if maqaa_f and details_list:
                    new_row = [datetime.now().strftime('%d/%m/%Y'), maqaa_f, ara_f, qax_f, ", ".join(details_list), ogeessa, sum(dynamic_fees.values())]
                    df = pd.concat([df, pd.DataFrame([new_row], columns=COL_NAMES)], ignore_index=True)
                    save_data(df); st.success("Galmeeffameera!")
                else: st.error("Maaloo odeeffannoo guuti.")

    # --- GABAASA BAL'AA ---
    elif menu == "📈 Gabaasa Bal'aa":
        st.header("📈 Gabaasa")
        if not df.empty:
            f_type = st.sidebar.radio("Filter:", ["Waggaa", "Kurmaana", "Ji'a", "Torbee"])
            sel_y = st.sidebar.selectbox("Waggaa", sorted(df['Waggaa'].dropna().unique(), reverse=True))
            filtered = df[df['Waggaa'] == sel_y]
            
            if f_type == "Kurmaana": filtered = filtered[filtered['Kurmaana'] == st.sidebar.selectbox("Q", [1,2,3,4])]
            elif f_type == "Ji'a": filtered = filtered[filtered['Ji\'a'] == st.sidebar.selectbox("Ji'a", MONTH_ORDER)]
            
            st.dataframe(filtered[COL_NAMES], use_container_width=True)
            total = filtered['Kafaltii_Taj'].sum()
            st.metric("Galii Filtarii", f"{total:,.2f} ETB")
            
            buf = io.BytesIO()
            with pd.ExcelWriter(buf, engine='xlsxwriter') as wr: filtered[COL_NAMES].to_excel(wr, index=False)
            
            c1, c2 = st.columns(2)
            c1.download_button("📥 Excel Download", buf.getvalue(), "Gabaasa.xlsx")
            if c2.button("✈️ Telegram-itti Ergi"):
                if send_to_telegram(buf.getvalue(), "Gabaasa.xlsx", f"📊 Gabaasa Galii: {total:,.2f} ETB"): st.success("Ergameera!")
        else: st.info("Data'n hin jiru.")

    # --- EDIT / DELETE ---
    elif menu == "🔍 Barbaadi/Edit":
        q = st.text_input("Maqaa Barbaadi...")
        if q:
            res = df[df['Maqaa_Abbaa_Dhimmaa'].str.contains(q, case=False, na=False)]
            for idx, row in res.iterrows():
                with st.expander(f"📄 {row['Maqaa_Abbaa_Dhimmaa']}"):
                    c1, c2 = st.columns(2)
                    up_name = c1.text_input("Maqaa", row['Maqaa_Abbaa_Dhimmaa'], key=f"n_{idx}")
                    up_fee = c2.number_input("Kafaltii", float(row['Kafaltii_Taj']), key=f"f_{idx}")
                    if st.button("💾 Save Changes", key=f"s_{idx}"):
                        df.at[idx, 'Maqaa_Abbaa_Dhimmaa'], df.at[idx, 'Kafaltii_Taj'] = up_name, up_fee
                        save_data(df); st.success("Fooyyeffameera!"); st.rerun()
                    if st.button("🗑️ Haqi", key=f"d_{idx}"):
                        df = df.drop(idx); save_data(df); st.rerun()

    elif menu == "Ba'i": st.session_state.logged_in = False; st.rerun()
