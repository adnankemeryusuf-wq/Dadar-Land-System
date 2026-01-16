import streamlit as st
import pandas as pd
import os
import io
import requests
from datetime import datetime
from fpdf import FPDF

# ================= 1. CONFIGURATION & STYLE =================
LOGO_PATH = "Adiaan/logo.png"

st.set_page_config(
    page_title="Dadar Land Customer Registration System", 
    page_icon=LOGO_PATH if os.path.exists(LOGO_PATH) else "🏢", 
    layout="wide"
)

# --- CSS: MANAGE APP DHOKSUU FI BAREEDINA UI ---
st.markdown("""
    <style>
    /* "Manage App", "Deploy", fi "Share" guutummaatti dhoksuuf */
    header, .stAppToolbar, .stActionButton, .stDeployButton {
        visibility: hidden; 
        display: none !important;
    }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}

    /* Style Sidebar fi Cards */
    .stApp { background: linear-gradient(135deg, #f1f8e9 0%, #ffffff 100%); }
    [data-testid="stSidebar"] { background-color: #1b5e20 !important; }
    [data-testid="stSidebar"] * { color: #ffffff !important; }
    
    /* Card style badhaasaaf */
    .card { 
        background: white; 
        padding: 20px; 
        border-radius: 12px; 
        box-shadow: 0 4px 6px rgba(0,0,0,0.1); 
        text-align: center; 
        margin-bottom: 10px;
    }
    .stButton>button { 
        background: linear-gradient(90deg, #4caf50, #2e7d32); 
        color: white; 
        border-radius: 8px; 
        font-weight: bold; 
        width: 100%; 
    }
    </style>
    """, unsafe_allow_html=True)

# ================= 2. DATA HANDLING =================
DATA_FILE = "dadar_final_report.txt"
COL_NAMES = ['Guyyaa', 'Maqaa_Abbaa_Dhimmaa', 'Araddaa', 'Qaxana', 'Gosa_Tajajjilaa', 'Maqaa_Ogeessa', 'Kafaltii_Taj']

def load_data():
    if not os.path.exists(DATA_FILE) or os.stat(DATA_FILE).st_size == 0:
        return pd.DataFrame(columns=COL_NAMES)
    df = pd.read_csv(DATA_FILE, sep="|", names=COL_NAMES, header=None, encoding='utf-8')
    return df

def save_data(df_to_save):
    df_to_save[COL_NAMES].to_csv(DATA_FILE, sep="|", index=False, header=False, encoding="utf-8")

# ================= 3. SARTIIFIKETA (PDF) WITH LOGOS =================
def create_certificate_pdf(name, count, rank, logo_p):
    pdf = FPDF(orientation='L', unit='mm', format='A4')
    pdf.add_page()
    
    # Halluuwwan Sadarkaa
    colors = {1: (255, 215, 0), 2: (192, 192, 192), 3: (205, 127, 50)}
    r_color = colors.get(rank, (0, 80, 0))
    r_text = "1FFAA" if rank==1 else ("2FFAA" if rank==2 else "3FFAA")

    # Border Dachaa
    pdf.set_draw_color(*r_color); pdf.set_line_width(3); pdf.rect(10, 10, 277, 190)
    pdf.set_draw_color(0, 80, 0); pdf.set_line_width(1); pdf.rect(13, 13, 271, 184)

    # Logo Bitaa fi Mirgaa galchuuf
    if logo_p and os.path.exists(logo_p):
        pdf.image(logo_p, x=20, y=18, w=25)  # Bitaa
        pdf.image(logo_p, x=250, y=18, w=25) # Mirgaa

    # Barreeffama Sartiifiketaa
    pdf.set_y(50); pdf.set_text_color(*r_color); pdf.set_font('Arial', 'B', 35)
    pdf.cell(0, 15, "SARTIIFIKETA BEEKAMTII", ln=True, align='C')
    
    pdf.set_y(65); pdf.set_text_color(0, 80, 0); pdf.set_font('Arial', 'B', 20)
    pdf.cell(0, 10, "Waajjira Lafaa Bulchiinsa Magaalaa Dadar", ln=True, align='C')

    pdf.set_y(100); pdf.set_text_color(0, 0, 0); pdf.set_font('Arial', 'B', 30)
    pdf.cell(0, 20, name.upper(), ln=True, align='C')

    pdf.set_y(130); pdf.set_font('Arial', '', 16)
    msg = f"Sadarkaa {r_text} Waggaa 2026 tajaajilamtoota {count} saffisaan tajaajiluun\ngumaacha guddaa waan gumaachaniif sartiifikonni kun kennameef."
    pdf.multi_cell(0, 10, msg, align='C')

    # Guyyaa fi Mallattoo
    pdf.set_y(170); pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, f"Guyyaa: {datetime.now().strftime('%d/%m/%Y')}              Mallattoo: ________________", align='C')

    return pdf.output(dest='S').encode('latin-1')

# ================= 4. MAIN APP LOGIC =================
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    # Login Page
    _, col_mid, _ = st.columns([1, 1.2, 1])
    with col_mid:
        if os.path.exists(LOGO_PATH): st.image(LOGO_PATH, width=100)
        st.header("Dadar Land Admin")
        with st.form("login"):
            u = st.text_input("Username")
            p = st.text_input("Password", type="password")
            if st.form_submit_button("Seeni"):
                if u == "DAD" and p == "2026":
                    st.session_state.logged_in = True
                    st.rerun()
                else: st.error("Koodiin dogoggora!")
else:
    df = load_data()
    with st.sidebar:
        if os.path.exists(LOGO_PATH): st.image(LOGO_PATH, width=100)
        menu = st.radio("FILANNOO", ["📊 Dashboard", "📝 Galmee Haaraa", "📈 Gabaasa", "🏆 Badhaasa Ogeeyyii", "🔍 Barbaadi"])
        if st.button("Log Out"):
            st.session_state.logged_in = False; st.rerun()

    # --- BADHAASA OGEEYYII ---
    if menu == "🏆 Badhaasa Ogeeyyii":
        st.markdown("<h2 style='text-align:center;'>🏆 Sadarkaa Ogeeyyii Sadan Jalqabaa</h2>", unsafe_allow_html=True)
        if not df.empty:
            top_3 = df['Maqaa_Ogeessa'].value_counts().head(3)
            cols = st.columns(3)
            colors = ["#FFD700", "#C0C0C0", "#CD7F32"] 
            labels = ["1FFAA", "2FFAA", "3FFAA"]

            for i, (name, count) in enumerate(top_3.items()):
                with cols[i]:
                    st.markdown(f"""
                        <div class='card' style='border-top: 10px solid {colors[i]};'>
                            <h1 style='color: {colors[i]};'>{labels[i]}</h1>
                            <h3>{name}</h3>
                            <p>Hojii: <b>{count}</b></p>
                        </div>""", unsafe_allow_html=True)
                    
                    # Button buufataa
                    pdf_data = create_certificate_pdf(name, count, i+1, LOGO_PATH)
                    st.download_button(
                        label=f"📥 Sartiifiketa {labels[i]}",
                        data=pdf_data,
                        file_name=f"Sartiifiketa_{name}.pdf",
                        mime="application/pdf",
                        key=f"btn_{i}"
                    )
        else:
            st.info("Data'n hojii ogeeyyii hin jiru.")

    # --- DASHBOARD & OTHERS ---
    elif menu == "📊 Dashboard":
        st.title("📊 Dashboard")
        st.write(f"Waliigala Galii: {df['Kafaltii_Taj'].sum() if not df.empty else 0} ETB")
        st.dataframe(df)

    elif menu == "📝 Galmee Haaraa":
        # Kutaa galmee kee asitti itti fufi...
        st.header("📝 Galmee Haaraa")
        with st.form("reg"):
            m_name = st.text_input("Maqaa Maamilaa")
            m_og = st.text_input("Maqaa Ogeessaa")
            m_pay = st.number_input("Kafaltii", min_value=0.0)
            if st.form_submit_button("Galmeessi"):
                new_row = [datetime.now().strftime('%d/%m/%Y'), m_name, "Araddaa", "Qaxana", "Tajaajila", m_og, m_pay]
                df = pd.concat([df, pd.DataFrame([new_row], columns=COL_NAMES)], ignore_index=True)
                save_data(df); st.success("Galmeeffameera!"); st.rerun()
