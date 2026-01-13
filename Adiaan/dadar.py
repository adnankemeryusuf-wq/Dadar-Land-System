import streamlit as st
import pandas as pd
import os
import io
from datetime import datetime

# ================= 1. CONFIG & STYLING =================
st.set_page_config(page_title="Dadar Land Admin Pro", layout="wide", page_icon="🏢")

st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #e8f5e9 0%, #c8e6c9 100%); }
    [data-testid="stSidebar"] { background-color: #1b5e20 !important; }
    [data-testid="stSidebar"] * { color: #ffffff !important; }
    
    /* Gosa Tajaajilaa Filadhu - Magariisa */
    div[data-baseweb="multiselect"] {
        border: 2px solid #2e7d32 !important;
        background-color: #ffffff !important;
        border-radius: 8px !important;
    }
    span[data-baseweb="tag"] {
        background-color: #2e7d32 !important;
        color: white !important;
    }
    
    div.stForm {
        background: rgba(255, 255, 255, 0.9);
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
    "Kaartaa": ["Kaartaa mana", "Kartaa Kadastaara", "Kaartaa lafa qonna magaalaa"],
    "Dhimma Dangaa": ["Kafaltii Humna Mandisaa"],
    "Dhimma Mana Murtii": ["Ugura Mana Murtii", "Uguraa Mana Murtii Kasuu"],
    "Liqii Bankii": ["Dorkka Liqii Bankii", "Dorkkaa Liqii Bankii Kasuu"]
}

MONTH_MAP = {9: "Fulbaana", 10: "Onkololeessa", 11: "Sadaasa", 12: "Muddee", 1: "Amajjii", 2: "Guraandhala", 3: "Bitootessa", 4: "Eebila", 5: "Caamsaa", 6: "Waxabajjii", 7: "Adooleessa", 8: "Hagayya"}
WEEKDAY_MAP = {0: "Wixata", 1: "Filatama", 2: "Roobii", 3: "Kamisa", 4: "Jimmata", 5: "Sanbata", 6: "Dilbata"}

def load_data():
    if not os.path.exists(DATA_FILE) or os.stat(DATA_FILE).st_size == 0:
        return pd.DataFrame(columns=COL_NAMES)
    return pd.read_csv(DATA_FILE, sep="|", names=COL_NAMES, header=None, encoding='utf-8')

def save_data(df):
    df.to_csv(DATA_FILE, sep="|", index=False, header=False, encoding="utf-8")

# ================= 3. MAIN APP =================
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    _, col_mid, _ = st.columns([1, 1.2, 1])
    with col_mid:
        st.markdown("<h2 style='text-align:center; color:#2e7d32;'>Admin Login</h2>", unsafe_allow_html=True)
        u, p = st.text_input("Username"), st.text_input("Password", type="password")
        if st.button("Seeni"):
            if u == "admin" and p == "123":
                st.session_state.logged_in = True; st.rerun()
else:
    with st.sidebar:
        st.markdown("### 🏢 DADAR LAND ADMIN")
        menu = st.radio("FILANNOO", ["📊 Dashboard", "📝 Galmee Haaraa", "📈 Gabaasa Bal'aa", "🔍 Barbaadi", "Ba'i"])

    df = load_data()

    if menu == "📝 Galmee Haaraa":
        st.markdown("<h2 style='color: #2e7d32;'>📝 Galmee Tajaajilaa Haaraa</h2>", unsafe_allow_html=True)
        main_options = sorted(list(GATII_DICT.keys()))
        selected_main = st.multiselect("🟢 Gosa Tajaajilaa Filadhu", main_options)
        
        details_list = []
        dynamic_fees = {} 
        is_tot_selected = False

        if selected_main:
            for gosa in selected_main:
                st.markdown(f"#### 🛠️ Qindaa'ina: {gosa}")
                subs = st.multiselect(f"Filannoo {gosa}:", GATII_DICT[gosa], key=f"multi_{gosa}")
                for s in subs:
                    details_list.append(f"{gosa}({s})")
                    dynamic_fees[f"{gosa}_{s}"] = st.number_input(f"Kafaltii {s} (ETB):", min_value=0.0, key=f"fee_{gosa}_{s}")
                    if s == "TOT": is_tot_selected = True

        with st.form("entry_form", clear_on_submit=True):
            if is_tot_selected:
                st.subheader("📋 Odeeffannoo TOT (Jijjiirraa Maqaa)")
                col1, col2 = st.columns(2)
                with col1:
                    maqaa_g = st.text_input("Maqaa Gurguraa"); araddaa_g = st.text_input("Araddaa (Gurguraa)"); qaxana_g = st.text_input("Qaxana (Gurguraa)")
                with col2:
                    maqaa_b = st.text_input("Maqaa Bitataa"); araddaa_b = st.text_input("Araddaa (Bitataa)"); qaxana_b = st.text_input("Qaxana (Bitataa)")
                maqaa_final, araddaa_final, qaxana_final = f"G: {maqaa_g} / B: {maqaa_b}", f"G: {araddaa_g} / B: {araddaa_b}", f"G: {qaxana_g} / B: {qaxana_b}"
            else:
                col1, col2 = st.columns(2)
                maqaa_final, araddaa_final, qaxana_final = col1.text_input("Maqaa Abbaa Dhimmaa"), col2.text_input("Araddaa"), col1.text_input("Qaxana")
            
            ogeessa = st.text_input("Maqaa Ogeessaa")
            if st.form_submit_button("💾 Galmeessi"):
                if maqaa_final and ogeessa and details_list:
                    yeroo_now = datetime.now().strftime('%d/%m/%Y')
                    service_str = ", ".join(details_list)
                    total_sum = sum(dynamic_fees.values())
                    new_row = [yeroo_now, maqaa_final, araddaa_final, qaxana_final, service_str, ogeessa, total_sum]
                    df.loc[len(df)] = new_row
                    save_data(df); st.success(f"✅ Galmeeffameera! Galiin: {total_sum} ETB")
                else: st.error("Maaloo odeeffannoo guutuu barreessi!")

    elif menu == "📈 Gabaasa Bal'aa":
        st.header("📈 Gabaasa Calalame")
        if not df.empty:
            df['Date_Obj'] = pd.to_datetime(df['Guyyaa'], format='%d/%m/%Y')
            df['Waggaa'] = df['Date_Obj'].dt.year
            df['Ji\'a_Lakk'] = df['Date_Obj'].dt.month
            df['Ji\'a'] = df['Ji\'a_Lakk'].map(MONTH_MAP)
            df['Torbee'] = (df['Date_Obj'].dt.day - 1) // 7 + 1
            df['Kurmaana'] = (df['Ji\'a_Lakk'] - 1) // 3 + 1

            c1, c2, c3, c4 = st.columns(4)
            sel_year = c1.selectbox("Waggaa", sorted(df['Waggaa'].unique(), reverse=True))
            sel_q = c2.selectbox("Kurmaana", [1, 2, 3, 4])
            sel_month = c3.selectbox("Ji'a", list(MONTH_MAP.values()))
            sel_week = c4.selectbox("Torbee", [1, 2, 3, 4])

            f_type = st.radio("Akkaataa Gabaasaa:", ["Waggaa", "Kurmaana", "Ji'a", "Torbee"], horizontal=True)
            
            filtered_df = df[df['Waggaa'] == sel_year]
            if f_type == "Kurmaana": filtered_df = filtered_df[filtered_df['Kurmaana'] == sel_q]
            elif f_type == "Ji'a": filtered_df = filtered_df[filtered_df['Ji\'a'] == sel_month]
            elif f_type == "Torbee": filtered_df = filtered_df[(filtered_df['Ji\'a'] == sel_month) & (filtered_df['Torbee'] == sel_week)]

            st.dataframe(filtered_df[COL_NAMES], use_container_width=True)
            st.metric(f"Waliigala Galii", f"{filtered_df['Kafaltii_Taj'].sum():,.2f} ETB")

            # EXCEL EXPORT
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                filtered_df[COL_NAMES].to_excel(writer, index=False, sheet_name='Gabaasa')
            
            st.divider()
            col_d1, col_d2 = st.columns(2)
            with col_d1:
                st.download_button(label="📥 Gabaasa Excel Buufadhu", data=buffer.getvalue(), 
                                 file_name=f"Gabaasa_Dadar_{f_type}.xlsx", mime="application/vnd.ms-excel")
            with col_d2:
                st.markdown(f'<a href="https://t.me/share/url?url=Gabaasa_Dadar_Excel" target="_blank"><button style="width:100%; height:45px; background-color:#0088cc; color:white; border-radius:8px; border:none; font-weight:bold;">✈️ Telegram irratti Ergi</button></a>', unsafe_allow_html=True)

    elif menu == "📊 Dashboard":
        st.header("📊 Dashboard")
        st.dataframe(df, use_container_width=True)
        st.metric("Walitti Qaba Galii", f"{df['Kafaltii_Taj'].sum():,.2f} ETB")

    elif menu == "🔍 Barbaadi":
        st.header("🔍 Barbaadi")
        q = st.text_input("Maqaa ykn Araddaa barreessi...")
        if q:
            res = df[df['Maqaa_Abbaa_Dhimmaa'].str.contains(q, case=False, na=False) | df['Araddaa'].str.contains(q, case=False, na=False)]
            st.dataframe(res, use_container_width=True)

    elif menu == "Ba'i":
        st.session_state.logged_in = False; st.rerun()
