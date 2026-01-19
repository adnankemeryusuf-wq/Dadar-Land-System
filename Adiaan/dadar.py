import streamlit as st
import pandas as pd
import sqlite3
import os
from datetime import datetime
from fpdf import FPDF
import plotly.express as px
from io import BytesIO

# ================== CONFIG & DIRECTORIES ==================
DB_FILE = "dadar_land.db"
NAGAHEE_DIR = "nagahee_scan"
for folder in [NAGAHEE_DIR]:
    if not os.path.exists(folder): os.makedirs(folder)

st.set_page_config(page_title="Dadar Land System", page_icon="🏢", layout="wide")

# CSS Styling
st.markdown("""
<style>
.stApp { background-color: #f8fafc; }
div.stForm { background-color: white; border-radius: 15px; padding: 30px; box-shadow: 0 10px 25px rgba(0,0,0,0.05); }
[ data-testid="stMetricValue"] { color: #065f46; font-size: 28px; font-weight: bold; }
.card { background: white; padding: 20px; border-radius: 12px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); text-align: center; border-left: 5px solid #10b981; margin-bottom: 20px; }
#MainMenu, footer, header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ================== SERVICE STRUCTURE ==================
SERVICE_STRUCTURE = {
    "🏷 Gibira & Kaffaltii": ["Gibira Baaxii Gooroo", "Gibira Lafa Qonnaa", "Kaffaltii Liizii Waggaa", "TOT (Turnover Tax)"],
    "📜 Kaartaa & Qabiyyee": ["Kaartaa Haaraa", "Kaartaa Bakka Bu'aa"],
    "📂 Tajaajila Biroo": ["Clearance", "Deebii Iyyannoo"]
}

# ================== DATABASE HELPERS ==================
COL_NAMES = ['id','Guyyaa','Maqaa_Abbaa_Dhimmaa','Araddaa','Qaxana','Gosa_Tajajjilaa','Maqaa_Ogeessa','Kafaltii_Taj','Nagahee_Path']

def get_conn():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute(f"""
        CREATE TABLE IF NOT EXISTS galmee (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            Guyyaa TEXT, Maqaa_Abbaa_Dhimmaa TEXT, Araddaa TEXT, Qaxana TEXT,
            Gosa_Tajajjilaa TEXT, Maqaa_Ogeessa TEXT, Kafaltii_Taj REAL, Nagahee_Path TEXT
        )
    """)
    conn.commit()
    return conn

def load_data():
    conn = get_conn()
    df = pd.read_sql("SELECT * FROM galmee", conn)
    conn.close()
    if df.empty:
        df = pd.DataFrame(columns=COL_NAMES)
    return df

def save_row(row):
    conn = get_conn()
    c = conn.cursor()
    c.execute("""
        INSERT INTO galmee
        (Guyyaa, Maqaa_Abbaa_Dhimmaa, Araddaa, Qaxana, Gosa_Tajajjilaa, Maqaa_Ogeessa, Kafaltii_Taj, Nagahee_Path)
        VALUES (?,?,?,?,?,?,?,?)
    """, row)
    conn.commit()
    conn.close()

# ================== PDF GENERATION ==================
def generate_pro_pdf(pdf_type, name, data_row=None, logo_file=None):
    pdf = FPDF(orientation='P', unit='mm', format='A4')
    pdf.add_page()
    pdf.set_draw_color(16,185,129); pdf.set_line_width(0.8)
    pdf.rect(10,10,190,277)
    pdf.set_draw_color(30,41,59); pdf.set_line_width(0.2)
    pdf.rect(12,12,186,273)

    if logo_file:
        pdf.image(BytesIO(logo_file.getbuffer()), 90, 15, 30)

    pdf.set_y(50)
    pdf.set_font('Arial','B',16); pdf.cell(0,8,"BULCHIINSA MAGAALAA DADAR",0,1,'C')
    pdf.set_font('Arial','',12); pdf.cell(0,8,"WAJJIRA LAFA FI MANAA",0,1,'C')
    pdf.ln(10)
    pdf.set_font('Arial','B',14); pdf.set_text_color(16,185,129)
    title = "Clearance" if pdf_type=="Clearance" else "Certificate"
    pdf.cell(0,10,title,"B",1,'C')

    pdf.set_text_color(0,0,0); pdf.ln(15)
    pdf.set_font('Arial','',12)

    if pdf_type=="Clearance" and data_row is not None:
        content = f"Obbo/Adde {name}, Araddaa {data_row['Araddaa']} keessatti tajaajila '{data_row['Gosa_Tajajjilaa']}' ilaalchisee kaffaltii Birrii {data_row['Kafaltii_Taj']:,.2f} guutummaatti galmeessisanii jiru."
    else:
        total_clients = data_row.get('TotalClients',0) if data_row else 0
        content = f"Ogeessi Maqaan isaa {name}, waggaa 2026 keessatti maamiltoota {total_clients} tajaajiluun beekamtii ol-aanaa argataniiru."

    pdf.multi_cell(0,10,content,align='L')
    pdf.set_y(240)
    pdf.set_font('Arial','B',10)
    pdf.cell(90,10,"Mallattoo Ogeessaa",0,0,'L')
    pdf.cell(90,10,"Mallattoo Itti Gaafatamaa",0,1,'R')
    pdf.line(10,260,60,260); pdf.line(140,260,190,260)

    return pdf.output(dest='S').encode('latin-1','replace')

# ================== SESSION ==================
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'role' not in st.session_state: st.session_state.role = None

# ================== LOGIN ==================
if not st.session_state.logged_in:
    st.title("🏢 Dadar Land System")
    with st.form("Login"):
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")
        if st.form_submit_button("SEENI"):
            if u=="DAD" and p=="2026": st.session_state.logged_in, st.session_state.role = True,"admin"; st.rerun()
            elif u=="ogeessa" and p=="1234": st.session_state.logged_in, st.session_state.role = True,"user"; st.rerun()
            else: st.error("Maaloo odeeffannoo sirrii galchi!")

# ================== MAIN APP ==================
else:
    df = load_data()
    with st.sidebar:
        st.markdown(f"Logged in as: **{st.session_state.role.upper()}**")
        menu = st.radio("MENU", ["📊 Dashboard","📝 Galmee Haaraa","🏆 Badhaasa","🔍 Barbaadi & Clearance"])
        if st.button("Logout"): st.session_state.logged_in=False; st.rerun()

    # --- DASHBOARD ---
    if menu=="📊 Dashboard" and not df.empty:
        c1,c2,c3=st.columns(3)
        c1.metric("Waliigala Galii",f"{df['Kafaltii_Taj'].sum():,.2f} ETB")
        c2.metric("Maamiltoota",len(df))
        c3.metric("Ogeeyyii",df['Maqaa_Ogeessa'].nunique())
        fig1=px.pie(df, values='Kafaltii_Taj', names='Araddaa', hole=0.5)
        st.plotly_chart(fig1,use_container_width=True)
        fig2=px.bar(df, x='Maqaa_Ogeessa', y='Kafaltii_Taj', color='Gosa_Tajajjilaa')
        st.plotly_chart(fig2,use_container_width=True)
        st.download_button("📥 Gabaasa CSV", df.to_csv(index=False).encode('utf-8'),"Gabaasa_Dadar.csv","text/csv")

    # --- REGISTRATION ---
    elif menu=="📝 Galmee Haaraa":
        with st.form("RegForm"):
            c1,c2=st.columns(2)
            name=c1.text_input("Maqaa Abbaa Dhimmaa")
            ara=c1.text_input("Araddaa")
            gosa=c2.selectbox("Gosa Tajaajilaa", sum(SERVICE_STRUCTURE.values(),[]))
            fee=c2.number_input("Kaffaltii (ETB)", min_value=0.0)
            og=c1.text_input("Maqaa Ogeessaa")
            nagahee=st.file_uploader("Nagahee Scan", type=['jpg','png'])
            if st.form_submit_button("💾 GALMEESSI"):
                if name and og:
                    final_fee = fee*0.02 if 'TOT' in gosa else fee
                    path=""
                    if nagahee: path=os.path.join(NAGAHEE_DIR,f"{name}_{datetime.now().strftime('%H%M%S')}.jpg"); open(path,'wb').write(nagahee.getbuffer())
                    save_row([datetime.now().strftime('%d/%m/%Y'),name,ara,'-',gosa,og,final_fee,path])
                    st.success(f"Galmeeffameera! Kaffaltii: {final_fee:,.2f} ETB")

    # --- SEARCH & CLEARANCE ---
    elif menu=="🔍 Barbaadi & Clearance":
        search=st.text_input("Maqaa ykn Araddaa")
        if search and not df.empty:
            res=df[df['Maqaa_Abbaa_Dhimmaa'].str.contains(search,case=False)|df['Araddaa'].str.contains(search,case=False)]
            if not res.empty:
                for idx,row in res.iterrows():
                    st.markdown(f"<div class='card'><h4>{row['Maqaa_Abbaa_Dhimmaa']}</h4><p>{row['Gosa_Tajajjilaa']} | {row['Kafaltii_Taj']} ETB</p></div>",unsafe_allow_html=True)
                    pdf_data=generate_pro_pdf('Clearance',row['Maqaa_Abbaa_Dhimmaa'],row)
                    st.download_button(f"📥 Clearance PDF",pdf_data,f"Clearance_{row['Maqaa_Abbaa_Dhimmaa']}.pdf")
                    if st.session_state.role=='admin':
                        if st.button("🗑 Haqi",key=f"del_{idx}"):
                            conn=get_conn(); conn.execute("DELETE FROM galmee WHERE id=?",(row['id'],)); conn.commit(); conn.close(); st.rerun()

    # --- AWARDS ---
    elif menu=="🏆 Badhaasa" and not df.empty:
        logo_up=st.file_uploader("Logo Upload", type=['png','jpg'])
        top3=df['Maqaa_Ogeessa'].value_counts().head(3)
        cols=st.columns(3)
        for i,(og_name,count) in enumerate(top3.items()):
            with cols[i]:
                st.markdown(f"<div class='card'><h2>#{i+1}</h2><h3>{og_name}</h3><p>Tajaajila: {count}</p></div>",unsafe_allow_html=True)
                cert=generate_pro_pdf('Cert',og_name,{'TotalClients':count},logo_up)
                st.download_button(f"📥 Certificate",cert,f"Cert_{og_name}.pdf")
