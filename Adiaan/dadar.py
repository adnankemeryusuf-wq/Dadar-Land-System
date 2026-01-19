import streamlit as st
import pandas as pd
import os
from datetime import datetime
from fpdf import FPDF

# ================= 1. CONFIGURATION =================
DATA_FILE = "dadar_final_report.txt"
NAGAHEE_DIR = "nagahee_scan"

if not os.path.exists(NAGAHEE_DIR):
    os.makedirs(NAGAHEE_DIR)

st.set_page_config(
    page_title="Dadar Land Administration",
    page_icon="🏢",
    layout="wide"
)

# ================= 2. STYLE (CSS) =================
# Integrated Pink (#f06292) and Clean White Theme
st.markdown(f"""
    <style>
    .stApp {{
        background-color: #f4f7f6;
    }}
    
    /* Login Box */
    .login-box {{
        background-color: white;
        padding: 35px;
        border-radius: 15px;
        border: 1px solid #e0e6e4;
        box-shadow: 0px 10px 30px rgba(0,0,0,0.08);
        margin-top: 50px;
    }}
    
    /* Sidebar */
    [data-testid="stSidebar"] {{
        background-color: #2c3e50 !important;
    }}
    [data-testid="stSidebar"] * {{
        color: white !important;
    }}

    /* Pink Themed Cards */
    .card {{
        background: white;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
        text-align: center;
        border-top: 5px solid #f06292; /* Pink Accent */
    }}
    
    /* Custom Button Style */
    div.stButton > button:first-child {{
        background-color: #f06292;
        color: white;
        border-radius: 8px;
    }}
    </style>
""", unsafe_allow_html=True)

# ================= 3. FUNCTIONS =================
COL_NAMES = ['Guyyaa', 'Maqaa_Abbaa_Dhimmaa', 'Araddaa', 'Qaxana', 'Gosa_Tajajjilaa', 'Maqaa_Ogeessa', 'Kafaltii_Taj']

@st.cache_data(ttl=60)
def load_data():
    if not os.path.exists(DATA_FILE) or os.stat(DATA_FILE).st_size == 0:
        return pd.DataFrame(columns=COL_NAMES)
    return pd.read_csv(DATA_FILE, sep="|", names=COL_NAMES, header=None, encoding='utf-8')

def save_data(df_to_save):
    df_to_save[COL_NAMES].to_csv(DATA_FILE, sep="|", index=False, header=False, encoding="utf-8")
    st.cache_data.clear()

# ================= 4. MAIN APP LOGIC =================
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

# --- LOGIN PAGE ---
if not st.session_state.logged_in:
    _, col_mid, _ = st.columns([1, 1.5, 1])
    with col_mid:
        st.markdown('<div class="login-box">', unsafe_allow_html=True)
        st.markdown("<h2 style='text-align:center; color:#2c3e50;'> Dadar Land Admin</h2>", unsafe_allow_html=True)
        with st.form("login_form"):
            u = st.text_input("Username")
            p = st.text_input("Password", type="password")
            btn = st.form_submit_button("SEENI", use_container_width=True)
            if btn:
                if u == "DAD" and p == "2026":
                    st.session_state.logged_in = True
                    st.rerun()
                else:
                    st.error("Maqaan ykn Koodiin dogoggora!")
        st.markdown('</div>', unsafe_allow_html=True)

# --- MAIN SYSTEM ---
else:
    df = load_data()
    with st.sidebar:
        st.title("Deder Land")
        menu = st.sidebar.radio("FILANNOO", ["📊 Dashboard", "📝 Galmee Haaraa", "🔍 Barbaadi/Edit"])
        st.sidebar.markdown("---")
        if st.sidebar.button("Log Out"):
            st.session_state.logged_in = False
            st.rerun()

    # --- DASHBOARD ---
    if menu == "📊 Dashboard":
        st.header("📊 Gabaasa Dashboard")
        if not df.empty:
            c1, c2, c3 = st.columns(3)
            # Ensure payments are numbers
            df['Kafaltii_Taj'] = pd.to_numeric(df['Kafaltii_Taj'], errors='coerce').fillna(0)
            
            total_money = df['Kafaltii_Taj'].sum()
            total_users = len(df)
            avg_pay = total_money / total_users if total_users > 0 else 0
            
            c1.markdown(f"<div class='card'><h3>💰 Galii Waliigalaa</h3><h2 style='color:#f06292;'>{total_money:,.2f}</h2></div>", unsafe_allow_html=True)
            c2.markdown(f"<div class='card'><h3>👥 Maamiltoota</h3><h2 style='color:#f06292;'>{total_users}</h2></div>", unsafe_allow_html=True)
            c3.markdown(f"<div class='card'><h3>📊 Giddu-galeessa</h3><h2 style='color:#f06292;'>{avg_pay:,.2f}</h2></div>", unsafe_allow_html=True)
            
            st.markdown("---")
            st.subheader("Ragaa Galmeeffame (10 dhiyoo)")
            st.dataframe(df.tail(10), use_container_width=True, hide_index=True)
        else:
            st.info("Ragaan galmeeffame hin jiru.")

    # --- REGISTRATION ---
    elif menu == "📝 Galmee Haaraa":
        st.header("📝 Galmee Haaraa Galmeessi")
        with st.form("reg_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            name = col1.text_input("Maqaa Abbaa Dhimmaa *")
            araddaa = col2.text_input("Araddaa *")
            ogeessa = col1.text_input("Maqaa Ogeessaa *")
            kaffaltii = col2.number_input("Kaffaltii (ETB)", min_value=0.0)
            tajaajila = st.text_area("Gosa Tajaajilaa")
            
            if st.form_submit_button("Galmeessi"):
                if name and araddaa and ogeessa:
                    new_data = [datetime.now().strftime('%d/%m/%Y'), name, araddaa, "-", tajaajila, ogeessa, kaffaltii]
                    df = pd.concat([df, pd.DataFrame([new_data], columns=COL_NAMES)], ignore_index=True)
                    save_data(df)
                    st.success(f"Galmeen {name} milkaa'inaan kuusameera!")
                else:
                    st.warning("Maaloo odeeffannoo guutaa!")

    # --- SEARCH & EDIT ---
    elif menu == "🔍 Barbaadi/Edit":
        st.header("🔍 Barbaadi fi Sakatta'i")
        q = st.text_input("Maqaa maamilaa barreessi...", placeholder="Fakkeenya: Alii...")
        if q:
            res = df[df['Maqaa_Abbaa_Dhimmaa'].str.contains(q, case=False, na=False)]
            if not res.empty:
                st.success(f"Ragaa {len(res)} argameera.")
                st.dataframe(res, use_container_width=True)
            else:
                st.warning("Maqaa kanaan ragaan argame hin jiru.")
