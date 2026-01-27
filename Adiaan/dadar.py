import streamlit as st
import pandas as pd
import os
import requests
from datetime import datetime
from fpdf import FPDF
import plotly.express as px

# ================= 1. CONFIGURATION =================
LOGO_PATH = "Adiaan/logo.png"
DATA_FILE = "dadar_final_report.txt"
BOT_TOKEN = "8357193631:AAHCuSnXzjZTQaglkmcS0gq-EvqnkIQLDBI"
CHAT_ID_MANAGER = "7329587700"
COL_NAMES = ['Guyyaa', 'Maqaa_Abbaa_Dhimmaa', 'Araddaa', 'Qaxana', 'Gosa_Tajajjilaa', 'Maqaa_Ogeessa', 'Kafaltii_Taj']

# ================= 2. CORE FUNCTIONS =================
def load_data():
    if not os.path.exists(DATA_FILE) or os.stat(DATA_FILE).st_size == 0:
        return pd.DataFrame(columns=COL_NAMES)
    df = pd.read_csv(DATA_FILE, sep="|", names=COL_NAMES, header=None, encoding='utf-8')
    df['dt'] = pd.to_datetime(df['Guyyaa'], format='%d/%m/%Y', errors='coerce')
    df['Waggaa'] = df['dt'].dt.year
    df['Ji\'a'] = df['dt'].dt.month_name()
    df['Torbee'] = df['dt'].dt.isocalendar().week
    return df

def save_data(df_to_save):
    df_to_save[COL_NAMES].to_csv(DATA_FILE, sep="|", index=False, header=False, encoding="utf-8")

def create_pdf_cert(name, count, rank):
    pdf = FPDF(orientation='L', unit='mm', format='A4')
    pdf.add_page()
    pdf.set_draw_color(46, 125, 50)
    pdf.set_line_width(5); pdf.rect(10, 10, 277, 190)
    if os.path.exists(LOGO_PATH): pdf.image(LOGO_PATH, 130, 15, 30)
    pdf.set_y(50); pdf.set_font('Arial', 'B', 35); pdf.cell(0, 30, "SARTIIFIKEETA BEEKAMTII", 0, 1, 'C')
    pdf.set_font('Arial', '', 25); pdf.cell(0, 20, f"Obbo/Adde: {name}", 0, 1, 'C')
    pdf.set_font('Arial', 'I', 18); pdf.multi_cell(0, 15, f"Waggaa 2026 keessatti maamiltoota {count} tajaajiluun\nsadarkaa {rank}ffaa argachuuf badhaafaman.", align='C')
    pdf.set_y(165); pdf.set_font('Arial', 'B', 14); pdf.cell(0, 10, f"Guyyaa: {datetime.now().strftime('%d/%m/%Y')} | Mallattoo: ________________", 0, 1, 'C')
    return pdf.output(dest='S').encode('latin-1', 'replace')

# ================= 3. APP LOGIC =================
if 'logged_in' not in st.session_state: st.session_state.logged_in = False

if not st.session_state.logged_in:
    # Login section (Akkuma koodii kee isa duraa)
    st.session_state.logged_in = True # For testing, set to True
else:
    df = load_data()
    menu = st.sidebar.radio("FILANNOO", ["📊 Dashboard", "📝 Galmee Haaraa", "📈 Gabaasa Bal'aa", "🏆 Badhaasa Ogeeyyii", "🔍 Barbaadi/Edit", "Logout"])

    # --- 📈 GABAASA BAL'AA ---
    if menu == "📈 Gabaasa Bal'aa":
        st.header("📈 Gabaasa Bal'aa & Calaltuu")
        if not df.empty:
            c1, c2, c3 = st.columns(3)
            sel_y = c1.selectbox("Waggaa Filadhu", sorted(df['Waggaa'].dropna().unique(), reverse=True))
            sel_m = c2.selectbox("Ji'a Filadhu (Optional)", ["Hunda"] + list(df['Ji\'a'].unique()))
            
            f_df = df[df['Waggaa'] == sel_y]
            if sel_m != "Hunda": f_df = f_df[f_df['Ji\'a'] == sel_m]
            
            st.dataframe(f_df[COL_NAMES], use_container_width=True)
            st.metric(f"Galii Waliigalaa ({sel_m})", f"{f_df['Kafaltii_Taj'].sum():,.2f} ETB")
            st.plotly_chart(px.line(f_df, x='Guyyaa', y='Kafaltii_Taj', title="Trendii Kaffaltii"))

    # --- 🏆 BADHAASA OGEEYYII ---
    elif menu == "🏆 Badhaasa Ogeeyyii":
        st.header("🏆 Ogeeyyii Cimaa Waggaa")
        if not df.empty:
            top_og = df['Maqaa_Ogeessa'].value_counts().head(3)
            cols = st.columns(3)
            for i, (name, count) in enumerate(top_og.items()):
                with cols[i]:
                    st.markdown(f"""<div style="background:white; p:20px; border-radius:15px; border:2px solid #gold; text-align:center;">
                        <h3>🥇 Sadarkaa {i+1}</h3><h4>{name}</h4><p>Maamiltoota {count} tajaajile</p></div>""", unsafe_allow_html=True)
                    if st.button(f"Print Cert: {name}"):
                        cert = create_pdf_cert(name, count, i+1)
                        st.download_button(f"📥 Buufadhu {name}", cert, f"Badhaasa_{name}.pdf")

    # --- 🔍 BARBAADI/EDIT ---
    elif menu == "🔍 Barbaadi/Edit":
        st.header("🔍 Barbaadi, Sirreessi ykn Haqi")
        q = st.text_input("Maqaa Abbaa Dhimmaa Barbaadi...")
        if q:
            res = df[df['Maqaa_Abbaa_Dhimmaa'].str.contains(q, case=False, na=False)]
            if not res.empty:
                for idx, row in res.iterrows():
                    with st.expander(f"📄 {row['Maqaa_Abbaa_Dhimmaa']} - {row['Guyyaa']}"):
                        new_name = st.text_input("Maqaa Sirreessi", row['Maqaa_Abbaa_Dhimmaa'], key=f"n_{idx}")
                        new_fee = st.number_input("Kaffaltii", value=float(row['Kafaltii_Taj']), key=f"f_{idx}")
                        
                        col_b1, col_b2 = st.columns(2)
                        if col_b1.button("💾 Ol-kaayi (Update)", key=f"up_{idx}"):
                            df.at[idx, 'Maqaa_Abbaa_Dhimmaa'] = new_name
                            df.at[idx, 'Kafaltii_Taj'] = new_fee
                            save_data(df); st.success("Sirreeffameera!"); st.rerun()
                        
                        if col_b2.button("🗑 Haqi (Delete)", key=f"del_{idx}"):
                            df = df.drop(idx); save_data(df); st.warning("Haquun milkaa'eera!"); st.rerun()
            else: st.info("Maqaan kun hin jiru.")
