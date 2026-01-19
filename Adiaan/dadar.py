import streamlit as st
import pandas as pd
import os
import io
from datetime import datetime
from fpdf import FPDF
import plotly.express as px

# ================= CONFIG =================
LOGO_PATH = "Adiaan/logo.png"
NAGAHEE_DIR = "nagahee_scan"
DATA_FILE = "dadar_final_report.txt"

if not os.path.exists(NAGAHEE_DIR):
    os.makedirs(NAGAHEE_DIR)

# Columns for CSV storage
COL_NAMES = ['Guyyaa','Maqaa_Abbaa_Dhimmaa','Araddaa','Qaxana','Gosa_Tajajjilaa','Maqaa_Ogeessa','Kafaltii_Taj']

# ================= STYLING =================
st.set_page_config(page_title="Dadar Land System", page_icon="🏢", layout="centered")
st.markdown("""
<style>
.stApp { background-color: #f4f7f9; }
div.stForm { background: white; border-radius: 12px; padding: 20px; border: 1px solid #ddd; }
.card { background: white; padding: 15px; border-radius: 7px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); text-align: center; }
</style>
""", unsafe_allow_html=True)

# ================= DATA FUNCTIONS =================
def load_data():
    if not os.path.exists(DATA_FILE) or os.stat(DATA_FILE).st_size == 0:
        return pd.DataFrame(columns=COL_NAMES)
    df = pd.read_csv(DATA_FILE, sep="|", names=COL_NAMES, header=None, encoding='utf-8')
    df['Kafaltii_Taj'] = pd.to_numeric(df['Kafaltii_Taj'], errors='coerce').fillna(0)
    df['Guyyaa'] = pd.to_datetime(df['Guyyaa'], format='%d/%m/%Y')
    df['Waggaa'] = df['Guyyaa'].dt.year
    df['Ji_a'] = df['Guyyaa'].dt.month
    df['Torbee'] = df['Guyyaa'].dt.isocalendar().week
    return df

def save_data(df):
    df[COL_NAMES].to_csv(DATA_FILE, sep="|", index=False, header=False, encoding="utf-8")

# ================= PDF CERTIFICATE =================
def create_pdf_cert(name, count, rank, logo_left=None, logo_right=None):
    pdf = FPDF(orientation='L', unit='mm', format='A4')
    pdf.add_page()
    
    # Border
    pdf.set_draw_color(0,100,0)
    pdf.set_line_width(2)
    pdf.rect(10,10,277,190)
    
    # Logos
    if logo_left: pdf.image(logo_left, 20, 15, 30)
    if logo_right: pdf.image(logo_right, 230, 15, 30)
    
    pdf.set_y(50)
    pdf.set_font('Arial','B',30)
    pdf.cell(0,10,"SARTIIFIKEETA BEEKAMTII",0,1,'C')
    pdf.set_font('Arial','',20)
    pdf.cell(0,20,f"Obbo/Adde: {name}",0,1,'C')
    pdf.set_font('Arial','',14)
    pdf.multi_cell(0,10,f"Waggaa 2026 keessatti maamiltoota {count} tajaajiluun sadarkaa {rank}ffaa argataniiru.", align='C')
    
    pdf.line(40,180,100,180)
    pdf.set_xy(40,182)
    pdf.cell(60,10,"Itti Gaafatamaa",align='C')
    
    return pdf.output(dest='S').encode('latin-1','replace')

# ================= SESSION =================
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'role' not in st.session_state: st.session_state.role = None

# ================= LOGIN =================
if not st.session_state.logged_in:
    if os.path.exists(LOGO_PATH):
        st.image(LOGO_PATH, width=50)
        st.title("Dadar Land Administration Customer Registration System")    
    with st.form("Login"):
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")
        if st.form_submit_button("Login"):
            if u=="admin" and p=="1234":
                st.session_state.logged_in=True
                st.session_state.role="admin"
                st.rerun()
            elif u=="staff" and p=="1234":
                st.session_state.logged_in=True
                st.session_state.role="staff"
                st.rerun()
            else:
                st.error("Login Dogoggora!")
else:
    # ================= SIDEBAR =================
    if os.path.exists(LOGO_PATH):
        st.sidebar.image(LOGO_PATH, use_container_width=True)
    st.sidebar.title("Main Menu")
    menu_options = ["📝 Galmee Haaraa","📊 Dashboard","📈 Gabaasa Bal'aa","🏆 Badhaasa Ogeeyyii","🔍 Barbaadi/Edit","Ba'i"]
    menu = st.sidebar.selectbox("Filannoo", menu_options)
    
    if st.sidebar.button("Logout"):
        st.session_state.logged_in=False
        st.rerun()
    
    df = load_data()
    
    # ================= DASHBOARD =================
    if menu=="📊 Dashboard":
        st.title("📊 Dashboard")
        if not df.empty:
            c1,c2,c3=st.columns(3)
            c1.metric("💰 Galii", f"{df['Kafaltii_Taj'].sum():,.2f} ETB")
            c2.metric("👥 Maamiltoota", len(df))
            c3.metric("👷 Ogeeyyii", df['Maqaa_Ogeessa'].nunique())
            
            fig=px.bar(df.groupby("Maqaa_Ogeessa")['Kafaltii_Taj'].sum().reset_index(), x="Maqaa_Ogeessa", y="Kafaltii_Taj", color='Maqaa_Ogeessa')
            st.plotly_chart(fig,use_container_width=True)
    
    # ================= REGISTRATION =================
    elif menu=="📝 Galmee Haaraa":
        st.title("📝 Galmee Tajaajilaa Haaraa")
        with st.form("RegForm"):
            c1,c2 = st.columns(2)
            name = c1.text_input("Maqaa Abbaa Dhimmaa")
            ara = c1.text_input("Araddaa")
            gosa = c2.selectbox("Gosa Tajaajilaa", ["Jijjiirraa Maqaa (Sale)","Kaartaa Haaraa","Waraqaa Qulqullummaa","TOT 2%","Adabbii"])
            fee = c2.number_input("Kaffaltii (ETB)", min_value=0.0)
            og = c1.text_input("Maqaa Ogeessaa")
            if st.form_submit_button("💾 GALMEESSI"):
                if name and og:
                    final_fee = fee*0.02 if "TOT" in gosa else fee
                    new_row = [datetime.now().strftime('%d/%m/%Y'), name, ara, "-", gosa, og, final_fee]
                    df = pd.concat([df,pd.DataFrame([new_row], columns=COL_NAMES)], ignore_index=True)
                    save_data(df)
                    st.success(f"Milkaa'inaan Galmeeffameera! Kaffaltii: {final_fee:,.2f} ETB")
    
    # ================= ADVANCED REPORT =================
    elif menu=="📈 Gabaasa Bal'aa":
        st.header("📈 Gabaasa & Calaltuu")
        if not df.empty:
            st.dataframe(df[COL_NAMES], use_container_width=True)
            st.metric("Galii Waliigala", f"{df['Kafaltii_Taj'].sum():,.2f} ETB")
    
    # ================= AWARDS =================
    elif menu=="🏆 Badhaasa Ogeeyyii":
        st.header("🏆 Sartiifiikeeta Ogeeyyii")
        if not df.empty:
            top_3 = df['Maqaa_Ogeessa'].value_counts().head(3)
            medals = ["🥇 1FFAA","🥈 2FFAA","🥉 3FFAA"]
            logo_left=st.file_uploader("Logo Bita", type=["png","jpg"])
            logo_right=st.file_uploader("Logo Mirga", type=["png","jpg"])
            for i,(name,count) in enumerate(top_3.items()):
                st.markdown(f"<div class='card'><h2>{medals[i]}</h2><h3>{name}</h3><p>Abbootii Dhimmaa: {count}</p></div>", unsafe_allow_html=True)
                pdf_bytes = create_pdf_cert(name,count,i+1,logo_left,logo_right)
                st.download_button(f"📥 Download {name} PDF", pdf_bytes, f"Cert_{name.replace(' ','_')}.pdf")
    
    # ================= SEARCH / EDIT =================
    elif menu=="🔍 Barbaadi/Edit":
        st.header("🔍 Barbaadi / Edit Galmee")
        q = st.text_input("Maqaa Barbaadi...")
        if q:
            res = df[df['Maqaa_Abbaa_Dhimmaa'].str.contains(q, case=False, na=False)]
            if not res.empty:
                for idx,row in res.iterrows():
                    with st.expander(f"{row['Maqaa_Abbaa_Dhimmaa']}"):
                        st.write(f"Araddaa: {row['Araddaa']} | Qaxana: {row['Qaxana']}")
                        st.write(f"Tajaajila: {row['Gosa_Tajajjilaa']} | Ogeessa: {row['Maqaa_Ogeessa']} | Kaffaltii: {row['Kafaltii_Taj']}")
                        if st.session_state.role=="admin":
                            confirm = st.checkbox(f"Dhugaa haquu barbaaddaa {row['Maqaa_Abbaa_Dhimmaa']}?", key=f"chk_{idx}")
                            if confirm and st.button("🗑 Haqi", key=f"del_{idx}"):
                                df = df.drop(idx)
                                save_data(df)
                                st.success(f"{row['Maqaa_Abbaa_Dhimmaa']} haqameera")
                                st.experimental_rerun()
    
    # ================= LOGOUT =================
    elif menu=="Ba'i":
        st.session_state.logged_in=False
        st.experimental_rerun()















