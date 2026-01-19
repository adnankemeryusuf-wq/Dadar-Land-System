import streamlit as st
import pandas as pd
import os, io, requests
from datetime import datetime
from fpdf import FPDF
import plotly.express as px

# ================= CONFIG =================
LOGO_PATH = "Adiaan/logo.png"
DATA_FILE = "dadar_final_report.txt"
BOT_TOKEN = "8357193631:AAHCuSnXzjZTQaglkmcS0gq-EvqnkIQLDBI"
CHAT_ID_MANAGER = "7329587700"
COL_NAMES = ['Guyyaa', 'Maqaa_Abbaa_Dhimmaa', 'Araddaa', 'Qaxana', 'Gosa_Tajajjilaa', 'Maqaa_Ogeessa', 'Kafaltii_Taj']
MONTH_ORDER = ["Fulbaana","Onkololeessa","Sadaasa","Muddee","Amajjii","Guraandhala","Bitootessa","Eebila","Caamsaa","Waxabajjii","Adooleessa","Hagayya"]
MONTH_MAP = {9:"Fulbaana",10:"Onkololeessa",11:"Sadaasa",12:"Muddee",1:"Amajjii",2:"Guraandhala",3:"Bitootessa",4:"Eebila",5:"Caamsaa",6:"Waxabajjii",7:"Adooleessa",8:"Hagayya"}

st.set_page_config(page_title="Dadar Land Admin Pro", page_icon=LOGO_PATH if os.path.exists(LOGO_PATH) else "🏢", layout="wide")

# ================= STYLE =================
st.markdown("""
<style>
.stApp { background: linear-gradient(135deg, #f1f8e9 0%, #ffffff 100%); }
[data-testid="stSidebar"] { background-color: #1b5e20 !important; }
[data-testid="stSidebar"] * { color: #ffffff !important; }
div.stForm { background: white; border-radius: 15px; padding: 25px; border: 2px solid #2e7d32; box-shadow: 0px 4px 15px rgba(0,0,0,0.1); }
.card { background: white; padding: 20px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); text-align: center; border-top: 5px solid #2e7d32; margin-bottom: 15px; }
.stButton>button { background: linear-gradient(90deg, #4caf50, #2e7d32); color: white; border-radius: 8px; font-weight: bold; width: 100%; height: 45px; border: none; transition: 0.3s;}
.stButton>button:hover { background: linear-gradient(90deg, #66bb6a, #2e7d32); cursor: pointer;}
</style>
""", unsafe_allow_html=True)

# ================= CORE FUNCTIONS =================
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

def send_to_telegram(file_data, file_name, caption):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendDocument"
    files = {'document': (file_name, file_data)}
    data = {'chat_id': CHAT_ID_MANAGER, 'caption': caption}
    try: return requests.post(url, files=files, data=data).status_code == 200
    except: return False

def send_report_telegram(df):
    import io
    # Excel
    excel_buf = io.BytesIO()
    with pd.ExcelWriter(excel_buf, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name="Gabaasa")
    excel_buf.seek(0)
    # Plotly Chart
    fig = px.bar(df.groupby("Maqaa_Ogeessa")["Kafaltii_Taj"].sum().reset_index(),
                 x="Maqaa_Ogeessa", y="Kafaltii_Taj",
                 title="Galii Ogeeyyii", color="Kafaltii_Taj", color_continuous_scale="Greens")
    chart_buf = io.BytesIO()
    fig.write_image(chart_buf, format='png')
    chart_buf.seek(0)
    # Send
    send_to_telegram(excel_buf.getvalue(), "Gabaasa.xlsx", "📊 Gabaasa Excel")
    send_to_telegram(chart_buf.getvalue(), "Chart.png", "📈 Chart Galii Ogeeyyii")

# ================= LOGIN =================
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if not st.session_state.logged_in:
    with st.form("login_form"):
        st.markdown("### Login")
        u = st.text_input("Username", placeholder="admin")
        p = st.text_input("Password", type="password", placeholder="••••••")
        if st.form_submit_button("Seeni"):
            if u=="admin" and p=="123":
                st.session_state.logged_in = True
                st.rerun()
            else:
                st.error("Dogoggora username ykn password!")
    st.stop()

# ================= MAIN APP =================
df = load_data()
with st.sidebar:
    st.title("🏢 Dadar Admin")
    menu = st.radio("FILANNOO", ["📊 Dashboard", "📝 Galmee Haaraa", "📈 Gabaasa Bal'aa", "🏆 Badhaasa Ogeeyyii", "🔍 Barbaadi/Edit"])
    if st.button("Log Out"): st.session_state.logged_in=False; st.rerun()

# ---------- DASHBOARD ----------
if menu=="📊 Dashboard":
    st.markdown("### 📊 Dashboard Waliigalaa")
    c1,c2,c3 = st.columns(3)
    with c1: st.markdown(f"<div class='card'><p>💰 Galii Waliigalaa</p><h2>{df['Kafaltii_Taj'].sum():,.2f} ETB</h2></div>", unsafe_allow_html=True)
    with c2: st.markdown(f"<div class='card'><p>👥 Maamiltoota</p><h2>{len(df)}</h2></div>", unsafe_allow_html=True)
    with c3: st.markdown(f"<div class='card'><p>🏆 Ogeessa Filatamaa</p><h2>{df['Maqaa_Ogeessa'].mode()[0] if not df.empty else '-'}</h2></div>", unsafe_allow_html=True)
    st.subheader("📈 Galii Ogeeyyii")
    fig = px.bar(df.groupby("Maqaa_Ogeessa")["Kafaltii_Taj"].sum().reset_index(),
                 x="Maqaa_Ogeessa", y="Kafaltii_Taj", color="Kafaltii_Taj",
                 color_continuous_scale="Greens", text="Kafaltii_Taj", title="Galii Ogeeyyii")
    fig.update_traces(texttemplate='%{text:,.0f}', textposition='outside')
    st.plotly_chart(fig, use_container_width=True)

# ---------- REGISTRATION ----------
elif menu=="📝 Galmee Haaraa":
    st.header("📝 Galmee Tajaajilaa")
    name = st.text_input("Maqaa Abbaa Dhimmaa")
    ogeessa = st.text_input("Maqaa Ogeessaa")
    kafaltii = st.number_input("Kafaltii (ETB)", min_value=0.0)
    if st.button("💾 Galmeessi") and name and ogeessa:
        new_row = [datetime.now().strftime('%d/%m/%Y'), name, "", "", "", ogeessa, kafaltii]
        df = pd.concat([df,pd.DataFrame([new_row], columns=COL_NAMES)], ignore_index=True)
        save_data(df)
        st.success("✅ Galmeeffameera!")

# ---------- REPORT ----------
elif menu=="📈 Gabaasa Bal'aa":
    st.header("📈 Gabaasa Bal'aa")
    if not df.empty:
        st.dataframe(df, use_container_width=True)
        buf = io.BytesIO()
        with pd.ExcelWriter(buf, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name="Gabaasa")
        buf.seek(0)
        st.download_button("📥 Excel Buusi", buf.getvalue(), "Gabaasa.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        if st.button("✈️ Telegramitti Ergi"):
            send_report_telegram(df)
            st.success("✅ Telegram ergameera!")
    else:
        st.info("Data hin jiru.")

# ---------- BADHAASA ----------
elif menu=="🏆 Badhaasa Ogeeyyii":
    st.header("🏆 Sadarkaa Ogeeyyii")
    if not df.empty:
        top3 = df['Maqaa_Ogeessa'].value_counts().head(3)
        colors = ["#FFD700","#C0C0C0","#CD7F32"]
        for i,(name,count) in enumerate(top3.items()):
            st.markdown(f"<div class='card' style='border-top:5px solid {colors[i]};'><h3>{name}</h3><p>Hojii Raawwatame: {count}</p></div>", unsafe_allow_html=True)

# ---------- SEARCH/EDIT ----------
elif menu=="🔍 Barbaadi/Edit":
    st.header("🔍 Barbaadi fi Sirreessi")
    q = st.text_input("Maqaa Abbaa Dhimmaa...")
    if q:
        res = df[df['Maqaa_Abbaa_Dhimmaa'].str.contains(q, case=False, na=False)]
        st.dataframe(res, use_container_width=True)

# ================= MULTI-SERVICE REGISTRATION =================
GATII_DICT = {
    "Gibira": ["Gibira Baaxii", "Gibira Qonnaa"],
    "Liizii": ["Liizii Waggaa", "Jijjiirraa Maqaa", "TOT"],
    "Ittii Fayyaddam": ["Hayyama Itti Fayyadama Lafaa", "Humna Mahandiisaa"],
    "Kaartaa": ["Kaartaa Lafa", "Kaartaa Kadastaara"],
    "Dhimma Dangaa": ["Kafaltii Humna Mandisaa"],
    "Dhimma Mana Murtii": ["Ugura Mana Murtii", "Uguraa Mana Murtii Kaasuu"],
    "Liqii Bankii": ["Dorkka Liqii Bankii"]
}

# Multi-service Form
elif menu=="📝 Galmee Haaraa":
    st.header("📝 Galmee Tajaajilaa")
    selected_main = st.multiselect("Gosa Tajaajilaa Filadhu", list(GATII_DICT.keys()))
    details, d_fees, is_tot = [], {}, False
    if selected_main:
        for g in selected_main:
            subs = st.multiselect(f"Tajaajila {g}:", GATII_DICT[g], key=f"m_{g}")
            for s in subs:
                details.append(f"{g}({s})")
                d_fees[f"{g}_{s}"] = st.number_input(f"Kafaltii {s} (ETB)", min_value=0.0, key=f"f_{g}_{s}")
                if s == "TOT": is_tot = True

    name = st.text_input("Maqaa Abbaa Dhimmaa")
    ogeessa = st.text_input("Maqaa Ogeessaa")

    if st.button("💾 Galmeessi") and name and details and ogeessa:
        new_row = [datetime.now().strftime('%d/%m/%Y'), name, "", "", ", ".join(details), ogeessa, sum(d_fees.values())]
        df = pd.concat([df,pd.DataFrame([new_row], columns=COL_NAMES)], ignore_index=True)
        save_data(df)
        st.success("✅ Galmeeffameera!")

# ================= PDF CERTIFICATES =================
def create_pdf_certificate(name, count, rank):
    pdf = FPDF(orientation='L', unit='mm', format='A4')
    pdf.add_page()
    colors = [(255,215,0),(192,192,192),(205,127,50)]
    rank_color = colors[rank-1] if rank<=3 else (0,80,0)
    pdf.set_draw_color(*rank_color)
    pdf.set_line_width(3)
    pdf.rect(10,10,277,190)
    pdf.set_font("Arial","B",30)
    pdf.cell(0,30,"SARTIIFIKETA BEEKAMTII",ln=True,align="C")
    pdf.set_font("Arial","B",22)
    pdf.cell(0,20,name.upper(),ln=True,align="C")
    pdf.set_font("Arial","",16)
    pdf.multi_cell(0,10,f"Waggaa 2026 tajaajila {count} kennuun sadarkaa {rank}ffaa argateera.", align="C")
    return pdf.output(dest="S").encode("latin-1")

# PDF for top 3 employees
elif menu=="🏆 Badhaasa Ogeeyyii":
    st.header("🏆 Sadarkaa Ogeeyyii")
    if not df.empty:
        top3 = df['Maqaa_Ogeessa'].value_counts().head(3)
        colors = ["#FFD700","#C0C0C0","#CD7F32"]
        for i,(name,count) in enumerate(top3.items()):
            st.markdown(f"<div class='card' style='border-top:5px solid {colors[i]};'><h3>{name}</h3><p>Hojii Raawwatame: {count}</p></div>", unsafe_allow_html=True)
            pdf_file = create_pdf_certificate(name,count,i+1)
            st.download_button(label=f"📥 Sartiifiketa {i+1}", data=pdf_file, file_name=f"{name}_certificate.pdf", mime="application/pdf")
