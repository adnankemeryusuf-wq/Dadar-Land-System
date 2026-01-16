import streamlit as st
import pandas as pd
import os
import io
import requests
from datetime import datetime
from fpdf import FPDF
import plotly.express as px

# ================= 1. CONFIGURATION & STYLE =================
LOGO_PATH = "Adiaan/logo.png"
NAGAHEE_DIR = "nagahee_scan"

# Folder nagahee itti kuusnu yoo hin jirre uumuuf
if not os.path.exists(NAGAHEE_DIR):
    os.makedirs(NAGAHEE_DIR)

st.set_page_config(
    page_title="Dadar Land Customer Registration System", 
    page_icon=LOGO_PATH if os.path.exists(LOGO_PATH) else "🏢", 
    layout="wide"
)

BOT_TOKEN = "8357193631:AAHCuSnXzjZTQaglkmcS0gq-EvqnkIQLDBI"
CHAT_ID_MANAGER = "7329587700"
DATA_FILE = "dadar_final_report.txt"

COL_NAMES = ['Guyyaa', 'Maqaa_Abbaa_Dhimmaa', 'Araddaa', 'Qaxana', 'Gosa_Tajajjilaa', 'Maqaa_Ogeessa', 'Kafaltii_Taj']
MONTH_ORDER = ["Fulbaana", "Onkololeessa", "Sadaasa", "Muddee", "Amajjii", "Guraandhala", "Bitootessa", "Eebila", "Caamsaa", "Waxabajjii", "Adooleessa", "Hagayya"]
MONTH_MAP = {9: "Fulbaana", 10: "Onkololeessa", 11: "Sadaasa", 12: "Muddee", 1: "Amajjii", 2: "Guraandhala", 3: "Bitootessa", 4: "Eebila", 5: "Caamsaa", 6: "Waxabajjii", 7: "Adooleessa", 8: "Hagayya"}

st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #f1f8e9 0%, #ffffff 100%); }
    [data-testid="stSidebar"] { background-color: #1b5e20 !important; }
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

def create_advanced_pdf(name, count, rank, logo_left=None, logo_right=None, signature=None):
    pdf = FPDF(orientation='L', unit='mm', format='A4')
    pdf.add_page()
    
    rank_colors = {1: (255, 215, 0), 2: (192, 192, 192), 3: (205, 127, 50)}
    rank_labels = {1: "1FFAA", 2: "2FFAA", 3: "3FFAA"}
    r_c = rank_colors.get(rank, (0, 80, 0))
    r_t = rank_labels.get(rank, f"{rank}FFAA")

    # Border & BG
    pdf.set_fill_color(255, 255, 255); pdf.rect(10, 10, 277, 190, 'F')
    pdf.set_draw_color(0, 80, 0); pdf.set_line_width(3.0); pdf.rect(10, 10, 277, 190)
    pdf.set_draw_color(*r_c); pdf.set_line_width(1.5); pdf.rect(13, 13, 271, 184)

    # Logo Handling
    def handle_img(file_obj, prefix):
        if file_obj:
            ext = file_obj.name.split('.')[-1].lower()
            path = f"temp_{prefix}.{ext}"
            with open(path, "wb") as f: f.write(file_obj.getbuffer())
            return path
        return None

    p_l = handle_img(logo_left, "l")
    p_r = handle_img(logo_right, "r")
    p_s = handle_img(signature, "sig")

    if p_l: pdf.image(p_l, x=20, y=18, w=25)
    if p_r: pdf.image(p_r, x=250, y=18, w=25)

    # Text Content
    pdf.set_y(45); pdf.set_text_color(*r_c); pdf.set_font('Arial', 'B', 35)
    pdf.cell(0, 15, "SARTIIFIKETA BEEKAMTII", ln=True, align='C')
    pdf.set_y(62); pdf.set_text_color(0, 80, 0); pdf.set_font('Arial', 'B', 22)
    pdf.cell(0, 12, "Waajjira Lafaa Bulchiinsa Magaalaa Dadar", ln=True, align='C')

    pdf.set_y(90); pdf.set_text_color(50, 50, 50); pdf.set_font('Arial', 'I', 18)
    pdf.cell(0, 10, f"Badhaasa Sadarkaa {r_t} Waggaa 2026", ln=True, align='C')

    pdf.ln(5); pdf.set_text_color(0, 80, 0); pdf.set_font('Arial', 'B', 30)
    pdf.cell(0, 25, f"Obbo/Adde: {name.upper()}", ln=True, align='C')

    pdf.set_y(140); pdf.set_text_color(60, 60, 60); pdf.set_font('Arial', '', 14)
    msg = f"Tajaajilamtoota {count} saffisaa fi qulqullinaan tajaajiluun gumaacha guddaa waan gumaachaniif badhaasa kanaan galateeffamaniiru."
    pdf.multi_cell(0, 10, msg.encode('latin-1', 'replace').decode('latin-1'), align='C')

    # Signature Area
    pdf.set_y(175)
    if p_s: pdf.image(p_s, x=55, y=160, h=15)
    pdf.set_draw_color(0, 80, 0); pdf.line(40, 175, 100, 175)
    pdf.set_xy(40, 177); pdf.set_font('Arial', 'B', 12)
    pdf.cell(60, 8, "Mallattoo Itti Gaafatamaa", align='C')

    pdf.line(190, 175, 250, 175)
    pdf.set_xy(190, 177); pdf.cell(60, 8, f"Guyyaa: {datetime.now().strftime('%d/%m/%Y')}", align='C')

    return pdf.output(dest='S').encode('latin-1', 'replace')

# ================= 3. MAIN APP =================
if 'logged_in' not in st.session_state: st.session_state.logged_in = False

if not st.session_state.logged_in:
    _, col_mid, _ = st.columns([1, 1.2, 1])
    with col_mid:
        if os.path.exists(LOGO_PATH): st.image(LOGO_PATH, width=100)
        st.markdown("<h2 style='text-align:center; color: #1b5e20;'>Dadar Land Admin System</h2>", unsafe_allow_html=True)
        with st.form("login"):
            u = st.text_input("Username")
            p = st.text_input("Password", type="password")
            if st.form_submit_button("Seeni"):
                if u == "DAD" and p == "2026": 
                    st.session_state.logged_in = True
                    st.rerun()
                else: st.error("Dogoggora!")
else:
    df = load_data()
    with st.sidebar:
        if os.path.exists(LOGO_PATH): st.image(LOGO_PATH, width=100)
        menu = st.radio("FILANNOO", ["📊 Dashboard", "📝 Galmee Haaraa", "📈 Gabaasa Bal'aa", "🏆 Badhaasa Ogeeyyii", "🔍 Barbaadi/Edit"])
        if st.button("Log Out"):
            st.session_state.logged_in = False
            st.rerun()

    # --- DASHBOARD ---
    if menu == "📊 Dashboard":
        st.title("📊 Dashboard")
        if not df.empty:
            c1, c2, c3 = st.columns(3)
            c1.markdown(f"<div class='card'><h4>💰 Galii</h4><h2>{df['Kafaltii_Taj'].sum():,.2f}</h2><p>ETB</p></div>", unsafe_allow_html=True)
            c2.markdown(f"<div class='card'><h4>👥 Maamiltoota</h4><h2>{len(df)}</h2><p>Waliigala</p></div>", unsafe_allow_html=True)
            c3.markdown(f"<div class='card'><h4>👷 Ogeeyyii</h4><h2>{df['Maqaa_Ogeessa'].nunique()}</h2><p>Aktiiwii</p></div>", unsafe_allow_html=True)
        else: st.info("Data'n hin jiru.")

    # --- REGISTRATION ---
    elif menu == "📝 Galmee Haaraa":
        st.header("📝 Galmee Tajaajilaa & Nagahee")
        GATII_DICT = {"Gibira": ["Gibira Baaxii Gooroo", "Gibira Lafa Qonnaa"], "Liizii": ["Liizii Waggaa", "TOT"], "Kaartaa": ["Kaartaa Lafa"]}
        
        sel_main = st.multiselect("Gosa Tajaajilaa", list(GATII_DICT.keys()))
        details, d_fees = [], {}
        for g in sel_main:
            subs = st.multiselect(f"Tajaajila {g}:", GATII_DICT[g])
            for s in subs:
                details.append(f"{g}({s})")
                d_fees[f"{g}_{s}"] = st.number_input(f"Kafaltii {s} (ETB)", min_value=0.0)

        with st.form("reg_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            maqaa = col1.text_input("Maqaa Abbaa Dhimmaa")
            ara = col2.text_input("Araddaa")
            qax = col1.text_input("Qaxana")
            ogeessa = col2.text_input("Maqaa Ogeessaa")
            
            # --- UPLOAD NAGAHEE ---
            nagahee_file = st.file_uploader("Nagahee Scan (JPG/PNG)", type=['jpg','png','jpeg'])
            
            if st.form_submit_button("💾 Galmeessi"):
                if maqaa and ogeessa and details:
                    if nagahee_file:
                        f_name = f"{maqaa.replace(' ','_')}_{datetime.now().strftime('%H%M%S')}.jpg"
                        with open(os.path.join(NAGAHEE_DIR, f_name), "wb") as f:
                            f.write(nagahee_file.getbuffer())
                    
                    new_data = [datetime.now().strftime('%d/%m/%Y'), maqaa, ara, qax, ", ".join(details), ogeessa, sum(d_fees.values())]
                    df = pd.concat([df, pd.DataFrame([new_data], columns=COL_NAMES)], ignore_index=True)
                    save_data(df)
                    st.success("✅ Galmeeffameera!")

    # --- BADHAASA OGEEYYII ---
    elif menu == "🏆 Badhaasa Ogeeyyii":
        st.header("🏆 Sartiifiikeeta Badhaasaa")
        cl, cm, cr = st.columns(3)
        l_l = cl.file_uploader("Logo Bitaa", type=['png','jpg'], key="l1")
        l_r = cm.file_uploader("Logo Mirgaa", type=['png','jpg'], key="l2")
        sig = cr.file_uploader("Mallattoo (Signature)", type=['png','jpg'], key="s1")

        if not df.empty:
            top_3 = df['Maqaa_Ogeessa'].value_counts().head(3)
            cols = st.columns(3)
            for i, (name, count) in enumerate(top_3.items(), 1):
                with cols[i-1]:
                    st.markdown(f"<div class='card'><h2>{i}FFAA</h2><h3>{name}</h3><p>Hojii: {count}</p></div>", unsafe_allow_html=True)
                    pdf_bytes = create_advanced_pdf(name, count, i, l_l, l_r, sig)
                    st.download_button(f"📥 PDF {i}", pdf_bytes, f"Cert_{name}.pdf", "application/pdf")

    # --- GABAASA BAL'AA ---
    elif menu == "📈 Gabaasa Bal'aa":
        st.header("📈 Gabaasa Galii")
        if not df.empty:
            st.dataframe(df[COL_NAMES], use_container_width=True)
            st.metric("Galii Waliigalaa", f"{df['Kafaltii_Taj'].sum():,.2f} ETB")
            
            # Trend Chart
            fig = px.line(df.groupby('Guyyaa')['Kafaltii_Taj'].sum().reset_index(), x='Guyyaa', y='Kafaltii_Taj', title="Trendii Galii")
            st.plotly_chart(fig)
            
    # --- SEARCH & EDIT ---
    elif menu == "🔍 Barbaadi/Edit":
        st.header("🔍 Barbaadi fi Sirreessi")
        q = st.text_input("Maqaa Barbaadi")
        if q and not df.empty:
            res = df[df['Maqaa_Abbaa_Dhimmaa'].str.contains(q, case=False, na=False)]
            for idx, row in res.iterrows():
                with st.expander(f"📄 {row['Maqaa_Abbaa_Dhimmaa']}"):
                    n_n = st.text_input("Maqaa", row['Maqaa_Abbaa_Dhimmaa'], key=f"n{idx}")
                    if st.button("Update", key=f"u{idx}"):
                        df.at[idx, 'Maqaa_Abbaa_Dhimmaa'] = n_n
                        save_data(df); st.rerun()
