import streamlit as st
import pandas as pd
import os
from datetime import datetime
from fpdf import FPDF

# ================= 1. CONFIGURATION & STYLE =================
LOGO_PATH = "Adiaan/logo.png"
DATA_FILE = "dadar_final_report.txt"
NAGAHEE_DIR = "nagahee_scan"

if not os.path.exists(NAGAHEE_DIR):
    os.makedirs(NAGAHEE_DIR)

st.set_page_config(
    page_title="Dadar Land Administration",
    page_icon="🏢",
    layout="wide"
)

# Custom CSS for the #f1f8e9 aesthetic
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(135deg, #f1f8e9 0%, #ffffff 100%);
    }
    [data-testid="stSidebar"] {
        background-color: #33691e !important;
    }
    [data-testid="stSidebar"] * {
        color: #ffffff !important;
    }
    div.stForm {
        background: white;
        border-radius: 15px;
        padding: 25px;
        border: 1px solid #c5e1a5;
        box-shadow: 0px 4px 15px rgba(0, 0, 0, 0.05);
    }
    .card {
        background: white;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        text-align: center;
        border-top: 5px solid #33691e;
    }
    .metric-value {
        font-size: 28px;
        font-weight: bold;
        color: #1b5e20;
    }
    </style>
""", unsafe_allow_html=True)

# ================= 2. CORE FUNCTIONS =================
COL_NAMES = ['Guyyaa', 'Maqaa_Abbaa_Dhimmaa', 'Araddaa', 'Qaxana', 'Gosa_Tajajjilaa', 'Maqaa_Ogeessa', 'Kafaltii_Taj']

@st.cache_data(ttl=60)
def load_data():
    if not os.path.exists(DATA_FILE) or os.stat(DATA_FILE).st_size == 0:
        return pd.DataFrame(columns=COL_NAMES)
    df = pd.read_csv(DATA_FILE, sep="|", names=COL_NAMES, header=None, encoding='utf-8')
    df['Kafaltii_Taj'] = pd.to_numeric(df['Kafaltii_Taj'], errors='coerce').fillna(0)
    return df

def save_data(df_to_save):
    df_to_save[COL_NAMES].to_csv(DATA_FILE, sep="|", index=False, header=False, encoding="utf-8")
    st.cache_data.clear()

def create_advanced_pdf(name, count, rank):
    pdf = FPDF(orientation='L', unit='mm', format='A4')
    pdf.add_page()
    # Rank colors: Gold, Silver, Bronze
    colors = [(255, 215, 0), (192, 192, 192), (205, 127, 50)]
    rank_color = colors[rank-1] if rank <= 3 else (51, 105, 30)
    
    pdf.set_draw_color(51, 105, 30); pdf.set_line_width(3); pdf.rect(10, 10, 277, 190)
    pdf.set_draw_color(*rank_color); pdf.set_line_width(1.5); pdf.rect(13, 13, 271, 184)
    
    pdf.set_y(60)
    pdf.set_font('Arial', 'B', 35); pdf.set_text_color(*rank_color)
    pdf.cell(0, 15, "SARTIIFIKETA BEEKAMTII", ln=True, align='C')
    
    pdf.set_y(90)
    pdf.set_font('Arial', 'B', 25); pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 20, f"Obbo/Adde: {name.upper()}", ln=True, align='C')
    
    pdf.set_font('Arial', '', 16)
    pdf.multi_cell(0, 15, f"Tajaajilamtoota {count} saffisaan tajaajiluun gumaacha guddaa\nwaan gumaachaniif badhaasa kanaan galateeffamaniiru.", align='C')
    return pdf.output(dest='S').encode('latin-1', 'ignore')

# ================= 3. AUTHENTICATION =================
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    _, col_mid, _ = st.columns([1, 1.2, 1])
    with col_mid:
        st.markdown("<br><br><h2 style='text-align:center;'>🏢 Dadar Land System</h2>", unsafe_allow_html=True)
        with st.form("login"):
            u = st.text_input("Username")
            p = st.text_input("Password", type="password")
            if st.form_submit_button("Seeni"):
                if u == "DAD" and p == "2026":
                    st.session_state.logged_in = True
                    st.rerun()
                else:
                    st.error("Maqaan ykn Koodiin dogoggora!")
else:
    df = load_data()
    with st.sidebar:
        st.header("Deder City Land")
        menu = st.radio("FILANNOO", ["📊 Dashboard", "📝 Galmee Haaraa", "🏆 Badhaasa", "🔍 Barbaadi/Edit"])
        if st.button("Log Out"):
            st.session_state.logged_in = False
            st.rerun()

    # --- DASHBOARD ---
    if menu == "📊 Dashboard":
        st.header("📊 Gabaasa Gabaabaa")
        if not df.empty:
            c1, c2, c3 = st.columns(3)
            with c1: st.markdown(f"<div class='card'><p>💰 Galii Waliigalaa</p><p class='metric-value'>{df['Kafaltii_Taj'].sum():,.2f} ETB</p></div>", unsafe_allow_html=True)
            with c2: st.markdown(f"<div class='card'><p>👥 Maamiltoota Waliigalaa</p><p class='metric-value'>{len(df)}</p></div>", unsafe_allow_html=True)
            with c3: st.markdown(f"<div class='card'><p>👷 Ogeeyyii</p><p class='metric-value'>{df['Maqaa_Ogeessa'].nunique()}</p></div>", unsafe_allow_html=True)
            
            st.markdown("### Transaction Trend")
            df['Date_Obj'] = pd.to_datetime(df['Guyyaa'], format='%d/%m/%Y', errors='coerce')
            trend = df.groupby('Guyyaa').size()
            st.line_chart(trend)
        else:
            st.info("Ragaan galmeeffame hin jiru.")

    # --- REGISTRATION ---
    elif menu == "📝 Galmee Haaraa":
        st.header("📝 Galmee Tajaajilaa Haaraa")
        
        SERVICE_STRUCTURE = {
            "🏷️ Gibira & Kaffaltii": ["Gibira Baaxii Gooroo", "Gibira Lafa Qonnaa", "Kaffaltii Liizii Waggaa", "Gibira Milkii", "TOT"],
            "📜 Kaartaa & Qabiyyee": ["Kaartaa Haaraa", "Kaartaa Bakka Bu'aa", "Jijjiirraa Maqaa", "Sirreeffama Daangaa"],
            "🏗️ Pilaanii & Ijaarsa": ["Hayyama Ijaarsaa", "Pilaanii Magaalaa", "Land Use", "Mirkaneessa Sertifikeeta"],
            "⚖️ Dhimma Seeraa": ["Ugura Mana Murtii", "Ugura Kaasuu", "Waliigaltee Liqii Baankii", "Dhimma Dhala"],
            "📂 Biroo": ["Waraqaa Ragaa", "Deebii Iyyannoo", "Tajaajila Koppii"]
        }
        
        selected_main = st.multiselect("🟢 Gosa Tajaajilaa Filadhu", list(SERVICE_STRUCTURE.keys()))
        details, d_fees = [], {}
        
        if selected_main:
            for g in selected_main:
                subs = st.multiselect(f"Tajaajila {g}:", SERVICE_STRUCTURE[g], key=f"m_{g}")
                for s in subs:
                    details.append(f"{g}({s})")
                    d_fees[f"{g}_{s}"] = st.number_input(f"Kafaltii {s} (ETB)", min_value=0.0, key=f"f_{g}_{s}")

        with st.form("entry_form", clear_on_submit=True):
            st.markdown("##### Odeeffannoo Maamilaa")
            c1, c2 = st.columns(2)
            name = c1.text_input("Maqaa Abbaa Dhimmaa *")
            ara = c2.text_input("Araddaa *")
            qax = c1.text_input("Qaxana")
            ogeessa = c2.text_input("Maqaa Ogeessaa *")
            nagahee = st.file_uploader("Nagahee Scan (JPG/PNG)", type=['jpg','png','jpeg'])

            if st.form_submit_button("💾 Galmeessi"):
                if name and details and ogeessa:
                    if nagahee:
                        f_name = f"{name.replace(' ','_')}_{datetime.now().strftime('%H%M%S')}.jpg"
                        with open(os.path.join(NAGAHEE_DIR, f_name), "wb") as f:
                            f.write(nagahee.getbuffer())
                    
                    total_paid = sum(d_fees.values())
                    new_row = [datetime.now().strftime('%d/%m/%Y'), name, ara, qax, ", ".join(details), ogeessa, total_paid]
                    df = pd.concat([df, pd.DataFrame([new_row], columns=COL_NAMES)], ignore_index=True)
                    save_data(df)
                    st.success(f"✅ Galmee {name} milkaa'inaan kuusameera!")
                    st.rerun()
                else:
                    st.warning("Maaloo odeeffannoo dirqamaa (*) guutaa.")

    # --- BADHAASA OGEEYYII ---
    elif menu == "🏆 Badhaasa":
        st.header("🏆 Sadarkaa Ogeeyyii")
        if not df.empty:
            top_3 = df['Maqaa_Ogeessa'].value_counts().head(3)
            cols = st.columns(len(top_3))
            for i, (name, count) in enumerate(top_3.items()):
                with cols[i]:
                    st.markdown(f"<div class='card'><h3>{name}</h3><p>Hojii Rawwatame: <b>{count}</b></p></div>", unsafe_allow_html=True)
                    pdf_bytes = create_advanced_pdf(name, count, i+1)
                    st.download_button(f"📥 Sartiifiketa {i+1}", pdf_bytes, f"{name}_Sertifikeeta.pdf", "application/pdf")
        else:
            st.info("Ragaan ogeeyyii hin jiru.")

    # --- BARBAADI / EDIT ---
    elif menu == "🔍 Barbaadi/Edit":
        st.header("🔍 Barbaadi fi Sirreessi")
        search_q = st.text_input("Maqaa Abbaa Dhimmaa Barbaadi...")
        if search_q and not df.empty:
            res = df[df['Maqaa_Abbaa_Dhimmaa'].str.contains(search_q, case=False, na=False)]
            st.dataframe(res, use_container_width=True)
        elif not df.empty:
            st.dataframe(df.tail(10), use_container_width=True)
