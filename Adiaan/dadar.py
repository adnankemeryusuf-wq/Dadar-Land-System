import streamlit as st
import pandas as pd
import os
import io
import requests
import base64
from datetime import datetime
from fpdf import FPDF

# ================= 1. CONFIGURATION & STYLE =================
LOGO_PATH = "Adiaan/logo.png"
DATA_FILE = "dadar_final_report.txt"
NAGAHEE_DIR = "Adiaan/nagahee"
BOT_TOKEN = "8357193631:AAHCuSnXzjZTQaglkmcS0gq-EvqnkIQLDBI"
CHAT_ID_MANAGER = "7329587700"

if not os.path.exists(NAGAHEE_DIR):
    os.makedirs(NAGAHEE_DIR)

st.set_page_config(
    page_title="Dadar Land Customer Registration", 
    page_icon=LOGO_PATH if os.path.exists(LOGO_PATH) else "🏢", 
    layout="wide"
)

# --- CORE FUNCTIONS ---
COL_NAMES = ['Guyyaa', 'Maqaa_Abbaa_Dhimmaa', 'Araddaa', 'Qaxana', 'Gosa_Tajajjilaa', 'Maqaa_Ogeessa', 'Kafaltii_Taj']
MONTH_MAP = {9: "Fulbaana", 10: "Onkololeessa", 11: "Sadaasa", 12: "Muddee", 1: "Amajjii", 2: "Guraandhala", 3: "Bitootessa", 4: "Eebila", 5: "Caamsaa", 6: "Waxabajjii", 7: "Adooleessa", 8: "Hagayya"}
MONTH_ORDER = ["Fulbaana", "Onkololeessa", "Sadaasa", "Muddee", "Amajjii", "Guraandhala", "Bitootessa", "Eebila", "Caamsaa", "Waxabajjii", "Adooleessa", "Hagayya"]

def save_data(df_to_save):
    try:
        df_to_save[COL_NAMES].to_csv(DATA_FILE, sep="|", index=False, header=False, encoding="utf-8")
        return True
    except Exception as e:
        st.error(f"Error saving data: {e}")
        return False

def load_data():
    if not os.path.exists(DATA_FILE) or os.stat(DATA_FILE).st_size == 0:
        return pd.DataFrame(columns=COL_NAMES)
    try:
        df = pd.read_csv(DATA_FILE, sep="|", names=COL_NAMES, header=None, encoding='utf-8')
        df['Date_Obj'] = pd.to_datetime(df['Guyyaa'], format='%d/%m/%Y', errors='coerce')
        df['Waggaa'] = df['Date_Obj'].dt.year
        df['Ji\'a'] = df['Date_Obj'].dt.month.map(MONTH_MAP)
        return df
    except:
        return pd.DataFrame(columns=COL_NAMES)

def get_base64_img(path):
    if os.path.exists(path):
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return ""

def create_advanced_pdf(name, count, rank, logo_l=None, logo_r=None):
    pdf = FPDF(orientation='L', unit='mm', format='A4')
    pdf.add_page()
    colors = {1: (255, 215, 0), 2: (192, 192, 192), 3: (205, 127, 50)}
    b_color = colors.get(rank, (27, 94, 32))
    pdf.set_draw_color(*b_color)
    pdf.set_line_width(3.0); pdf.rect(10, 10, 277, 190)
    
    # Logo Handling
    if logo_l: pdf.image(logo_l, 15, 15, 30)
    elif os.path.exists(LOGO_PATH): pdf.image(LOGO_PATH, 15, 15, 30)
    
    pdf.set_y(50)
    pdf.set_font('Arial', 'B', 32); pdf.set_text_color(*b_color)
    pdf.cell(0, 15, "SARTIIFIKETA BEEKAMTII", ln=True, align='C')
    pdf.set_font('Arial', '', 20); pdf.set_text_color(0, 0, 0); pdf.ln(20)
    msg = f"Obbo/Adde {str(name).upper()}\n\nTajaajilamtoota {count} saffisaan tajaajiluun sadarkaa {rank}ffaa\nwaggaa 2026 waan qabataniif beekamtiin kun kennameef."
    pdf.multi_cell(0, 12, msg, align='C')
    return pdf.output(dest='S').encode('latin-1')

# ================= 2. STYLE =================
img_b64 = get_base64_img(LOGO_PATH)
st.markdown(f"""
    <style>
    .header-container {{ display: flex; align-items: center; background-color: white; padding: 15px; border-radius: 12px; border-bottom: 5px solid #2e7d32; margin-bottom: 25px; }}
    .logo-img {{ width: 90px; height: 90px; margin-right: 25px; }}
    .card {{ background: white; padding: 20px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); text-align: center; border-top: 5px solid #2e7d32; }}
    </style>
    """, unsafe_allow_html=True)

# ================= 3. MAIN APP =================
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.markdown("<br><br>", unsafe_allow_html=True)
    _, col_mid, _ = st.columns([1, 1.2, 1])
    with col_mid:
        if os.path.exists(LOGO_PATH): st.image(LOGO_PATH, width=120)
        st.markdown("<h2 style='text-align:center;'>Systemii Galmee Dadar</h2>", unsafe_allow_html=True)
        with st.form("login"):
            u = st.text_input("Username")
            p = st.text_input("Password", type="password")
            if st.form_submit_button("Seeni"):
                if u == "DAD" and p == "2026":
                    st.session_state.logged_in = True; st.rerun()
                else: st.error("Dogoggora!")
else:
    logo_src = f"data:image/png;base64,{img_b64}" if img_b64 else ""
    st.markdown(f'<div class="header-container"><img src="{logo_src}" class="logo-img"><div><h1 style="margin:0; font-size: 28px;">BULCHIINSA MAGAALAA DADAR</h1><h2 style="margin:0; font-size: 20px; color: #4caf50;">WAAJJIRA LAFAA</h2></div></div>', unsafe_allow_html=True)
    
    df = load_data()
    menu = st.sidebar.radio("FILANNOO", ["📊 Dashboard", "📝 Galmee Haaraa", "🏆 Badhaasa", "🔍 Barbaadi/Edit"])

    if menu == "📊 Dashboard":
        st.header("📊 Dashboard")
        if not df.empty:
            c1, c2, c3 = st.columns(3)
            with c1: st.markdown(f"<div class='card'><p>💰 Galii</p><h3>{df['Kafaltii_Taj'].sum():,.2f}</h3></div>", unsafe_allow_html=True)
            with c2: st.markdown(f"<div class='card'><p>👥 Maamiltoota</p><h3>{len(df)}</h3></div>", unsafe_allow_html=True)
            with c3: st.markdown(f"<div class='card'><p>👷 Ogeeyyii</p><h3>{df['Maqaa_Ogeessa'].nunique()}</h3></div>", unsafe_allow_html=True)
            st.area_chart(df.groupby('Ji\'a')['Kafaltii_Taj'].sum().reindex(MONTH_ORDER).fillna(0))
        else: st.info("Data'n hin jiru.")

    elif menu == "📝 Galmee Haaraa":
        st.header("📝 Galmee Tajaajilaa")
        GATII_DICT = {
            "Gibira": ["Gibira Baaxii Gooroo", "Gibira Lafa Qonnaa", "Gibira Manaa"],
            "Liizii": ["Liizii Waggaa", "Jijjiirraa Maqaa", "Kafaltii Liizii Duraa", "TOT (Turnover Tax)"],
            "Ittii Fayyaddam": ["Hayyama Itti Fayyadama Lafaa", "Humna Mahandiisaa", "Waraqaa Ragaa Qabiyyee"],
            "Kaartaa": ["Kaartaa Lafa", "Kaartaa Kadastaara", "Kaartaa Lafa Qonnaa", "Suphaa Kaartaa"],
            "Dhimma Mana Murtii": ["Ugura Mana Murtii", "Uguraa Mana Murtii Kaasuu", "Waraqaa Ragaa Dhorkaa"],
            "Liqii Bankii": ["Dhorkaa Liqii Bankii", "Dhorkaa Liqii Bankii Kaasuu", "Xalayaa Madaallii Qabeenyaa"]
        }

        selected_main = st.multiselect("🟢 Gosa Tajaajilaa Filadhu", list(GATII_DICT.keys()))
        details, d_fees = [], {}
        if selected_main:
            for g in selected_main:
                subs = st.multiselect(f"Tajaajila {g}:", GATII_DICT[g], key=f"m_{g}")
                for s in subs:
                    details.append(f"{g}({s})")
                    d_fees[f"{g}_{s}"] = st.number_input(f"Kafaltii {s} (ETB)", min_value=0.0, key=f"f_{g}_{s}")

        with st.form("entry_form", clear_on_submit=True):
            c1, c2 = st.columns(2)
            maqaa_f = c1.text_input("Maqaa Abbaa Dhimmaa *")
            ara_f = c2.text_input("Araddaa *")
            qax_f = c1.text_input("Qaxana *")
            ogeessa = c2.text_input("Maqaa Ogeessaa *")
            nagahee_file = st.file_uploader("Nagahee Scan (JPG/PNG)", type=['jpg','png','jpeg'])
            
            if st.form_submit_button("💾 Galmeessi"):
                if not (maqaa_f and ara_f and ogeessa) or not details:
                    st.error("⚠️ Maaloo, odeeffannoo hunda guuti!")
                else:
                    if nagahee_file:
                        f_path = os.path.join(NAGAHEE_DIR, f"{maqaa_f.replace(' ','_')}.jpg")
                        with open(f_path, "wb") as f: f.write(nagahee_file.getbuffer())
                    
                    new_row = [datetime.now().strftime('%d/%m/%Y'), maqaa_f, ara_f, qax_f, ", ".join(details), ogeessa, sum(d_fees.values())]
                    df = pd.concat([df, pd.DataFrame([new_row], columns=COL_NAMES)], ignore_index=True)
                    if save_data(df):
                        st.success(f"✅ Galmeen {maqaa_f} raawwatameera!"); st.balloons()

    elif menu == "🏆 Badhaasa":
        st.header("🏆 Sadarkaa Ogeeyyii")
        cl, cr = st.columns(2)
        l_l = cl.file_uploader("Logo Bitaa", type=['png', 'jpg'], key="l_pdf")
        
        if not df.empty:
            top_3 = df['Maqaa_Ogeessa'].value_counts().head(3)
            cols = st.columns(3)
            colors = ["#FFD700", "#C0C0C0", "#CD7F32"]
            for i, (name, count) in enumerate(top_3.items()):
                with cols[i]:
                    st.markdown(f"<div class='card' style='border-top:5px solid {colors[i]}'><h2>#{i+1}</h2><h3>{name}</h3><p>Hojii: {count}</p></div>", unsafe_allow_html=True)
                    pdf_data = create_advanced_pdf(name, count, i+1, l_l)
                    st.download_button(f"Sartiifiketa {name}", data=pdf_data, file_name=f"Badhaasa_{name}.pdf", mime="application/pdf")

    elif menu == "🔍 Barbaadi/Edit":
        st.header("🔍 Barbaadi fi Sirreessi")
        q = st.text_input("Maqaa Barbaadi...")
        if q and not df.empty:
            res = df[df['Maqaa_Abbaa_Dhimmaa'].str.contains(q, case=False, na=False)]
            for idx, row in res.iterrows():
                with st.expander(f"📄 {row['Maqaa_Abbaa_Dhimmaa']}"):
                    n_n = st.text_input("Maqaa", row['Maqaa_Abbaa_Dhimmaa'], key=f"n_{idx}")
                    if st.button("💾 Update", key=f"u_{idx}"):
                        df.at[idx, 'Maqaa_Abbaa_Dhimmaa'] = n_n
                        save_data(df); st.rerun()
