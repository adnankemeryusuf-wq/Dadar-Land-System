import streamlit as st
import pandas as pd
import os
import io
import requests
from datetime import datetime

# ================= 1. CONFIGURATION & SETTINGS =================
BOT_TOKEN = "8357193631:AAHCuSnXzjZTQaglkmcS0gq-EvqnkIQLDBI"
CHAT_ID_MANAGER = "7329587700"
DATA_FILE = "dadar_final_report.txt"
COL_NAMES = ['Guyyaa', 'Maqaa_Abbaa_Dhimmaa', 'Araddaa', 'Qaxana', 'Gosa_Tajajjilaa', 'Maqaa_Ogeessa', 'Kafaltii_Taj']

st.set_page_config(page_title="Dadar Land Admin Pro", layout="wide", page_icon="🏢")

# Style bareedduu (Green Theme)
st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #e8f5e9 0%, #c8e6c9 100%); }
    [data-testid="stSidebar"] { background-color: #1b5e20 !important; }
    [data-testid="stSidebar"] * { color: #ffffff !important; }
    div.stForm { background: rgba(255, 255, 255, 0.9); border-radius: 15px; padding: 25px; border: 2px solid #2e7d32; }
    .stButton>button { background: linear-gradient(90deg, #4caf50, #2e7d32); color: white; border-radius: 8px; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# Gosa Tajaajilaa
GATII_DICT = {
    "Gibira": ["Gibira Baaxii Gooroo", "Gibira Lafa Qonnaa"],
    "Liizii": ["Liizii Waggaa", "Jijjiirraa Maqaa", "Kafaltii Liizii Duraa", "TOT"],
    "Ittii Fayyaddam": ["Hayyama Itti Fayyadama Lafaa", "Humna Mahandiisaa"],
    "Kaartaa": ["Kaartaa mana", "Kartaa Kadastaara", "Kaartaa lafa qonna magaalaa"],
    "Dhimma Dangaa": ["Kafaltii Humna Mandisaa"],
    "Dhimma Mana Murtii": ["Ugura Mana Murtii", "Uguraa Mana Murtii Kasuu"],
    "Liqii Bankii": ["Dorkka Liqii Bankii", "Dorkkaa Liqii Bankii Kasuu"]
}

MONTH_MAP = {9: "Fulbaana", 10: "Onkololeessa", 11: "Sadaasa", 12: "Muddee", 1: "Amajjii", 2: "Guraandhala", 3: "Bitootessa", 4: "Eebila", 5: "Caamsaa", 6: "Waxabajjii", 7: "Adooleessa", 8: "Hagayya"}
WEEKDAY_MAP = {0: "Wixata", 1: "Kibxata", 2: "Roobii", 3: "Kamisa", 4: "Jimmata", 5: "Sanbata", 6: "Dilbata"}

# ================= 2. FUNCTIONS =================

def load_data():
    if not os.path.exists(DATA_FILE) or os.stat(DATA_FILE).st_size == 0:
        return pd.DataFrame(columns=COL_NAMES)
    df = pd.read_csv(DATA_FILE, sep="|", names=COL_NAMES, header=None, encoding='utf-8')
    df['Date_Obj'] = pd.to_datetime(df['Guyyaa'], format='%d/%m/%Y', errors='coerce')
    df['Waggaa'] = df['Date_Obj'].dt.year
    df['Ji\'a_Lakk'] = df['Date_Obj'].dt.month
    df['Ji\'a'] = df['Ji\'a_Lakk'].map(MONTH_MAP)
    df['Torbee'] = (df['Date_Obj'].dt.day - 1) // 7 + 1
    df['Guyyaa_Torbee'] = df['Date_Obj'].dt.dayofweek.map(WEEKDAY_MAP)
    df['Kurmaana'] = df['Ji\'a_Lakk'].apply(lambda x: 1 if x in [9,10,11,12] else (2 if x in [1,2,3] else (3 if x in [4,5,6] else 4)))
    return df

def save_data(df_to_save):
    df_to_save[COL_NAMES].to_csv(DATA_FILE, sep="|", index=False, header=False, encoding="utf-8")

def send_to_telegram(file_data, file_name, caption):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendDocument"
    files = {'document': (file_name, file_data)}
    data = {'chat_id': CHAT_ID_MANAGER, 'caption': caption}
    try:
        response = requests.post(url, files=files, data=data)
        return response.status_code == 200
    except: return False

# ================= 3. MAIN APP LOGIC =================

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

# --- LOGIN PAGE ---
if not st.session_state.logged_in:
    _, col_mid, _ = st.columns([1, 1.2, 1])
    with col_mid:
        st.markdown("<h2 style='text-align:center;'>🏢 Admin Login</h2>", unsafe_allow_html=True)
        with st.form(key="login_unique_form"):
            u = st.text_input("Username")
            p = st.text_input("Password", type="password")
            if st.form_submit_button("Seeni"):
                if u == "admin" and p == "123":
                    st.session_state.logged_in = True
                    st.rerun()
                else:
                    st.error("Username ykn Password sirrii miti!")

# --- AUTHENTICATED APP ---
else:
    df = load_data()
    with st.sidebar:
        st.markdown("### 🏢 DADAR LAND SYSTEM")
        menu = st.radio("FILANNOO", ["📊 Dashboard", "📝 Galmee Haaraa", "📈 Gabaasa Bal'aa", "🔍 Barbaadi/Edit", "Ba'i"])

    # --- 📊 DASHBOARD ---
    if menu == "📊 Dashboard":
        st.header("📊 Dashboard Waliigalaa")
        if not df.empty:
            c1, c2, c3 = st.columns(3)
            c1.metric("💰 Waliigala Galii", f"{df['Kafaltii_Taj'].sum():,.2f} ETB")
            c2.metric("👥 Baay'ina Galmee", len(df))
            c3.metric("📅 Waggaa", datetime.now().year)
            st.divider()
            st.dataframe(df[COL_NAMES], use_container_width=True)
        else:
            st.info("Data'n galmeeffame hin jiru.")

    # --- 📝 GALMEE HAARAA ---
    elif menu == "📝 Galmee Haaraa":
        st.markdown("<h2 style='color: #2e7d32;'>📝 Galmee Tajaajilaa Haaraa</h2>", unsafe_allow_html=True)
        main_options = sorted(list(GATII_DICT.keys()))
        selected_main = st.multiselect("🟢 Gosa Tajaajilaa Filadhu", main_options)
        
        details_list, dynamic_fees = [], {}
        is_tot_selected = False

        if selected_main:
            for gosa in selected_main:
                st.markdown(f"#### 🛠 Qindaa'ina: {gosa}")
                subs = st.multiselect(f"Filannoo {gosa}:", GATII_DICT[gosa], key=f"multi_{gosa}")
                for s in subs:
                    details_list.append(f"{gosa}({s})")
                    dynamic_fees[f"{gosa}_{s}"] = st.number_input(f"Kafaltii {s} (ETB):", min_value=0.0, key=f"f_{gosa}_{s}")
                    if s == "TOT": is_tot_selected = True

        with st.form("entry_form", clear_on_submit=True):
            if is_tot_selected:
                st.subheader("📋 Odeeffannoo TOT")
                c1, c2 = st.columns(2)
                with c1:
                    m_g, a_g, q_g = st.text_input("Maqaa Gurguraa"), st.text_input("Araddaa (G)"), st.text_input("Qaxana (G)")
                with c2:
                    m_b, a_b, q_b = st.text_input("Maqaa Bitataa"), st.text_input("Araddaa (B)"), st.text_input("Qaxana (B)")
                m_final, a_final, q_final = f"G: {m_g} / B: {m_b}", f"G: {a_g} / B: {a_b}", f"G: {q_g} / B: {q_b}"
            else:
                c1, c2 = st.columns(2)
                m_final, a_final = c1.text_input("Maqaa Abbaa Dhimmaa"), c2.text_input("Araddaa")
                q_final = c1.text_input("Qaxana")
            
            ogeessa = st.text_input("Maqaa Ogeessaa")
            if st.form_submit_button("💾 Galmeessi"):
                if m_final and ogeessa and details_list:
                    new_row = [datetime.now().strftime('%d/%m/%Y'), m_final, a_final, q_final, ", ".join(details_list), ogeessa, sum(dynamic_fees.values())]
                    df = pd.concat([df, pd.DataFrame([new_row], columns=COL_NAMES)], ignore_index=True)
                    save_data(df); st.success("✅ Galmeeffameera!")
                else: st.error("Maaloo guuti!")

    # --- 📈 GABAASA BAL'AA (WITH TELEGRAM) ---
    elif menu == "📈 Gabaasa Bal'aa":
        st.header("📈 Gabaasa Calalame")
        if not df.empty:
            f_type = st.sidebar.radio("Gosa Gabaasaa:", ["Waggaa", "Kurmaana", "Ji'a", "Torbee", "Guyyaa"])
            sel_year = st.sidebar.selectbox("Waggaa", sorted(df['Waggaa'].dropna().unique(), reverse=True))
            filtered_df = df[df['Waggaa'] == sel_year]

            if f_type == "Kurmaana":
                sel_q = st.sidebar.selectbox("Kurmaana", [1, 2, 3, 4])
                filtered_df = filtered_df[filtered_df['Kurmaana'] == sel_q]
            elif f_type == "Ji'a":
                sel_m = st.sidebar.selectbox("Ji'a", list(MONTH_MAP.values()))
                filtered_df = filtered_df[filtered_df['Ji\'a'] == sel_m]
            elif f_type == "Torbee":
                sel_m = st.sidebar.selectbox("Ji'a ", list(MONTH_MAP.values()))
                sel_w = st.sidebar.selectbox("Torbee", [1, 2, 3, 4])
                filtered_df = filtered_df[(filtered_df['Ji\'a'] == sel_m) & (filtered_df['Torbee'] == sel_w)]
            elif f_type == "Guyyaa":
                sel_d = st.sidebar.selectbox("Guyyaa", ["Wixata", "Kibxata", "Roobii", "Kamisa", "Jimmata"])
                filtered_df = filtered_df[filtered_df['Guyyaa_Torbee'] == sel_d]

            st.dataframe(filtered_df[COL_NAMES], use_container_width=True)
            total = filtered_df['Kafaltii_Taj'].sum()
            st.metric(f"Galii ({f_type})", f"{total:,.2f} ETB")

            # Excel Export
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                filtered_df[COL_NAMES].to_excel(writer, index=False, sheet_name='Gabaasa')
            
            c1, c2 = st.columns(2)
            with c1: st.download_button("📥 Excel Buufadhu", buffer.getvalue(), file_name=f"Gabaasa_{f_type}.xlsx")
            with c2:
                if st.button("✈️ Telegram-itti Ergi"):
                    cap = f"📊 Gabaasa {f_type}\n💰 Galii: {total:,.2f} ETB\n📅 Guyyaa: {datetime.now().strftime('%d/%m/%Y')}"
                    if send_to_telegram(buffer.getvalue(), f"Gabaasa_{f_type}.xlsx", cap): st.success("✅ Ergameera!")
                    else: st.error("❌ Hin ergamne!")

    # --- 🔍 BARBAADI / EDIT ---
    elif menu == "🔍 Barbaadi/Edit":
        st.header("🔍 Barbaadi ykn Haqi")
        search_q = st.text_input("Maqaa barreessi...")
        if search_q:
            results = df[df['Maqaa_Abbaa_Dhimmaa'].str.contains(search_q, case=False, na=False)]
            for idx, row in results.iterrows():
                with st.expander(f"📄 {row['Maqaa_Abbaa_Dhimmaa']}"):
                    c_e, c_d = st.columns(2)
                    with c_e:
                        new_fee = st.number_input("Kafaltii Fooyyessi", float(row['Kafaltii_Taj']), key=f"ed_{idx}")
                        if st.button("💾 Save", key=f"s_{idx}"):
                            df.at[idx, 'Kafaltii_Taj'] = new_fee
                            save_data(df); st.success("Fooyyeffameera!"); st.rerun()
                    with c_d:
                        if st.button("🗑 Haqi (Delete)", key=f"d_{idx}"):
                            df = df.drop(idx); save_data(df); st.error("Haqameera!"); st.rerun()

    # --- BA'I ---
    elif menu == "Ba'i":
        st.session_state.logged_in = False
        st.rerun()
