import streamlit as st
import pandas as pd
import os
import io
import requests
from datetime import datetime
from fpdf import FPDF
import plotly.express as px
from ethiopian_date import EthiopianDateConverter

# ================= 1. CONFIGURATION & STYLE =================
# 1. Jalqaba variable kana qopheessi
LOGO_PATH = "Adiaan/logo.png"

# 2. Page config irratti variable sana fayyadami (Waraabbii malee)
st.set_page_config(
    page_title="Dadar Land Customer Registration System", 
    page_icon=LOGO_PATH if os.path.exists(LOGO_PATH) else "🏢", 
    layout="wide"
)
BOT_TOKEN = "8357193631:AAHCuSnXzjZTQaglkmcS0gq-EvqnkIQLDBI"
CHAT_ID_MANAGER = "7329587700"
LOGO_PATH = "Adiaan/logo.png"
DATA_FILE = "dadar_final_report.txt"

COL_NAMES = ['Guyyaa', 'Maqaa_Abbaa_Dhimmaa', 'Araddaa', 'Qaxana', 'Gosa_Tajajjilaa', 'Maqaa_Ogeessa', 'Kafaltii_Taj']
MONTH_ORDER = ["Fulbaana", "Onkololeessa", "Sadaasa", "Muddee", "Amajjii", "Guraandhala", "Bitootessa", "Eebila", "Caamsaa", "Waxabajjii", "Adooleessa", "Hagayya"]
MONTH_MAP = {9: "Fulbaana", 10: "Onkololeessa", 11: "Sadaasa", 12: "Muddee", 1: "Amajjii", 2: "Guraandhala", 3: "Bitootessa", 4: "Eebila", 5: "Caamsaa", 6: "Waxabajjii", 7: "Adooleessa", 8: "Hagayya"}

st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #f1f8e9 0%, #ffffff 100%); }
    [data-testid="stSidebar"] { background-color: #1b5e20 !important; }
    [data-testid="stSidebar"] * { color: #ffffff !important; }
    div.stForm { background: white; border-radius: 15px; padding: 25px; border: 2px solid #2e7d32; box-shadow: 0px 4px 15px rgba(0,0,0,0.1); }
    .card { background: white; padding: 20px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); text-align: center; border-top: 5px solid #2e7d32; margin-bottom: 10px; }
    .stButton>button { background: linear-gradient(90deg, #4caf50, #2e7d32); color: white; border-radius: 8px; font-weight: bold; width: 100%; height: 45px; border: none; }
    </style>
    """, unsafe_allow_html=True)

# ================= 2. CORE FUNCTIONS =================
def load_data():
    if not os.path.exists(DATA_FILE) or os.stat(DATA_FILE).st_size == 0:
        return pd.DataFrame(columns=COL_NAMES)
    df = pd.read_csv(DATA_FILE, sep="|", names=COL_NAMES, header=None, encoding='utf-8')
    df['Date_Obj'] = pd.to_datetime(df['Guyyaa'], format='%d/%m/%Y', errors='coerce')
    df['Waggaa'] = df['Date_Obj'].dt.year
    df['Ji\'a'] = df['Date_Obj'].dt.month.map(MONTH_MAP)
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

def create_advanced_pdf(name, count, rank, logo_left=None, logo_right=None):
    # Orientation 'L' (Landscape), A4
    pdf = FPDF(orientation='L', unit='mm', format='A4')
    pdf.add_page()
    
    # --- Halluuwwan Sadarkaatti Hunda'an ---
    if rank == 1:
        rank_color = (255, 215, 0)   # Gold
        rank_text = "1FFAA"
    elif rank == 2:
        rank_color = (192, 192, 192) # Silver
        rank_text = "2FFAA"
    else:
        rank_color = (205, 127, 50)  # Bronze
        rank_text = "3FFAA"

    deep_green = (0, 80, 0)
    bg_color = (255, 255, 255) # White background for clarity


# --- 1. Background fi Border (Dynamic Border Color) ---
    pdf.set_fill_color(*bg_color)
    pdf.rect(10, 10, 277, 190, 'F')
    
    # Border inni gubbaa (Magariisa)
    pdf.set_draw_color(*deep_green)
    pdf.set_line_width(3.0)
    pdf.rect(10, 10, 277, 190)
    
    # Border inni keessaa (Halluu Sadarkaa: Gold/Silver/Bronze)
    pdf.set_draw_color(*rank_color)
    pdf.set_line_width(1.5)
    pdf.rect(13, 13, 271, 184)

    # --- 2. Logo Handling (Safe Temporary Files) ---
    def save_temp_logo(logo_file, prefix):
        if logo_file:
            ext = logo_file.name.split('.')[-1].lower()
            temp_path = f"temp_{prefix}.{ext}"
            with open(temp_path, "wb") as f:
                f.write(logo_file.getbuffer())
            return temp_path
        return None

    path_l = save_temp_logo(logo_left, "left")
    path_r = save_temp_logo(logo_right, "right")

    if path_l: pdf.image(path_l, x=20, y=18, w=25)
    if path_r: pdf.image(path_r, x=250, y=18, w=25)

    # --- 3. Mata Duree ---
    pdf.set_y(45)
    pdf.set_text_color(*rank_color)
    pdf.set_font('Arial', 'B', 35) 
    pdf.cell(0, 15, "SARTIIFIKETA BEEKAMTII", ln=True, align='C')
    
    pdf.set_y(62)
    pdf.set_text_color(*deep_green)
    pdf.set_font('Arial', 'B', 22)
    pdf.cell(0, 12, "Waajjira Lafaa Bulchiinsa Magaalaa Dadar", ln=True, align='C')

    # --- 4. Sadarkaa fi Maqaa ---
    pdf.set_y(90)
    pdf.set_text_color(50, 50, 50)
    pdf.set_font('Arial', 'I', 18)
    pdf.cell(0, 10, f"Badhaasa Sadarkaa {rank_text} Waggaa 2026", ln=True, align='C')

    pdf.ln(5)
    pdf.set_text_color(*deep_green)
    pdf.set_font('Arial', 'B', 30) 
    pdf.cell(0, 25, f"Obbo/Adde: {name.upper()}", ln=True, align='C')

    # --- 5. Gumaacha Hojii ---
    pdf.set_y(140)
    pdf.set_text_color(60, 60, 60)
    pdf.set_font('Arial', '', 14)
    msg = f"Tajaajilamtoota {count} saffisaa fi qulqullinaan tajaajiluun gumaacha guddaa waan gumaachaniif badhaasa kanaan galateeffamaniiru."
    pdf.multi_cell(0, 10, msg, align='C')

    # --- 6. Mallattoo ---
    pdf.set_y(175)
    pdf.set_draw_color(*deep_green)
    pdf.line(40, 175, 100, 175)
    pdf.set_xy(40, 177); pdf.set_font('Arial', 'B', 12)
    pdf.cell(60, 8, "Mallattoo Itti Gaafatamaa", align='C')

    pdf.line(190, 175, 250, 175)
    pdf.set_xy(190, 177); pdf.cell(60, 8, f"Guyyaa: {datetime.now().strftime('%d/%m/%Y')}", align='C')

    return pdf.output(dest='S').encode('latin-1')
# ================= 3. MAIN APP =================
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    _, col_mid, _ = st.columns([1, 1.2, 1])
    with col_mid:
        if os.path.exists(LOGO_PATH):
            st.image(LOGO_PATH, width=100)
        st.markdown("<h2 style='text-align:center; color: #1b5e20;'>Dadar Land Administration Customer Registration System</h2>", unsafe_allow_html=True)
        with st.form("login_form"):
            st.markdown("####  Login")
            u = st.text_input("Username", placeholder="admin")
            p = st.text_input("Password", type="password", placeholder="••••••••")
            if st.form_submit_button("Seeni"):
                if u == "DAD" and p == "2026":
                    st.session_state.logged_in = True
                    st.rerun()
                else:
                    st.error("Maqaan ykn Koodiin dogoggora!")
else:
    df = load_data()
    with st.sidebar:
        if os.path.exists(LOGO_PATH): 
            st.image(LOGO_PATH, width=100)
        st.success("Deder City Land Office")
        menu = st.radio("FILANNOO", ["📊 Dashboard", "📝 Galmee Haaraa", "📈 Gabaasa Bal'aa", "🏆 Badhaasa Ogeeyyii", "🔍 Barbaadi/Edit"])
        if st.button("Log Out"):
            st.session_state.logged_in = False
            st.rerun()


    if menu == "📊 Dashboard":
        st.header("📊 Dashboard Waliigalaa")
        if not df.empty:
            c1, c2, c3 = st.columns(3)
            c1.markdown(f"<div class='card'><p>💰 Galii Waliigalaa</p><p class='metric-value'>{df['Kafaltii_Taj'].sum():,.2f} ETB</p></div>", unsafe_allow_html=True)
            c2.markdown(f"<div class='card'><p>👥 Maamiltoota</p><p class='metric-value'>{len(df)}</p></div>", unsafe_allow_html=True)
            top_og = df['Maqaa_Ogeessa'].mode()[0] if not df.empty else "-"
            c3.markdown(f"<div class='card'><p>🏆 Ogeessa Cimaa</p><p class='metric-value'>{top_og}</p></div>", unsafe_allow_html=True)
            st.area_chart(df.groupby('Ji\'a')['Kafaltii_Taj'].sum().reindex(MONTH_ORDER).fillna(0))

    elif menu == "📝 Galmee Haaraa":
        st.header("📝 Galmee Tajaajilaa")
        GATII_DICT = {"Gibira": ["Gibira Lafa Qonnaa", "Gibira Manaa"], "Liizii": ["Liizii Waggaa", "Jijjiirraa Maqaa", "TOT"]}
        
        with st.form("entry_form"):
            maqaa = st.text_input("Maqaa Abbaa Dhimmaa")
            ara = st.text_input("Araddaa")
            qax = st.text_input("Qaxana")
            ogeessa = st.text_input("Maqaa Ogeessaa")
            gosa = st.multiselect("Gosa Tajaajilaa", sum(GATII_DICT.values(), []))
            kaffaltii = st.number_input("Kaffaltii (ETB)", min_value=0.0)
            
            if st.form_submit_button("💾 Galmeessi"):
                if maqaa and ogeessa:
                    new_row = [datetime.now().strftime('%d/%m/%Y'), maqaa, ara, qax, ", ".join(gosa), ogeessa, kaffaltii]
                    df = pd.concat([df, pd.DataFrame([new_row], columns=COL_NAMES)], ignore_index=True)
                    save_data(df)
                    st.success("Galmeeffameera!")

    elif menu == "📈 Gabaasa Bal'aa":
        st.header("📈 Gabaasa Bal'aa")
        if not df.empty:
            f_type = st.selectbox("Calali:", ["Waliigala", "Waggaa", "Ji'a"])
            filtered = df.copy() # Calala dabalataa asitti galchuun ni danda'ama
            
            # Export Buttons
            st.subheader("📥 Gabaasa Buufadhu")
            ex1, ex2, ex3 = st.columns(3)
            
            # Excel
            buf_ex = io.BytesIO()
            with pd.ExcelWriter(buf_ex, engine='xlsxwriter') as writer:
                filtered[COL_NAMES].to_excel(writer, index=False)
            ex1.download_button("📊 Excel Buusi", buf_ex.getvalue(), "Gabaasa.xlsx")
            
            # PPT
            ppt_file = create_ppt_report(filtered, f_type)
            ex2.download_button("🖥️ PPT Buusi", ppt_file, "Gabaasa.pptx")
            
            st.dataframe(filtered[COL_NAMES], use_container_width=True)

    if st.sidebar.button("Log Out"):
        st.session_state.logged_in = False
        st.rerun()

