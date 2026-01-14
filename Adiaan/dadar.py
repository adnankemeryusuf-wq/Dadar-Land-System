import streamlit as st
import pandas as pd
import os
import io
import requests
from datetime import datetime
from fpdf import FPDF

# ================= 1. CONFIGURATION & STYLE =================
st.set_page_config(page_title="Dadar Land Office", page_icon="🏢", layout="wide")

BOT_TOKEN = "8357193631:AAHCuSnXzjZTQaglkmcS0gq-EvqnkIQLDBI"
CHAT_ID_MANAGER = "7329587700"
LOGO_PATH = "Adiaan/logo.png"
DATA_FILE = "dadar_final_report.txt"

COL_NAMES = ['Guyyaa', 'Maqaa_Abbaa_Dhimmaa', 'Araddaa', 'Qaxana', 'Gosa_Tajajjilaa', 'Maqaa_Ogeessa', 'Kafaltii_Taj']
MONTH_ORDER = ["Fulbaana", "Onkololeessa", "Sadaasa", "Muddee", "Amajjii", "Guraandhala", "Bitootessa", "Eebila", "Caamsaa", "Waxabajjii", "Adooleessa", "Hagayya"]
MONTH_MAP = {9: "Fulbaana", 10: "Onkololeessa", 11: "Sadaasa", 12: "Muddee", 1: "Amajjii", 2: "Guraandhala", 3: "Bitootessa", 4: "Eebila", 5: "Caamsaa", 6: "Waxabajjii", 7: "Adooleessa", 8: "Hagayya"}

st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #f1f8e9 0%, #ffffff 100%); }
    [data-testid="stSidebar"] { background-color: #1b5e20 !important; }
    [data-testid="stSidebar"] * { color: #ffffff !important; }
    div.stForm { background: white; border-radius: 15px; padding: 25px; border: 2px solid #2e7d32; box-shadow: 0px 4px 15px rgba(0,0,0,0.1); }
    .card { background: white; padding: 20px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); text-align: center; border-top: 5px solid #2e7d32; margin-bottom: 10px; }
    .stButton>button { background: linear-gradient(90deg, #4caf50, #2e7d32); color: white; border-radius: 8px; font-weight: bold; width: 100%; height: 45px; border: none; }
    </style>
    """, unsafe_allow_html=True)

# ================= 2. FUNCTIONS =================
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

def create_advanced_pdf(name, count, rank, logo_l=None, logo_r=None):
    pdf = FPDF(orientation='L', unit='mm', format='A4')
    pdf.add_page()
    gold, green, bg = (255, 215, 0), (0, 80, 0), (255, 254, 245)
    pdf.set_fill_color(*bg); pdf.rect(10, 10, 277, 190, 'F')
    pdf.set_draw_color(*green); pdf.set_line_width(2.5); pdf.rect(10, 10, 277, 190)
    pdf.set_draw_color(*gold); pdf.set_line_width(1.0); pdf.rect(13, 13, 271, 184)

    if logo_l:
        with open("temp_l.png", "wb") as f: f.write(logo_l.getbuffer())
        pdf.image("temp_l.png", x=25, y=18, w=35)
    if logo_r:
        with open("temp_r.png", "wb") as f: f.write(logo_r.getbuffer())
        pdf.image("temp_r.png", x=235, y=18, w=35)

    pdf.set_y(45); pdf.set_text_color(*gold); pdf.set_font('Arial', 'B', 32)
    pdf.cell(0, 15, "SARTIIFIKETA BEEKAMTII", ln=True, align='C')
    pdf.set_y(65); pdf.set_text_color(*green); pdf.set_font('Arial', 'B', 22)
    pdf.cell(0, 12, "Waajjira Lafaa Bulchiinsa Magaalaa Dadar", ln=True, align='C')
    pdf.set_y(100); pdf.set_text_color(60, 60, 60); pdf.set_font('Arial', 'I', 18)
    pdf.cell(0, 8, "Sartiifiketiin kun kabajaan kan kennameef:", ln=True, align='C')
    pdf.set_text_color(*green); pdf.set_font('Arial', 'B', 26)
    pdf.cell(0, 22, f"Obbo/Adde: {name.upper()}", ln=True, align='C')
    pdf.set_font('Arial', '', 14); pdf.set_text_color(40, 40, 40)
    msg = "Waggaa 2026 keessatti tajaajila saffisaa, qulqulluu fi amannamaa ta'een tajaajila hawaasaa irratti gumaacha guddaa waan gumaachaniif badhaasa kanaan galateeffamaniiru."
    pdf.multi_cell(0, 9, msg, align='C')
    pdf.set_y(172); pdf.line(40, 172, 110, 172); pdf.line(180, 172, 250, 172)
    pdf.set_xy(40, 174); pdf.cell(70, 8, "Mallattoo Itti Gaafatamaa", align='C')
    pdf.set_xy(180, 174); pdf.cell(70, 8, f"Guyyaa: {datetime.now().strftime('%d/%m/%Y')}", align='C')
    return pdf.output(dest='S').encode('latin-1')

# ================= 3. MAIN APP =================
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    _, col_mid, _ = st.columns([1, 1.5, 1])
    with col_mid:
        st.markdown("<h2 style='text-align:center;'>🔐 Dadar Land Login</h2>", unsafe_allow_html=True)
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")
        if st.button("Seeni"):
            if u == "admin" and p == "123":
                st.session_state.logged_in = True
                st.rerun()
            else: st.error("Username ykn Password dogoggora!")
else:
    df = load_data()
    with st.sidebar:
        if os.path.exists(LOGO_PATH): st.image(LOGO_PATH, width=80)
        st.success("Deder City Land Office")
        menu = st.radio("FILANNOO", ["📊 Dashboard", "📝 Galmee Haaraa", "📈 Gabaasa Bal'aa", "🏆 Badhaasa Ogeeyyii", "🔍 Barbaadi/Edit", "Ba'i"])
        if st.button("Log Out"):
            st.session_state.logged_in = False
            st.rerun()

    if menu == "📊 Dashboard":
        st.title("📊 Dashboard")
        
        if not df.empty:
            c1, c2, c3 = st.columns(3)
            with c1: st.markdown(f"<div class='card'><h4>💰 Galii</h4><h2>{df['Kafaltii_Taj'].sum():,.2f}</h2><p>ETB</p></div>", unsafe_allow_html=True)
            with c2: st.markdown(f"<div class='card'><h4>👥 Maamiltoota</h4><h2>{len(df)}</h2><p>Waliigala</p></div>", unsafe_allow_html=True)
            with c3: st.markdown(f"<div class='card'><h4>👷 Ogeeyyii</h4><h2>{df['Maqaa_Ogeessa'].nunique()}</h2><p>Aktiiwii</p></div>", unsafe_allow_html=True)
            st.subheader("📈 Galii Ji'aan")
            chart = df.groupby('Ji\'a')['Kafaltii_Taj'].sum().reindex(MONTH_ORDER).fillna(0)
            st.area_chart(chart)
        else: st.info("Data'n galmeeffame hin jiru.")

    elif menu == "📝 Galmee Haaraa":
        st.header("📝 Galmee Tajaajilaa")
        GATII_DICT = {
            "Gibira": ["Gibira Baaxii Gooroo", "Gibira Lafa Qonnaa", "Gibira Manaa"],
            "Liizii": ["Liizii Waggaa", "Jijjiirraa Maqaa", "Kafaltii Liizii Duraa", "TOT"],
            "Ittii Fayyaddam": ["Hayyama Itti Fayyadama Lafaa", "Humna Mahandiisaa"],
            "Kaartaa": ["Kaartaa Manaa", "Kaartaa Kadastaara", "Kaartaa Haaromsuu"],
            "Dhimma Dangaa": ["Kafaltii Humna Mandisaa"],
            "Dhimma Mana Murtii": ["Ugura Mana Murtii", "Uguraa Mana Murtii Kaasuu"],
            "Liqii Bankii": ["Dorkka Liqii Bankii", "Dorkkaa Liqii Bankii Kaasuu"]
        }
        selected_main = st.multiselect("🟢 Gosa Tajaajilaa Filadhu", list(GATII_DICT.keys()))
        details, d_fees, is_tot = [], {}, False
        if selected_main:
            for g in selected_main:
                subs = st.multiselect(f"Tajaajila {g}:", GATII_DICT[g], key=f"m_{g}")
                for s in subs:
                    details.append(f"{g}({s})")
                    d_fees[f"{g}_{s}"] = st.number_input(f"Kafaltii {s} (ETB)", min_value=0.0, key=f"f_{g}_{s}")
                    if s == "TOT": is_tot = True

        with st.form("entry_form", clear_on_submit=True):
            if is_tot:
                col1, col2 = st.columns(2)
                maqaa_f = f"G: {col1.text_input('Maqaa Gurguraa')} / B: {col2.text_input('Maqaa Bitataa')}"
                ara_f = f"G: {col1.text_input('Araddaa G')} / B: {col2.text_input('Araddaa B')}"
                qax_f = f"G: {col1.text_input('Qaxana G')} / B: {col2.text_input('Qaxana B')}"
            else:
                c1, c2 = st.columns(2)
                maqaa_f, ara_f = c1.text_input("Maqaa Abbaa Dhimmaa"), c2.text_input("Araddaa")
                qax_f = c1.text_input("Qaxana")
            ogeessa = st.text_input("Maqaa Ogeessaa")
            if st.form_submit_button("💾 Galmeessi"):
                if maqaa_f and details and ogeessa:
                    new_row = [datetime.now().strftime('%d/%m/%Y'), maqaa_f, ara_f, qax_f, ", ".join(details), ogeessa, sum(d_fees.values())]
                    df = pd.concat([df, pd.DataFrame([new_row], columns=COL_NAMES)], ignore_index=True)
                    save_data(df); st.success("✅ Galmeeffameera!"); st.rerun()

    elif menu == "📈 Gabaasa Bal'aa":
        st.header("📈 Gabaasa & Telegram")
        st.dataframe(df[COL_NAMES], use_container_width=True)
        total = df['Kafaltii_Taj'].sum()
        st.metric("Galii Waliigalaa", f"{total:,.2f} ETB")
        buf = io.BytesIO()
        with pd.ExcelWriter(buf, engine='xlsxwriter') as wr: df[COL_NAMES].to_excel(wr, index=False)
        c1, c2 = st.columns(2)
        c1.download_button("📥 Excel Download", buf.getvalue(), "Gabaasa.xlsx")
        if c2.button("✈️ Telegram-itti Ergi"):
            if send_to_telegram(buf.getvalue(), "Gabaasa.xlsx", f"Gabaasa Dadar: {total} ETB"): st.success("✅ Ergameera!")

    elif menu == "🏆 Badhaasa Ogeeyyii":
        st.header("🏆 Badhaasa & Sartiifiikeeta")
        cl, cr = st.columns(2)
        logo_l = cl.file_uploader("Logo Bitaa", type=['png', 'jpg'], key="l_up")
        logo_r = cr.file_uploader("Logo Mirgaa", type=['png', 'jpg'], key="r_up")
        if not df.empty:
            top_3 = df['Maqaa_Ogeessa'].value_counts().head(3)
            cols = st.columns(3)
            for i, (name, count) in enumerate(top_3.items(), 1):
                with cols[i-1]:
                    st.markdown(f"<div class='card'><h2>{i}FFAA</h2><h3>{name}</h3><p>Tajaajila: {count}</p></div>", unsafe_allow_html=True)
                    pdf_bytes = create_advanced_pdf(name, count, i, logo_l, logo_r)
                    st.download_button(f"📥 PDF {i}ffaa", pdf_bytes, f"Cert_{name}.pdf", "application/pdf", key=f"btn_{i}")

    elif menu == "🔍 Barbaadi/Edit":
        st.header("🔍 Barbaadi fi Sirreessi")
        q = st.text_input("Maqaa Barbaadi...")
        if q and not df.empty:
            res = df[df['Maqaa_Abbaa_Dhimmaa'].str.contains(q, case=False, na=False)]
            for idx, row in res.iterrows():
                with st.expander(f"📄 {row['Maqaa_Abbaa_Dhimmaa']}"):
                    n_n = st.text_input("Maqaa", row['Maqaa_Abbaa_Dhimmaa'], key=f"n_{idx}")
                    n_f = st.number_input("Kafaltii", float(row['Kafaltii_Taj']), key=f"f_{idx}")
                    if st.button("💾 Update", key=f"u_{idx}"):
                        df.at[idx, 'Maqaa_Abbaa_Dhimmaa'], df.at[idx, 'Kafaltii_Taj'] = n_n, n_f
                        save_data(df); st.success("Sirreeffameera!"); st.rerun()
                    if st.button("🗑 Haqi", key=f"d_{idx}"):
                        df = df.drop(idx); save_data(df); st.rerun()

    elif menu == "Ba'i":
        st.session_state.logged_in = False
        st.rerun()

