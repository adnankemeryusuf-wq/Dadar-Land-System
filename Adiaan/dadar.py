import streamlit as st
import pandas as pd
import os
import io
from datetime import datetime
from fpdf import FPDF
import plotly.express as px

# ================= 1. QINDOOMMINA & MIIDHAGSINA =================
DATA_FILE = "dadar_final_report.txt"
NAGAHEE_DIR = "nagahee_scan"
LOGO_PATH = "Adiaan/logo.png"

if not os.path.exists(NAGAHEE_DIR):
    os.makedirs(NAGAHEE_DIR)

st.set_page_config(page_title="Dadar Land System", layout="wide", page_icon="🏢")

# Constants
COL_NAMES = ['Guyyaa', 'Maqaa_Abbaa_Dhimmaa', 'Araddaa', 'Qaxana', 'Gosa_Tajajjilaa', 'Maqaa_Ogeessa', 'Kafaltii_Taj']
MONTH_MAP = {9: "Fulbaana", 10: "Onkololeessa", 11: "Sadaasa", 12: "Muddee", 1: "Amajjii", 2: "Guraandhala", 3: "Bitootessa", 4: "Eebila", 5: "Caamsaa", 6: "Waxabajjii", 7: "Adooleessa", 8: "Hagayya"}

# Miidhagsa CSS
st.markdown("""
    <style>
    .stApp { background-color: #f0f2f6; }
    [data-testid="stSidebar"] { background-color: #1b5e20 !important; }
    .card { background: white; padding: 20px; border-radius: 10px; box-shadow: 0 4px 8px rgba(0,0,0,0.1); text-align: center; border-top: 5px solid #2e7d32; }
    .metric-val { font-size: 24px; font-weight: bold; color: #1b5e20; }
    </style>
    """, unsafe_allow_html=True)

# ================= 2. DALAGAAWWAN (FUNCTIONS) =================
def load_data():
    if not os.path.exists(DATA_FILE) or os.stat(DATA_FILE).st_size == 0:
        return pd.DataFrame(columns=COL_NAMES)
    df = pd.read_csv(DATA_FILE, sep="|", names=COL_NAMES, header=None, encoding='utf-8')
    df['Kafaltii_Taj'] = pd.to_numeric(df['Kafaltii_Taj'], errors='coerce').fillna(0.0)
    df['Date_Obj'] = pd.to_datetime(df['Guyyaa'], format='%d/%m/%Y', errors='coerce')
    df['Ji\'a'] = df['Date_Obj'].dt.month.map(MONTH_MAP)
    return df

def save_data(df_to_save):
    df_to_save[COL_NAMES].to_csv(DATA_FILE, sep="|", index=False, header=False, encoding="utf-8")

def create_pdf(name, count, rank):
    pdf = FPDF(orientation='L', unit='mm', format='A4')
    pdf.add_page()
    pdf.set_draw_color(0, 80, 0)
    pdf.set_line_width(2)
    pdf.rect(10, 10, 277, 190)
    pdf.set_y(50)
    pdf.set_font('Arial', 'B', 35)
    pdf.cell(0, 20, "SARTIIFIKETA BEEKAMTII", ln=True, align='C')
    pdf.set_font('Arial', '', 25)
    pdf.cell(0, 20, f"Obbo/Adde: {name.upper()}", ln=True, align='C')
    pdf.set_font('Arial', 'I', 18)
    pdf.multi_cell(0, 15, f"\nTajaajilamtoota {count} saffisaan tajaajiluun\nsadarkaa {rank}ffaa argataniiru.", align='C')
    return pdf.output(dest='S').encode('latin-1', 'replace')

# ================= 3. APP LOGIC =================
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    _, col_mid, _ = st.columns([1, 1.2, 1])
    with col_mid:
        st.markdown("<h2 style='text-align:center;'>Dadar Land Login</h2>", unsafe_allow_html=True)
        with st.form(key="login_form_final"):
            u = st.text_input("Username")
            p = st.text_input("Password", type="password")
            if st.form_submit_button("Seeni"):
                if u == "DAD" and p == "2026":
                    st.session_state.logged_in = True
                    st.rerun()
                else: st.error("Maqaa ykn Password dogoggora!")
else:
    df = load_data()
    st.sidebar.title("Dadar System")
    menu = st.sidebar.radio("FILANNOO", ["📊 Dashboard", "📝 Galmee Haaraa", "📈 Gabaasa Bal'aa", "🏆 Badhaasa", "🔍 Barbaadi/Sirreessi"])
    
    if st.sidebar.button("Log Out"):
        st.session_state.logged_in = False
        st.rerun()

    # --- DASHBOARD ---
    if menu == "📊 Dashboard":
        st.title("📊 Dashboard Waliigalaa")
        if not df.empty:
            c1, c2, c3 = st.columns(3)
            c1.markdown(f"<div class='card'><p>💰 Galii Waliigalaa</p><p class='metric-val'>{df['Kafaltii_Taj'].sum():,.2f} ETB</p></div>", unsafe_allow_html=True)
            c2.markdown(f"<div class='card'><p>👥 Baay'ina Maamiltootaa</p><p class='metric-val'>{len(df)}</p></div>", unsafe_allow_html=True)
            top_og = df['Maqaa_Ogeessa'].mode()[0] if not df['Maqaa_Ogeessa'].empty else "-"
            c3.markdown(f"<div class='card'><p>🏆 Ogeessa Hojii Baay'ee</p><p class='metric-val'>{top_og}</p></div>", unsafe_allow_html=True)
            
            fig = px.bar(df.groupby('Ji\'a')['Kafaltii_Taj'].sum().reset_index(), x='Ji\'a', y='Kafaltii_Taj', title="Galii Ji'aan", color_discrete_sequence=['#2e7d32'])
            st.plotly_chart(fig, use_container_width=True)
        else: st.info("Data'n galmeeffame hin jiru.")

    # --- REGISTRATION ---
    elif menu == "📝 Galmee Haaraa":
        st.header("📝 Galmee Tajaajilaa Haaraa")
        with st.form(key="reg_form_v3", clear_on_submit=True):
            col1, col2 = st.columns(2)
            m_name = col1.text_input("Maqaa Abbaa Dhimmaa")
            m_ara = col2.text_input("Araddaa")
            m_oge = col1.text_input("Maqaa Ogeessaa")
            m_kaff = col2.number_input("Kafaltii (ETB)", min_value=0.0)
            m_gosa = st.selectbox("Gosa Tajaajilaa", ["Gibira", "Liizii", "Kaartaa", "Jijjiirraa Maqaa", "TOT"])
            
            if st.form_submit_button("💾 Galmeessi"):
                if m_name and m_oge:
                    new_row = [datetime.now().strftime('%d/%m/%Y'), m_name, m_ara, "N/A", m_gosa, m_oge, m_kaff]
                    df = pd.concat([df, pd.DataFrame([new_row], columns=COL_NAMES)], ignore_index=True)
                    save_data(df)
                    st.success(f"✅ Galmeen {m_name} sirriitti kuusameera!")
                else: st.error("Maaloo odeeffannoo guutuu galchi!")

    # --- GABAASA BAL'AA ---
    elif menu == "📈 Gabaasa Bal'aa":
        st.header("📈 Tarreeffama Gabaasaa")
        st.dataframe(df[COL_NAMES], use_container_width=True)
        
        # Download Excel
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df[COL_NAMES].to_excel(writer, index=False, sheet_name='Sheet1')
        st.download_button(label="📥 Gabaasa Excel Buusi", data=output.getvalue(), file_name="Gabaasa_Dadar.xlsx")

    # --- BADHAASA ---
    elif menu == "🏆 Badhaasa":
        st.header("🏆 Badhaasa Ogeeyyii")
        if not df.empty:
            top_3 = df['Maqaa_Ogeessa'].value_counts().head(3)
            cols = st.columns(3)
            for i, (name, count) in enumerate(top_3.items(), 1):
                with cols[i-1]:
                    st.markdown(f"<div class='card'><h3>{i}FFAA</h3><p><b>{name}</b></p><p>Hojii: {count}</p></div>", unsafe_allow_html=True)
                    pdf_data = create_pdf(name, count, i)
                    st.download_button(f"📥 Sartiifiketa {i}", pdf_data, f"Sartii_{name}.pdf", "application/pdf", key=f"pdf_{i}")
        else: st.warning("Data'n hojii ogeeyyii hin jiru.")

    # --- SEARCH & EDIT & DELETE ---
    elif menu == "🔍 Barbaadi/Sirreessi":
        st.header("🔍 Barbaadi fi Sirreessi")
        search_q = st.text_input("Maqaa maamilaa barreessi...")
        
        if search_q and not df.empty:
            results = df[df['Maqaa_Abbaa_Dhimmaa'].str.contains(search_q, case=False, na=False)]
            if not results.empty:
                for idx, row in results.iterrows():
                    with st.expander(f"📄 {row['Maqaa_Abbaa_Dhimmaa']} - {row['Guyyaa']}"):
                        with st.form(key=f"edit_form_{idx}"):
                            new_name = st.text_input("Maqaa", row['Maqaa_Abbaa_Dhimmaa'])
                            new_kaff = st.number_input("Kafaltii", float(row['Kafaltii_Taj']))
                            
                            c1, c2, _ = st.columns([1, 1, 2])
                            if c1.form_submit_button("💾 Update"):
                                df.at[idx, 'Maqaa_Abbaa_Dhimmaa'] = new_name
                                df.at[idx, 'Kafaltii_Taj'] = new_kaff
                                save_data(df)
                                st.success("Sirreeffameera!")
                                st.rerun()
                            
                            if c2.form_submit_button("🗑 Haqi"):
                                df = df.drop(idx)
                                save_data(df)
                                st.warning("Galmeen haqameera!")
                                st.rerun()
            else: st.error("Maqaan kun hin jiru!")
