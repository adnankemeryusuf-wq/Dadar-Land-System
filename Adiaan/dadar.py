import streamlit as st
import pandas as pd
import sqlite3
import os
from datetime import datetime
from fpdf import FPDF
import plotly.express as px

# ================= CONFIG =================
DB_FILE = "dadar_land.db"
NAGAHEE_DIR = "nagahee_scan"
LOGO_PATH = "Adiaan/logo.png"

if not os.path.exists(NAGAHEE_DIR):
    os.makedirs(NAGAHEE_DIR)

COL_NAMES = ['id','date','customer_name','araddaa','qaxana','service_type','staff_name','payment','nagahee_path']

# ================= DATABASE =================
def get_conn():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            customer_name TEXT,
            araddaa TEXT,
            qaxana TEXT,
            service_type TEXT,
            staff_name TEXT,
            payment REAL,
            nagahee_path TEXT
        )
    """)
    conn.commit()
    return conn

def load_data():
    conn = get_conn()
    df = pd.read_sql("SELECT * FROM records", conn)
    conn.close()
    if not df.empty:
        # Safely convert to datetime; invalid dates become NaT
        df['date'] = pd.to_datetime(df['date'], format='%d/%m/%Y', errors='coerce')
        df['year'] = df['date'].dt.year
        df['month'] = df['date'].dt.month
        df['week'] = df['date'].dt.isocalendar().week
    return df

def save_row(row):
    conn = get_conn()
    c = conn.cursor()
    c.execute("""
        INSERT INTO records
        (date, customer_name, araddaa, qaxana, service_type, staff_name, payment, nagahee_path)
        VALUES (?,?,?,?,?,?,?,?)
    """, row)
    conn.commit()
    conn.close()

def delete_row(record_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute("DELETE FROM records WHERE id=?", (record_id,))
    conn.commit()
    conn.close()

# ================= PDF CERTIFICATE =================
def create_pdf_cert(name, count, rank, logo_left=None, logo_right=None):
    pdf = FPDF(orientation='L', unit='mm', format='A4')
    pdf.add_page()
    pdf.set_draw_color(0,100,0)
    pdf.set_line_width(2)
    pdf.rect(10,10,277,190)
    
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

# ================= STYLING =================
st.set_page_config(page_title="Dadar Land System", page_icon="🏢", layout="Centered")
st.markdown("""
<style>
.stApp { background-color: #f4f7f9; }
div.stForm { background: white; border-radius: 12px; padding: 20px; border: 1px solid #ddd; }
.card { background: white; padding: 15px; border-radius: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); text-align: center; margin-bottom: 20px; }
</style>
""", unsafe_allow_html=True)

# ================= SESSION =================
if 'logged_in' not in st.session_state: st.session_state.logged_in=False
if 'role' not in st.session_state: st.session_state.role=None

# ================= LOGIN =================
USER_CREDENTIALS = {"admin":"1234","staff":"1234"}

if not st.session_state.logged_in:
    if os.path.exists(LOGO_PATH): st.image(LOGO_PATH, width=120)
    st.title("W/Bulchiinsa Lafaa Magaalaa Dadar")
    with st.form("Login"):
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")
        if st.form_submit_button("Login"):
            if u in USER_CREDENTIALS and p==USER_CREDENTIALS[u]:
                st.session_state.logged_in=True
                st.session_state.role=u
                st.rerun()
            else:
                st.error("Login Dogoggora!")
else:
    # ================= SIDEBAR =================
    if os.path.exists(LOGO_PATH): st.sidebar.image(LOGO_PATH, use_container_width=True)
    st.sidebar.title("Main Menu")
    menu_options = ["📝 Galmee Haaraa","📊 Dashboard","📈 Gabaasa Bal'aa","🏆 Badhaasa Ogeeyyii","🔍 Barbaadi/Edit"]
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
            c1.metric("💰 Galii", f"{df['payment'].sum():,.2f} ETB")
            c2.metric("👥 Maamiltoota", len(df))
            c3.metric("👷 Ogeeyyii", df['staff_name'].nunique())
            
            fig=px.bar(df.groupby("staff_name")['payment'].sum().reset_index(), x="staff_name", y="payment", color='staff_name', title="Raawwii Ogeeyyii")
            st.plotly_chart(fig,use_container_width=True)
    
    # ================= REGISTRATION =================
    elif menu=="📝 Galmee Haaraa":
        st.title("📝 Galmee Tajaajilaa Haaraa")
        with st.form("RegForm"):
            c1,c2 = st.columns(2)
            name = c1.text_input("Maqaa Abbaa Dhimmaa")
            ara = c1.text_input("Araddaa")
            qax = c1.text_input("Qaxana")
            gosa = c2.selectbox("Gosa Tajaajilaa", ["Jijjiirraa Maqaa (Sale)","Kaartaa Haaraa","Waraqaa Qulqullummaa","TOT 2%","Adabbii"])
            fee = c2.number_input("Kaffaltii (ETB)", min_value=0.0)
            og = c1.text_input("Maqaa Ogeessaa")
            nagahee = st.file_uploader("Nagahee Scan (JPG/PNG)", type=["jpg","png","jpeg"])
            
            if st.form_submit_button("💾 Galmeessi"):
                if name and og:
                    path=""
                    if nagahee:
                        path=os.path.join(NAGAHEE_DIR,f"{name}_{datetime.now().strftime('%H%M%S')}.jpg")
                        with open(path,"wb") as f: f.write(nagahee.getbuffer())
                    final_fee = fee*0.02 if "TOT" in gosa else fee
                    save_row([datetime.now().strftime('%d/%m/%Y'), name, ara, qax, gosa, og, final_fee, path])
                    st.success(f"✅ Galmeeffameera! Kaffaltii: {final_fee:,.2f} ETB")
    
    # ================= ADVANCED REPORT =================
    elif menu=="📈 Gabaasa Bal'aa":
        st.header("📈 Gabaasa & Calaltuu")
        if not df.empty:
            st.dataframe(df[COL_NAMES[1:]], use_container_width=True)
            st.metric("Galii Waliigala", f"{df['payment'].sum():,.2f} ETB")
    
    # ================= AWARDS =================
    elif menu=="🏆 Badhaasa Ogeeyyii":
        st.header("🏆 Sartiifiikeeta Ogeeyyii")
        if not df.empty:
            top_3 = df['staff_name'].value_counts().head(3)
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
            res = df[df['customer_name'].str.contains(q, case=False, na=False)]
            if not res.empty:
                for idx,row in res.iterrows():
                    with st.expander(f"{row['customer_name']}"):
                        st.write(f"Araddaa: {row['araddaa']} | Qaxana: {row['qaxana']}")
                        st.write(f"Tajaajila: {row['service_type']} | Ogeessa: {row['staff_name']} | Kaffaltii: {row['payment']}")
                        if st.session_state.role=="admin":
                            confirm = st.checkbox(f"Dhugaa haquu barbaaddaa {row['customer_name']}?", key=f"chk_{idx}")
                            if confirm and st.button("🗑 Haqi", key=f"del_{idx}"):
                                delete_row(row['id'])
                                st.success(f"{row['customer_name']} haqameera")
                                st.experimental_rerun()
    
    # ================= LOGOUT =================
    elif menu=="Ba'i":
        st.session_state.logged_in=False
        st.experimental_rerun()


