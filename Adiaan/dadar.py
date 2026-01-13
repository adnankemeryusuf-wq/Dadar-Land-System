import streamlit as st
import pandas as pd
import os
from datetime import datetime

# ================= 1. CONFIG & STYLING =================
st.set_page_config(page_title="Dadar Land Admin Pro", layout="wide", page_icon="🏢")

st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #e8f5e9 0%, #c8e6c9 100%); }
    [data-testid="stSidebar"] { background-color: #1b5e20 !important; }
    [data-testid="stSidebar"] * { color: #ffffff !important; }
    div.stForm {
        background: rgba(255, 255, 255, 0.85);
        backdrop-filter: blur(10px);
        border-radius: 15px;
        padding: 25px;
        border: 1px solid rgba(255, 255, 255, 0.5);
    }
    .stButton>button {
        background: linear-gradient(90deg, #4caf50, #2e7d32);
        color: white; border-radius: 8px; font-weight: bold; height: 3.5em;
    }
    </style>
    """, unsafe_allow_html=True)

# ================= 2. DATA & SETTINGS =================
DATA_FILE = "dadar_final_report.txt"
COL_NAMES = ['Yeroo', 'Maqaa', 'Araddaa', 'Qaxana', 'Gosa', 'Ogeessa', 'Kafaltii_Taj']

MONTHS_OR = {
    "01": "Fulbaana", "02": "Onkololeessa", "03": "Sadaasa", "04": "Muddee",
    "05": "Amajjii", "06": "Guraandhala", "07": "Bitootessa", "08": "Eebila",
    "09": "Caamsaa", "10": "Waxabajjii", "11": "Adooleessa", "12": "Hagayya", "13": "Qaammee"
}

GATII_DICT = {
    "Dhimma Dangaa": ["Kafaltii Humna Mandisaa"],
    "Dhimma Mana Murtii": ["Kafaltii Itti Fayyadamaa"], 
    "Dorkka Liqii Bankii": 100.0, 
    "Dorkkaa Liqii Bankii Kasuu": 100.0,
    "Gibira Kaadaastara Baaxii Gooroo": 300.0,
    "Gibira Lafa Qonnaa": 100.0,
    "Ittii Fayyaddam": ["Hayyama Itti Fayyadama Lafaa", "Humna Mahandiisaa"], 
    "Kaartaa Lafa Qonna Magaalaa": 0.0, 
    "Kaartaa Mana": 0.0, 
    "Kartaa Kadastaara": 0.0, 
    "Liizii": ["Liizii Waggaa", "Jijjirraa Maqaa", "Lizii Duraa", "TOT"],
    "Ugura Mana Murtii": 50.0,
    "Uguraa Mana Murtii Kasuu": 50.0
}

def load_data():
    if not os.path.exists(DATA_FILE) or os.stat(DATA_FILE).st_size == 0:
        return pd.DataFrame(columns=COL_NAMES)
    return pd.read_csv(DATA_FILE, sep="|", names=COL_NAMES, header=None, encoding='utf-8')

def save_data(df):
    df.to_csv(DATA_FILE, sep="|", index=False, header=False, encoding="utf-8")

# ================= 4. MAIN APP =================
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    _, col_mid, _ = st.columns([1, 1.2, 1])
    with col_mid:
        u, p = st.text_input("Username"), st.text_input("Password", type="password")
        if st.button("Seeni"):
            if u == "admin" and p == "123":
                st.session_state.logged_in = True; st.rerun()
else:
    with st.sidebar:
        menu = st.radio("FILANNOO", ["📊 Dashboard", "📝 Galmee Haaraa", "🔍 Barbaadi", "Ba'i"])

    df = load_data()

    if menu == "📝 Galmee Haaraa":
        st.markdown("<h2 style='color: #2e7d32;'>📝 Galmee Tajaajilaa</h2>", unsafe_allow_html=True)
        
        main_options = sorted(list(GATII_DICT.keys()))
        selected_main = st.multiselect("Gosa Tajaajilaa Filadhu", main_options)
        
        details_list = []
        dynamic_fees = {} 

        if selected_main:
            for gosa in selected_main:
                st.markdown(f"#### 🛠️ Qindaa'ina: {gosa}")
                
                # --- Ittii Fayyaddam & Liizii (Multiselect dhuunfaa) ---
                if gosa in ["Ittii Fayyaddam", "Liizii"]:
                    subs = st.multiselect(f"Filannoo {gosa}:", GATII_DICT[gosa], key=f"multi_{gosa}")
                    for s in subs:
                        details_list.append(f"{gosa}({s})")
                        dynamic_fees[f"{gosa}_{s}"] = st.number_input(f"Kafaltii {s} (ETB):", min_value=0.0, key=f"fee_{gosa}_{s}")

                # --- Dhimma Dangaa & Mana Murtii (Filannoo tokko qofa garuu kaffaltii dhuunfaa) ---
                elif gosa in ["Dhimma Dangaa", "Dhimma Mana Murtii"]:
                    sub = st.selectbox(f"Filannoo {gosa}:", GATII_DICT[gosa], key=f"sub_{gosa}")
                    details_list.append(f"{gosa}({sub})")
                    dynamic_fees[f"{gosa}_{sub}"] = st.number_input(f"Kafaltii {sub} (ETB):", min_value=0.0, key=f"fee_{gosa}_{sub}")

                # --- Gibira ---
                elif gosa in ["Gibira Lafa Qonnaa", "Gibira Kaadaastara Baaxii Gooroo"]:
                    c1, c2, c3 = st.columns(3)
                    g = c1.selectbox("Guyyaa", [f"{i:02d}" for i in range(1, 31)], key=f"d_{gosa}")
                    j = c2.selectbox("Ji'a", list(MONTHS_OR.keys()), format_func=lambda x: f"{x}-{MONTHS_OR[x]}", key=f"m_{gosa}")
                    b = c3.selectbox("Waggaa", [str(y) for y in range(2020, 2030)], key=f"y_{gosa}")
                    details_list.append(f"{gosa}({g}/{j}/{b})")
                    dynamic_fees[f"{gosa}"] = st.number_input(f"Kafaltii {gosa} (ETB):", min_value=0.0, key=f"fee_{gosa}")

                else:
                    details_list.append(gosa)
                    dynamic_fees[gosa] = st.number_input(f"Kafaltii {gosa} (ETB):", min_value=0.0, key=f"fee_{gosa}")

        with st.form("entry_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            maqaa = col1.text_input("Maqaa Abbaa Dhimmaa Fullatti")
            araddaa = col2.text_input("Araddaa")
            qaxana = col1.text_input("Qaxana")
            ogeessa = col2.text_input("Maqaa Ogeessaa")
            
            if st.form_submit_button("💾 Galmeessi"):
                if maqaa and ogeessa and details_list:
                    yeroo_now = datetime.now().strftime('%d/%m/%Y')
                    service_str = ", ".join(details_list)
                    
                    total_sum = sum(dynamic_fees.values())
                    
                    new_row = [yeroo_now, maqaa, araddaa, qaxana, service_str, ogeessa, total_sum]
                    df.loc[len(df)] = new_row
                    save_data(df)
                    st.success(f"✅ Galmeeffameera: {maqaa} | Total: {total_sum} ETB")
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
