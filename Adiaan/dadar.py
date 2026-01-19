import streamlit as st
import pandas as pd
import os, io, tempfile, shutil, hashlib, requests
from datetime import datetime
from fpdf import FPDF

# ================= SECURITY =================
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID_MANAGER = os.getenv("CHAT_ID_MANAGER")

# ================= CONFIG =================
st.set_page_config("Dadar Land Admin Pro", layout="wide", page_icon="🏢")

DATA_FILE = "dadar_data.txt"
COLS = ["Guyyaa","Maqaa_Abbaa_Dhimmaa","Araddaa","Qaxana","Gosa_Tajaajilaa","Maqaa_Ogeessa","Kafaltii"]
MONTH_ORDER = ["Fulbaana","Onkololeessa","Sadaasa","Muddee","Amajjii","Guraandhala",
               "Bitootessa","Eebila","Caamsaa","Waxabajjii","Adooleessa","Hagayya"]
MONTH_MAP = {9:"Fulbaana",10:"Onkololeessa",11:"Sadaasa",12:"Muddee",
             1:"Amajjii",2:"Guraandhala",3:"Bitootessa",4:"Eebila",
             5:"Caamsaa",6:"Waxabajjii",7:"Adooleessa",8:"Hagayya"}

PASS_HASH = hashlib.sha256("123".encode()).hexdigest()

# ================= STYLE =================
st.markdown("""
<style>
.stApp {background: linear-gradient(135deg,#f1f8e9,#ffffff);}
[data-testid="stSidebar"]{background:#1b5e20;}
[data-testid="stSidebar"] *{color:white;}
.card{background:white;padding:20px;border-radius:12px;
box-shadow:0 4px 6px rgba(0,0,0,.1);text-align:center;
border-top:5px solid #2e7d32;}
.stButton>button{background:linear-gradient(90deg,#4caf50,#2e7d32);
color:white;font-weight:bold;width:100%;}
</style>
""", unsafe_allow_html=True)

# ================= DATA =================
def load_data():
    if not os.path.exists(DATA_FILE):
        return pd.DataFrame(columns=COLS)
    df = pd.read_csv(DATA_FILE, sep="|", names=COLS)
    df["Date"] = pd.to_datetime(df["Guyyaa"], format="%d/%m/%Y", errors="coerce")
    df["Waggaa"] = df["Date"].dt.year
    df["Ji'a"] = df["Date"].dt.month.map(MONTH_MAP)
    df["Ji'a"] = pd.Categorical(df["Ji'a"], categories=MONTH_ORDER, ordered=True)
    return df

def save_data(df):
    if os.path.exists(DATA_FILE):
        shutil.copy(DATA_FILE, DATA_FILE+".bak")
    df[COLS].to_csv(DATA_FILE, sep="|", index=False, header=False)

def send_telegram(file_bytes, name, caption):
    if not BOT_TOKEN: return False
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendDocument"
    files = {"document": (name, file_bytes)}
    data = {"chat_id": CHAT_ID_MANAGER, "caption": caption}
    return requests.post(url, files=files, data=data).status_code == 200

# ================= PDF =================
def generate_pdf(name, count, rank, logo_l=None, logo_r=None):
    pdf = FPDF("L","mm","A4")
    pdf.add_page()
    colors = {1:(212,175,55),2:(192,192,192),3:(205,127,50)}
    r,g,b = colors.get(rank,(27,94,32))

    pdf.set_fill_color(245,255,245)
    pdf.rect(10,10,277,190,"F")
    pdf.set_draw_color(r,g,b)
    pdf.set_line_width(4)
    pdf.rect(8,8,281,194)

    if logo_l:
        with tempfile.NamedTemporaryFile(delete=False,suffix=".png") as f:
            f.write(logo_l.getvalue()); pdf.image(f.name,20,15,35)
    if logo_r:
        with tempfile.NamedTemporaryFile(delete=False,suffix=".png") as f:
            f.write(logo_r.getvalue()); pdf.image(f.name,235,15,35)

    pdf.set_y(50)
    pdf.set_text_color(r,g,b)
    pdf.set_font("Arial","B",34)
    pdf.cell(0,20,"SARTIIFIKETA BEEKAMTII",ln=True,align="C")

    pdf.set_font("Arial","",18)
    pdf.set_text_color(40,40,40)
    pdf.cell(0,12,f"{name.upper()}",ln=True,align="C")
    pdf.ln(10)
    pdf.multi_cell(0,10,f"Tajaajila {count} sirnaan kennuun\nbeekamtii kana argateera.",align="C")

    return pdf.output(dest="S").encode("latin-1","replace")

# ================= LOGIN =================
if "login" not in st.session_state:
    st.session_state.login = False

if not st.session_state.login:
    st.title("🔐 Admin Login")
    u = st.text_input("Username")
    p = st.text_input("Password", type="password")
    if st.button("Seeni"):
        if u=="admin" and hashlib.sha256(p.encode()).hexdigest()==PASS_HASH:
            st.session_state.login=True; st.rerun()
        else:
            st.error("Dogoggora!")
    st.stop()

# ================= MAIN =================
df = load_data()

with st.sidebar:
    st.title("🏢 Dadar Admin")
    menu = st.radio("MENU",["📊 Dashboard","📝 Galmee","📈 Gabaasa","🏆 Badhaasa","🔍 Edit","🚪 Ba'i"])

# DASHBOARD
if menu=="📊 Dashboard":
    if not df.empty:
        c1,c2,c3 = st.columns(3)
        c1.markdown(f"<div class='card'><h3>💰 Galii</h3><h2>{df['Kafaltii'].sum():,.2f}</h2></div>",unsafe_allow_html=True)
        c2.markdown(f"<div class='card'><h3>👥 Maamiltoota</h3><h2>{len(df)}</h2></div>",unsafe_allow_html=True)
        c3.markdown(f"<div class='card'><h3>👷 Ogeeyyii</h3><h2>{df['Maqaa_Ogeessa'].nunique()}</h2></div>",unsafe_allow_html=True)
        st.line_chart(df.groupby("Ji'a")["Kafaltii"].sum())
    else: st.info("Data hin jiru")

# GALMEE
elif menu=="📝 Galmee":
    with st.form("f"):
        m = st.text_input("Maqaa")
        a = st.text_input("Araddaa")
        q = st.text_input("Qaxana")
        g = st.text_input("Gosa Tajaajilaa")
        o = st.text_input("Ogeessa")
        k = st.number_input("Kafaltii",0.0)
        if st.form_submit_button("Galmeessi"):
            df = pd.concat([df,pd.DataFrame([[datetime.now().strftime("%d/%m/%Y"),m,a,q,g,o,k]],columns=COLS)])
            save_data(df); st.success("Galmeeffameera")

# GABAASA
elif menu=="📈 Gabaasa":
    st.dataframe(df)
    buf = io.BytesIO()
    df.to_excel(buf,index=False)
    st.download_button("Excel",buf.getvalue(),"gabaasa.xlsx")
    if st.button("Telegram"):
        send_telegram(buf.getvalue(),"gabaasa.xlsx","Gabaasa Dadar")

# BADHAASA
elif menu=="🏆 Badhaasa":
    l = st.file_uploader("Logo Bitaa",["png","jpg"])
    r = st.file_uploader("Logo Mirgaa",["png","jpg"])
    top = df["Maqaa_Ogeessa"].value_counts().head(3)
    for i,(n,c) in enumerate(top.items(),1):
        pdf = generate_pdf(n,c,i,l,r)
        st.download_button(f"PDF {i}ffaa",pdf,f"{n}.pdf")

# EDIT
elif menu=="🔍 Edit":
    q = st.text_input("Barbaadi")
    res = df[df["Maqaa_Abbaa_Dhimmaa"].str.contains(q,na=False)]
    st.dataframe(res)

# LOGOUT
elif menu=="🚪 Ba'i":
    st.session_state.login=False; st.rerun()
