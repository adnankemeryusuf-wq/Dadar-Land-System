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
    .login-box {
        background-color: white; padding: 40px; border-radius: 15px;
        border: 2px solid #2e7d32; box-shadow: 0 10px 25px rgba(0,0,0,0.1);
        max-width: 450px; margin: auto;
    }
    .metric-card {
        background: white; padding: 20px; border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05); text-align: center;
        border-top: 5px solid #2e7d32; margin-bottom: 10px;
    }
    .stButton>button { 
        background: linear-gradient(90deg, #4caf50, #2e7d32); 
        color: white; border-radius: 8px; font-weight: bold; width: 100%; height: 45px; 
    }
    </style>
    """, unsafe_allow_html=True)

# ================= 2. DATA MANAGEMENT =================
DATA_FILE = "dadar_final_report.txt"
COL_NAMES = ['Guyyaa', 'Maqaa_Abbaa_Dhimmaa', 'Araddaa', 'Qaxana', 'Gosa_Tajajjilaa', 'Maqaa_Ogeessa', 'Kafaltii_Taj']

GATII_DICT = {
    "Gibira": ["Gibira Baaxii Gooroo", "Gibira Lafa Qonnaa"],
    "Liizii": ["Liizii Waggaa", "Jijjiirraa Maqaa", "Kafaltii Liizii Duraa", "TOT"],
    "Ittii Fayyaddam": ["Hayyama Itti Fayyadama Lafaa", "Humna Mahandiisaa"],
    "Kaartaa": ["Kaartaa Manaa", "Kaartaa Kadastaara", "Kaartaa Lafa Qonna Magaalaa", "Kaartaa Haaromsuu"],
    "Dhimma Dangaa": ["Kafaltii Humna Mandisaa"],
    "Dhimma Mana Murtii": ["Ugura Mana Murtii", "Uguraa Mana Murtii Kaasuu"],
    "Liqii Bankii": ["Dorkka Liqii Bankii", "Dorkkaa Liqii Bankii Kaasuu"]
}

MONTH_ORDER = ["Fulbaana", "Onkololeessa", "Sadaasa", "Muddee", "Amajjii", "Guraandhala", "Bitootessa", "Eebila", "Caamsaa", "Waxabajjii", "Adooleessa", "Hagayya"]
MONTH_MAP = {9: "Fulbaana", 10: "Onkololeessa", 11: "Sadaasa", 12: "Muddee", 1: "Amajjii", 2: "Guraandhala", 3: "Bitootessa", 4: "Eebila", 5: "Caamsaa", 6: "Waxabajjii", 7: "Adooleessa", 8: "Hagayya"}

def load_data():
    if not os.path.exists(DATA_FILE) or os.stat(DATA_FILE).st_size == 0:
        return pd.DataFrame(columns=COL_NAMES)
    df = pd.read_csv(DATA_FILE, sep="|", names=COL_NAMES, header=None, encoding='utf-8')
    df['Date_Obj'] = pd.to_datetime(df['Guyyaa'], format='%d/%m/%Y', errors='coerce')
    df['Waggaa'] = df['Date_Obj'].dt.year
    df['Ji\'a'] = df['Date_Obj'].dt.month.map(MONTH_MAP)
    df['Torbee'] = (df['Date_Obj'].dt.day - 1) // 7 + 1
    # Kurmaana Itoophiyaa (Ful-Mud = Q1, Amj-Bit = Q2, Eeb-Wax = Q3, Ado-Hag = Q4)
    df['Kurmaana'] = df['Date_Obj'].dt.month.apply(lambda x: 1 if x in [9,10,11,12] else (2 if x in [1,2,3] else (3 if x in [4,5,6] else 4)))
    return df

def save_data(df_to_save):
    df_to_save[COL_NAMES].to_csv(DATA_FILE, sep="|", index=False, header=False, encoding="utf-8")

# ================= 3. APP LOGIC =================
if 'logged_in' not in st.session_state: st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.markdown("<br><br>", unsafe_allow_html=True)
    _, col_mid, _ = st.columns([1, 1.5, 1])
    with col_mid:
        st.markdown('<div class="login-box">', unsafe_allow_html=True)
        st.markdown("<h2 style='text-align: center; color: #1b5e20;'>🏢 Dadar Land Login</h2>", unsafe_allow_html=True)
        u_input = st.text_input("Username")
        p_input = st.text_input("Password", type="password")
        if st.button("SEENI"):
            if u_input == "admin" and p_input == "123":
                st.session_state.logged_in = True
                st.rerun()
            else: st.error("Maaloo odeeffannoo sirrii galchi!")
        st.markdown('</div>', unsafe_allow_html=True)
else:
    with st.sidebar:
        st.markdown("### 🏢 DADAR LAND")
        menu = st.radio("FILANNOO", ["📊 Dashboard", "📝 Galmee Haaraa", "📈 Gabaasa Bal'aa", "🔍 Barbaadi/Edit", "🚪 Ba'i"])

    df = load_data()

    # --- DASHBOARD ---
    if menu == "📊 Dashboard":
        st.markdown("<h1 style='text-align: center; color: #1b5e20;'>📊 Dashboard Waliigalaa</h1>", unsafe_allow_html=True)
        if not df.empty:
            t_income = df['Kafaltii_Taj'].sum()
            t_clients = len(df)
            c1, c2, c3 = st.columns(3)
            with c1: st.markdown(f'<div class="metric-card"><small>WALIIGALA GALII</small><h2>{t_income:,.2f} ETB</h2></div>', unsafe_allow_html=True)
            with c2: st.markdown(f'<div class="metric-card"><small>TAJAAJILAMTOOTA</small><h2>{t_clients}</h2></div>', unsafe_allow_html=True)
            with c3: st.markdown(f'<div class="metric-card"><small>GIDDU-GALEESSA</small><h2>{(t_income/t_clients if t_clients > 0 else 0):,.2f}</h2></div>', unsafe_allow_html=True)
            
            chart_data = df.groupby('Ji\'a')['Kafaltii_Taj'].sum().reindex(MONTH_ORDER).fillna(0)
            st.area_chart(chart_data, color="#2e7d32")
        else: st.info("Data'n galmeeffame hin jiru.")

    # --- GABAASA (CALALII) ---
    elif menu == "📈 Gabaasa Bal'aa":
        st.markdown("<h2 style='color: #1b5e20;'>📈 Gabaasa Bal'aa fi Calalii</h2>", unsafe_allow_html=True)
        
        if not df.empty:
            # Bakka Calalii (Filtering Section)
            st.markdown("#### 🔍 Akkaataa Barbaaddeen Calali")
            col_f1, col_f2, col_f3 = st.columns(3)
            
            with col_f1:
                filter_type = st.selectbox("Gosa Calalii", ["Waliigala", "Waggaa", "Kurmaana", "Ji'a", "Torbee", "Guyyaa Addaa"])
            
            filtered_df = df.copy()
            
            if filter_type == "Waggaa":
                y = st.selectbox("Waggaa Filadhu", sorted(df['Waggaa'].unique(), reverse=True))
                filtered_df = df[df['Waggaa'] == y]
                
            elif filter_type == "Kurmaana":
                y = st.selectbox("Waggaa", sorted(df['Waggaa'].unique(), reverse=True))
                q = st.radio("Kurmaana (Q)", [1, 2, 3, 4], horizontal=True)
                filtered_df = df[(df['Waggaa'] == y) & (df['Kurmaana'] == q)]
                
            elif filter_type == "Ji'a":
                y = st.selectbox("Waggaa", sorted(df['Waggaa'].unique(), reverse=True))
                m = st.selectbox("Ji'a Filadhu", MONTH_ORDER)
                filtered_df = df[(df['Waggaa'] == y) & (df['Ji\'a'] == m)]
                
            elif filter_type == "Torbee":
                y = st.selectbox("Waggaa", sorted(df['Waggaa'].unique(), reverse=True))
                m = st.selectbox("Ji'a", MONTH_ORDER)
                w = st.slider("Torbee (1-4)", 1, 4)
                filtered_df = df[(df['Waggaa'] == y) & (df['Ji\'a'] == m) & (df['Torbee'] == w)]
                
            elif filter_type == "Guyyaa Addaa":
                d = st.date_input("Guyyaa Filadhu")
                d_str = d.strftime('%d/%m/%Y')
                filtered_df = df[df['Guyyaa'] == d_str]

            # Agarsiisa Data Calalamee
            st.divider()
            st.markdown(f"**Gabaasa {filter_type}**")
            st.dataframe(filtered_df[COL_NAMES], use_container_width=True)
            
            # Gabaasa Gabaabaa
            total_f = filtered_df['Kafaltii_Taj'].sum()
            count_f = len(filtered_df)
            
            c_res1, c_res2 = st.columns(2)
            c_res1.success(f"💰 Waliigala Galii: **{total_f:,.2f} ETB**")
            c_res2.info(f"👥 Baay'ina Tajaajilamtootaa: **{count_f}**")
            
            # Download Button
            buf = io.BytesIO()
            with pd.ExcelWriter(buf, engine='xlsxwriter') as writer:
                filtered_df[COL_NAMES].to_excel(writer, index=False, sheet_name='Gabaasa')
            
            st.download_button(
                label="📥 Gabaasa kana Excel-iin Download godhu",
                data=buf.getvalue(),
                file_name=f"Gabaasa_Dadar_{filter_type}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        else:
            st.warning("Data'n calalamu hin jiru.")

    # --- SECTIONS KAN BIROO ---
    elif menu == "📝 Galmee Haaraa":
        st.header("📝 Galmee Tajaajilaa")
        selected_main = st.multiselect("🟢 Gosa Tajaajilaa", list(GATII_DICT.keys()))
        details, d_fees = [], {}
        if selected_main:
            for g in selected_main:
                subs = st.multiselect(f"Filannoo {g}:", GATII_DICT[g], key=f"m_{g}")
                for s in subs:
                    details.append(f"{g}({s})")
                    d_fees[f"{g}_{s}"] = st.number_input(f"Kafaltii {s}", min_value=0.0, key=f"f_{g}_{s}")
        
        with st.form("entry", clear_on_submit=True):
            c1, c2 = st.columns(2)
            maqaa_f, ara_f = c1.text_input("Maqaa"), c2.text_input("Araddaa")
            qax_f, ogeessa = c1.text_input("Qaxana"), c2.text_input("Ogeessa")
            if st.form_submit_button("💾 GALMEESSI"):
                if maqaa_f and details:
                    new = [datetime.now().strftime('%d/%m/%Y'), maqaa_f, ara_f, qax_f, ", ".join(details), ogeessa, sum(d_fees.values())]
                    df = pd.concat([df, pd.DataFrame([new], columns=COL_NAMES)], ignore_index=True)
                    save_data(df); st.success("✅ Galmeeffameera!")
                else: st.error("Odeeffannoo guutuu barreessi!")

    elif menu == "🔍 Barbaadi/Edit":
        q = st.text_input("Maqaa Barbaadi...")
        if q:
            res = df[df['Maqaa_Abbaa_Dhimmaa'].str.contains(q, case=False, na=False)]
            for idx, row in res.iterrows():
                with st.expander(f"📄 {row['Maqaa_Abbaa_Dhimmaa']}"):
                    if st.button("🗑️ Haqi", key=f"d_{idx}"):
                        df = df.drop(idx); save_data(df); st.rerun()

    elif menu == "🚪 Ba'i":
        st.session_state.logged_in = False
        st.rerun()
