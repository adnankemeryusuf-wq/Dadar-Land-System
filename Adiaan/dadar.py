import streamlit as st
import pandas as pd
import os
from datetime import datetime

# ================= 1. CONFIGURATION & LOGO =================
LOGO_PATH = "Adiaan/logo.png" 
DATA_FILE = "dadar_data.csv"
UPLOAD_FOLDER = "Sanadoota_Kuufaman"

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

st.set_page_config(
    page_title="Dadar Land Admin System",
    page_icon=LOGO_PATH if os.path.exists(LOGO_PATH) else "🏢",
    layout="wide"
)

# ================= 2. STYLE (HALLUU #1B5E20) =================
st.markdown(f"""
    <style>
    .stApp {{ background-color: #f4f7f6; }}
    [data-testid="stSidebar"] {{
        background-color: #1b5e20 !important;
        border-right: 5px solid #ff0000;
    }}
    [data-testid="stSidebar"] * {{ color: white !important; }}
    h1, h2, h3 {{ color: #1b5e20 !important; font-family: 'Segoe UI', sans-serif; }}
    .stButton>button {{
        background-color: #1b5e20;
        color: white;
        border-radius: 20px;
        padding: 10px 24px;
        font-weight: bold;
    }}
    .stButton>button:hover {{ background-color: #2e7d32; color: #ffd700; border: 1px solid #ffd700; }}
    div.stForm {{ border: 2px solid #1b5e20; border-radius: 15px; background-color: white; }}
    .login-container {{ text-align: center; padding: 30px; border: 2px solid #1b5e20; border-radius: 15px; background-color: white; }}
    </style>
    """, unsafe_allow_html=True)

# ================= 3. DATA FUNCTIONS =================
def load_data():
    if os.path.exists(DATA_FILE):
        return pd.read_csv(DATA_FILE)
    return pd.DataFrame(columns=["Guyyaa", "Maqaa", "Tajaajila", "Sanada_Path"])

def save_data(df):
    df.to_csv(DATA_FILE, index=False)

# ================= 4. APP LOGIC =================
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    _, col_mid, _ = st.columns([1, 1.5, 1])
    with col_mid:
        st.markdown("<div class='login-container'>", unsafe_allow_html=True)
        if os.path.exists(LOGO_PATH): st.image(LOGO_PATH, width=150)
        st.header("Waajjira Bulchiinsa Lafa Magaalaa Dadar")
        with st.form("login_form"):
            u = st.text_input("Username")
            p = st.text_input("Password", type="password")
            if st.form_submit_button("Seeni"):
                if u == "DAD" and p == "2026":
                    st.session_state.logged_in = True
                    st.rerun()
                else: st.error("Username ykn Password dogoggora!")
        st.markdown("</div>", unsafe_allow_html=True)
else:
    df = load_data()
    with st.sidebar:
        if os.path.exists(LOGO_PATH): st.image(LOGO_PATH, width=100)
        st.markdown("### Dadar City Land Office")
        st.divider()
        menu = st.radio("FILANNOO", ["📊 Dashboard", "📝 Galmee & Scan", "🔍 Barbaadi"])
        if st.button("Ba'i"):
            st.session_state.logged_in = False
            st.rerun()

    if menu == "📊 Dashboard":
        st.title("📊 Dashboard")
        c1, c2 = st.columns(2)
        c1.metric("Waliigala Galmee", len(df))
        c2.metric("Sanadoota Kuufaman", len(os.listdir(UPLOAD_FOLDER)))
        st.dataframe(df.tail(5), use_container_width=True)

    elif menu == "📝 Galmee & Scan":
        st.header("📝 Galmee Haaraa")
        with st.form("my_form", clear_on_submit=True):
            maqaa = st.text_input("Maqaa Abbaa Dhimmaa")
            tajaajila = st.selectbox("Gosa Tajaajilaa", ["Kaartaa", "Liizii", "Gibira", "Waliigala"])
            sanada = st.file_uploader("Sanada (JPG/PDF)", type=["png", "jpg", "pdf"])
            if st.form_submit_button("💾 Save"):
                if maqaa and sanada:
                    file_path = os.path.join(UPLOAD_FOLDER, f"{maqaa}_{sanada.name}")
                    with open(file_path, "wb") as f:
                        f.write(sanada.getbuffer())
                    
                    new_data = {"Guyyaa": datetime.now().strftime("%Y-%m-%d"), "Maqaa": maqaa, "Tajaajila": tajaajila, "Sanada_Path": file_path}
                    df = pd.concat([df, pd.DataFrame([new_data])], ignore_index=True)
                    save_data(df)
                    st.success(f"Galmeen {maqaa} milkiin kuufameera!")
                else: st.error("Maaloo maqaa fi sanada guuti!")

    elif menu == "🔍 Barbaadi":
        st.header("🔍 Sanada Barbaadi")
        search = st.text_input("Maqaa maamilaa barreessi...")
        if search:
            result = df[df['Maqaa'].str.contains(search, case=False, na=False)]
            st.dataframe(result)
            for idx, row in result.iterrows():
                with open(row['Sanada_Path'], "rb") as file:
                    st.download_button(f"📥 Buufadhu: {row['Maqaa']}", file, file_name=os.path.basename(row['Sanada_Path']))
