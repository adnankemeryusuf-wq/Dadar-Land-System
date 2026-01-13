import streamlit as st
import pandas as pd
import os
from datetime import datetime

# ================= 1. CONFIG & STYLING =================
st.set_page_config(page_title="Dadar Land Admin Pro", layout="wide", page_icon="🏢")

st.markdown("""
    <style>
    /* 1. Background guutuu */
    .stApp { background: linear-gradient(135deg, #e8f5e9 0%, #c8e6c9 100%); }
    [data-testid="stSidebar"] { background-color: #1b5e20 !important; }
    [data-testid="stSidebar"] * { color: #ffffff !important; }

    /* 2. Gosa Tajaajilaa Filadhu (The main box) */
    div[data-baseweb="multiselect"] {
        border: 2px solid #2e7d32 !important;
        background-color: #ffffff !important;
        border-radius: 8px !important;
    }

    /* 3. Filannoowwan keessaa (Selected chips/tags) */
    span[data-baseweb="tag"] {
        background-color: #2e7d32 !important;
        color: white !important;
        border-radius: 5px !important;
    }

    /* 4. Dropdown list items (Yeroo filattu kan gadi ba'u) */
    div[role="listbox"] ul li {
        background-color: #f1f8e9 !important;
        color: #1b5e20 !important;
    }
    div[role="listbox"] ul li:hover {
        background-color: #2e7d32 !important;
        color: white !important;
    }

    /* 5. Form styling */
    div.stForm {
        background: rgba(255, 255, 255, 0.9);
        border-radius: 15px;
        padding: 25px;
        border: 2px solid #2e7d32;
    }

    /* 6. Button styling */
    .stButton>button {
        background: linear-gradient(90deg, #4caf50, #2e7d32);
        color: white; border-radius: 8px; font-weight: bold; width: 100%;
    }
    </style>
    """, unsafe_allow_html=True)

# ================= 2. DATA & SETTINGS =================
DATA_FILE = "dadar_final_report.txt"
COL_NAMES = ['Lakka','Guyyaa', 'Maqaa_Abbbaa_Dhimmaa', 'Araddaa', 'Qaxana', 'Gosa_Tajaajilaa', 'Maqaa_Ogeessa', 'Kafaltii_Taj']

GATII_DICT = {
    "Gibira": ["Gibira Baaxii Gooroo", "Gibira Lafa Qonnaa"],
    "Liizii": ["Liizii Waggaa", "Jijjiirraa Maqaa", "Kafaltii Liizii Duraa", "TOT"],
    "Ittii Fayyaddam": ["Hayyama Itti Fayyadama Lafaa", "Humna Mahandiisaa"],
    "Kaartaa": ["Kaartaa mana", "Kartaa Kadastaara", "Kaartaa lafa qonna magaalaa"],
    "Dhimma Dangaa": ["Kafaltii Humna Mandisaa"],
    "Dhimma Mana Murtii": ["Ugura Mana Murtii", "Uguraa Mana Murtii Kasuu"],
    "Liqii Bankii": ["Dorkka Liqii Bankii", "Dorkkaa Liqii Bankii Kasuu"]
}

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
        menu = st.radio("FILANNOO", ["📊 Dashboard", "📝 Galmee Haaraa", "🔍 Barbaadi", "Ba'i"])

    df = load_data()

    if menu == "📝 Galmee Haaraa":
        st.markdown("<h2 style='color: #2e7d32;'>📝 Galmee Tajaajilaa</h2>", unsafe_allow_html=True)
        
        main_options = sorted(list(GATII_DICT.keys()))
        # Amma asitti bifti isaa guutummaatti magariisa
        selected_main = st.multiselect("🟢 Gosa Tajaajilaa Filadhu", main_options)
        
        details_list = []
        dynamic_fees = {} 
        is_tot_selected = False

        if selected_main:
            for gosa in selected_main:
                st.markdown(f"#### 🛠️ Qindaa'ina: {gosa}")
                # Filannoowwan gadii (Sub-options)
                subs = st.multiselect(f"Filannoo {gosa}:", GATII_DICT[gosa], key=f"multi_{gosa}")
                for s in subs:
                    details_list.append(f"{gosa}({s})")
                    dynamic_fees[f"{gosa}_{s}"] = st.number_input(f"Kafaltii {s} (ETB):", min_value=0.0, key=f"fee_{gosa}_{s}")
                    if s == "TOT":
                        is_tot_selected = True

        with st.form("entry_form", clear_on_submit=True):
            if is_tot_selected:
                st.subheader("📋 Odeeffannoo TOT (Jijjiirraa Maqaa)")
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("**👤 Nama Gurguru (Seller)**")
                    maqaa_g = st.text_input("Maqaa Gurguraa")
                    araddaa_g = st.text_input("Araddaa (Gurguraa)")
                    qaxana_g = st.text_input("Qaxana (Gurguraa)")
                with col2:
                    st.markdown("**👤 Nama Bitu (Buyer)**")
                    maqaa_b = st.text_input("Maqaa Bitataa")
                    araddaa_b = st.text_input("Araddaa (Bitataa)")
                    qaxana_b = st.text_input("Qaxana (Bitataa)")
                
                maqaa_final = f"G: {maqaa_g} / B: {maqaa_b}"
                araddaa_final = f"G: {araddaa_g} / B: {araddaa_b}"
                qaxana_final = f"G: {qaxana_g} / B: {qaxana_b}"
            else:
                col1, col2 = st.columns(2)
                maqaa_final = col1.text_input("Maqaa Abbaa Dhimmaa Fullatti")
                araddaa_final = col2.text_input("Araddaa")
                qaxana_final = col1.text_input("Qaxana")
            
            ogeessa = st.text_input("Maqaa Ogeessaa")
            
            if st.form_submit_button("💾 Galmeessi"):
                if maqaa_final and ogeessa and details_list:
                    yeroo_now = datetime.now().strftime('%d/%m/%Y')
                    service_str = ", ".join(details_list)
                    total_sum = sum(dynamic_fees.values())
                    
                    new_row = [yeroo_now, maqaa_final, araddaa_final, qaxana_final, service_str, ogeessa, total_sum]
                    df.loc[len(df)] = new_row
                    save_data(df)
                    st.success(f"✅ Galmeeffameera! Total: {total_sum} ETB")
                else: st.error("Maaloo odeeffannoo guutuu barreessi!")

    elif menu == "📊 Dashboard":
        st.header("📊 Dashboard")
        st.dataframe(df, use_container_width=True)
        st.metric("Walitti Qaba Galii", f"{df['Kafaltii_Taj'].sum():,.2f} ETB")

    elif menu == "🔍 Barbaadi":
        st.header("🔍 Barbaadi")
        q = st.text_input("Maqaa barreessi...")
        if q:
            res = df[df['Maqaa'].str.contains(q, case=False, na=False)]
            st.dataframe(res, use_container_width=True)

    elif menu == "Ba'i":
        st.session_state.logged_in = False; st.rerun()


