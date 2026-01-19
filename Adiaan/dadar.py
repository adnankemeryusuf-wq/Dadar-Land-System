import streamlit as st

import pandas as pd

import os

import io

import requests

from datetime import datetime

from fpdf import FPDF



# ================= 1. CONFIGURATION & DIRECTORIES =================

DATA_FILE = "dadar_final_report.txt"

NAGAHEE_DIR = "nagaheewwan"



# Directory'n nagahee yoo hin jirre uumi

if not os.path.exists(NAGAHEE_DIR):

    os.makedirs(NAGAHEE_DIR)



# Telegram Config

BOT_TOKEN = "8357193631:AAHCuSnXzjZTQaglkmcS0gq-EvqnkIQLDBI"

CHAT_ID_MANAGER = "7329587700"



st.set_page_config(page_title="Dadar Land Admin Pro", layout="wide", page_icon="🏢")



# Custom CSS for Professional Look

st.markdown("""

    <style>

    .stApp { background: linear-gradient(135deg, #f1f8e9 0%, #ffffff 100%); }

    [data-testid="stSidebar"] { background-color: #1b5e20 !important; }

    [data-testid="stSidebar"] * { color: #ffffff !important; }

    div.stForm { background: white; border-radius: 15px; padding: 25px; border: 2px solid #2e7d32; box-shadow: 0px 4px 15px rgba(0,0,0,0.1); }

    .card { background: white; padding: 20px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); text-align: center; border-top: 5px solid #2e7d32; margin-bottom: 10px; }

    .stButton>button { background: linear-gradient(90deg, #4caf50, #2e7d32); color: white; border-radius: 8px; font-weight: bold; width: 100%; height: 45px; }

    </style>

    """, unsafe_allow_html=True)



# ================= 2. DATA MANAGEMENT =================

COL_NAMES = ['Guyyaa', 'Maqaa_Abbaa_Dhimmaa', 'Araddaa', 'Qaxana', 'Gosa_Tajajjilaa', 'Maqaa_Ogeessa', 'Kafaltii_Taj']

MONTH_ORDER = ["Fulbaana", "Onkololeessa", "Sadaasa", "Muddee", "Amajjii", "Guraandhala", "Bitootessa", "Eebila", "Caamsaa", "Waxabajjii", "Adooleessa", "Hagayya"]

MONTH_MAP = {9: "Fulbaana", 10: "Onkololeessa", 11: "Sadaasa", 12: "Muddee", 1: "Amajjii", 2: "Guraandhala", 3: "Bitootessa", 4: "Eebila", 5: "Caamsaa", 6: "Waxabajjii", 7: "Adooleessa", 8: "Hagayya"}



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

    try:

        r = requests.post(url, files=files, data=data)

        return r.status_code == 200

    except: return False



# ================= 3. PDF GENERATOR =================

def create_advanced_pdf(name, count, rank, logo_l=None, logo_r=None):

    pdf = FPDF(orientation='L', unit='mm', format='A4')

    pdf.add_page()

    rank_colors = {1: (212, 175, 55), 2: (192, 192, 192), 3: (205, 127, 50)}

    r_c, g_c, b_c = rank_colors.get(rank, (27, 94, 32))



    pdf.set_fill_color(245, 255, 245); pdf.rect(12, 12, 273, 186, 'F')

    pdf.set_line_width(4); pdf.set_draw_color(r_c, g_c, b_c); pdf.rect(10, 10, 277, 190)



    if logo_l:

        with open("temp_l.png", "wb") as f: f.write(logo_l.getbuffer())

        pdf.image("temp_l.png", 20, 15, 35)

    if logo_r:

        with open("temp_r.png", "wb") as f: f.write(logo_r.getbuffer())

        pdf.image("temp_r.png", 240, 15, 35)



    pdf.set_y(50); pdf.set_text_color(r_c, g_c, b_c); pdf.set_font('Arial', 'B', 35)

    pdf.cell(0, 25, "SARTIIFIKETA BEEKAMTII", ln=True, align='C')

    

    pdf.set_text_color(50, 50, 50); pdf.set_font('Arial', 'B', 28)

    pdf.ln(10); pdf.cell(0, 20, f"{name.upper()}", ln=True, align='C')

    

    pdf.set_font('Arial', '', 16)

    msg = f"Waggaa 2026 keessatti maamiltoota {count} tajaajiluun sadarkaa {rank}ffaa argataniiru."

    pdf.multi_cell(0, 10, msg, align='C')

    

    return pdf.output(dest='S').encode('latin-1', 'replace')



 ================= 2. SERVICE LIST (GOSA TAJAAJILAA) =================

# Gosa tajaajilaa hunda akka gosa gurguddaatti addaan baasuu

SERVICE_STRUCTURE = {

    "🏷️ Gibira & Kaffaltii": [

        "Gibira Baaxii Gooroo", "Gibira Lafa Qonnaa", "Kaffaltii Liizii Waggaa", 

        "Kaffaltii Liizii Duraa", "Gibira Milkii (Stamp Duty)", "TOT (Turnover Tax)"

    ],

    "📜 Kaartaa & Qabiyyee": [

        "Kaartaa Haaraa", "Kaartaa Bakka Bu'aa", "Kaartaa Kadastaaraa", 

        "Jijjiirraa Maqaa (Gift/Sale)", "Sirreeffama Daangaa", "Ganda Irraa gara Magaalaatti"

    ],

    "🏗️ Pilaanii & Ijaarsa": [

        "Hayyama Ijaarsaa", "Pilaanii Magaalaa", "Itti Fayyadama Lafaa (Land Use)", 

        "Mirkaneessa Sertifikeeta Ijaarsaa", "Humna Mahandisummaa"

    ],

    "⚖️ Dhimma Seeraa": [

        "Ugura Mana Murtii", "Ugura Kaasuu", "Waliigaltee Liqii Baankii", 

        "Waliigaltee Hiikuu", "Dhimma Dhala (Inheritance)"

    ],

    "📂 Tajaajila Biroo": [

        "Waraqaa Ragaa (Clearance)", "Deebii Iyyannoo", "Tajaajila Koppii (Photocopy)"

    ]

}



if 'logged_in' not in st.session_state: st.session_state.logged_in = False



if not st.session_state.logged_in:

    _, col_mid, _ = st.columns([1, 1.2, 1])

    with col_mid:

        st.header("🏢 Admin Login")

        u, p = st.text_input("Username"), st.text_input("Password", type="password")

        if st.button("Seeni"):

            if u == "admin" and p == "123": st.session_state.logged_in = True; st.rerun()

            else: st.error("Dogoggora!")

else:

    df = load_data()

    menu = st.sidebar.radio("FILANNOO", ["📊 Dashboard", "📝 Galmee Haaraa", "📈 Gabaasa", "🏆 Badhaasa", "🔍 Barbaadi/Edit", "Ba'i"])



    if menu == "📊 Dashboard":

        st.header("📊 Dashboard Overview")

        if not df.empty:

            c1, c2, c3 = st.columns(3)

            c1.metric("💰 Galii Waliigalaa", f"{df['Kafaltii_Taj'].sum():,.2f} ETB")

            c2.metric("👥 Maamiltoota", len(df))

            c3.metric("👷 Ogeeyyii", df['Maqaa_Ogeessa'].nunique())

            st.area_chart(df.groupby('Ji\'a')['Kafaltii_Taj'].sum().reindex(MONTH_ORDER).fillna(0))



    elif menu == "📝 Galmee Haaraa":

        st.header("📝 Galmee Tajaajilaa Haaraa")

        selected_cats = st.multiselect("🟢 Ramaddii Tajaajilaa Filadhu", list(SERVICE_STRUCTURE.keys()))

        

        details, d_fees, is_tot = [], {}, False

        if selected_cats:

            for cat in selected_cats:

                subs = st.multiselect(f"Tajaajiloota {cat}:", SERVICE_STRUCTURE[cat], key=cat)

                for s in subs:

                    details.append(s)

                    d_fees[s] = st.number_input(f"Kaffaltii {s} (ETB):", min_value=0.0, key=f"f_{s}")

                    if "TOT" in s: is_tot = True



        with st.form("reg_form", clear_on_submit=True):

            if is_tot:

                col1, col2 = st.columns(2)

                maqaa_f = f"G: {col1.text_input('Maqaa Gurguraa')} / B: {col2.text_input('Maqaa Bitataa')}"

                ara_f = f"G: {col1.text_input('Araddaa G')} / B: {col2.text_input('Araddaa B')}"

                qax_f = f"G: {col1.text_input('Qaxana G')} / B: {col2.text_input('Qaxana B')}"

            else:

                c1, c2 = st.columns(2)

                maqaa_f, ara_f = c1.text_input("Maqaa Maamilaa"), c2.text_input("Araddaa")

                qax_f = c1.text_input("Qaxana")

            

            ogeessa = st.text_input("Maqaa Ogeessaa")

            nagahee = st.file_uploader("Nagahee (Scan)", type=['jpg','png'])



            if st.form_submit_button("💾 Galmeessi"):

                if maqaa_f and details and ogeessa:

                    if nagahee:

                        f_path = os.path.join(NAGAHEE_DIR, f"{datetime.now().strftime('%H%M%S')}.jpg")

                        with open(f_path, "wb") as f: f.write(nagahee.getbuffer())

                    

                    new_row = [datetime.now().strftime('%d/%m/%Y'), maqaa_f, ara_f, qax_f, ", ".join(details), ogeessa, sum(d_fees.values())]

                    df = pd.concat([df, pd.DataFrame([new_row], columns=COL_NAMES)], ignore_index=True)

                    save_data(df); st.success("✅ Galmeeffameera!")

                else: st.error("⚠️ Odeeffannoo guuti!")



    elif menu == "📈 Gabaasa":

        st.header("📈 Gabaasa Bal'aa")

        if not df.empty:

            st.dataframe(df[COL_NAMES], use_container_width=True)

            buf = io.BytesIO()

            with pd.ExcelWriter(buf, engine='xlsxwriter') as wr: df[COL_NAMES].to_excel(wr, index=False)

            st.download_button("📥 Excel Buusi", buf.getvalue(), "Gabaasa.xlsx")

            if st.button("✈️ Telegram-itti Ergi"):

                if send_to_telegram(buf.getvalue(), "Gabaasa.xlsx", "Gabaasa Har'aa"): st.success("Ergameera!")



    elif menu == "🏆 Badhaasa":

        st.header("🏆 Beekamtii Ogeeyyii")

        l_l = st.file_uploader("Logo Bitaa", type=['png','jpg'], key="ll")

        l_r = st.file_uploader("Logo Mirgaa", type=['png','jpg'], key="lr")

        if not df.empty:

            top_3 = df['Maqaa_Ogeessa'].value_counts().head(3)

            cols = st.columns(3)

            for i, (name, count) in enumerate(top_3.items(), 1):

                with cols[i-1]:

                    st.markdown(f"<div class='card'><h3>{i}FFAA</h3><p>{name}</p></div>", unsafe_allow_html=True)

                    pdf = create_advanced_pdf(name, count, i, l_l, l_r)

                    st.download_button(f"📥 Sartiifikeeta", pdf, f"Cert_{name}.pdf")



    elif menu == "Ba'i":

        st.session_state.logged_in = False; st.rerun()
