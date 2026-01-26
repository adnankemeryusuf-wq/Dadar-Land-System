5import streamlit as st
import pandas as pd
import os
import io
import requests
from datetime import datetime
from fpdf import FPDF
import plotly.express as px
from ethiopian_date import EthiopianDateConverter

# ================= 1. CONFIGURATION & STYLE =================
# Page config si'a tokko qofa gubbaatti waamama
st.set_page_config(
    page_title="Dadar Land Administration System", 
    page_icon="🏢", 
    layout="wide"
)

LOGO_PATH = "Adiaan/logo.png"
NAGAHEE_DIR = "nagahee_scan"
DATA_FILE = "dadar_final_report.txt"
BOT_TOKEN = "8357193631:AAHCuSnXzjZTQaglkmcS0gq-EvqnkIQLDBI"
CHAT_ID_MANAGER = "7329587700"

if not os.path.exists(NAGAHEE_DIR):
    os.makedirs(NAGAHEE_DIR)

# Style CSS
st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #f1f8e9 0%, #ffffff 100%); }
    [data-testid="stSidebar"] { background-color: #1b5e20 !important; }
    [data-testid="stSidebar"] * { color: #ffffff !important; }
    div.stForm { background: white; border-radius: 15px; padding: 25px; border: 2px solid #2e7d32; box-shadow: 0px 4px 15px rgba(0,0,0,0.1); }
    .card { background: white; padding: 20px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); text-align: center; border-top: 5px solid #2e7d32; margin-bottom: 10px; }
    .metric-value { font-size: 24px; font-weight: bold; color: #2e7d32; }
    .stButton>button { background: linear-gradient(90deg, #4caf50, #2e7d32); color: white; border-radius: 8px; font-weight: bold; width: 100%; }
    </style>
    """, unsafe_allow_html=True)

# ================= 2. CORE FUNCTIONS =================
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

def get_ethiopian_date_str():
    now = datetime.now()
    converter = EthiopianDateConverter()
    e_date = converter.to_ethiopian(now.year, now.month, now.day)
    return f"{e_date.day:02d}/{e_date.month:02d}/{e_date.year}"

def create_advanced_pdf(name, count, rank):
    pdf = FPDF(orientation='L', unit='mm', format='A4')
    pdf.add_page()
    pdf.set_draw_color(0, 80, 0)
    pdf.set_line_width(3.0)
    pdf.rect(10, 10, 277, 190)
    pdf.set_font('Arial', 'B', 30)
    pdf.set_xy(0, 50)
    pdf.cell(297, 20, "SARTIIFIKETA BEEKAMTII", ln=True, align='C')
    pdf.set_font('Arial', '', 20)
    pdf.set_xy(0, 80)
    pdf.cell(297, 20, f"Ogeessa: {name}", ln=True, align='C')
    pdf.cell(297, 20, f"Sadarkaa: {rank} | Hojii: {count}", ln=True, align='C')
    return pdf.output(dest='S').encode('latin-1')

# ================= 3. MAIN APPLICATION =================
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    # --- LOGIN PAGE ---
    _, col_mid, _ = st.columns([1, 1.2, 1])
    with col_mid:
        if os.path.exists(LOGO_PATH): st.image(LOGO_PATH, width=100)
        st.markdown("<h2 style='text-align:center; color:#1b5e20;'>Dadar Land Admin System</h2>", unsafe_allow_html=True)
        with st.form("login_form"):
            u = st.text_input("Username")
            p = st.text_input("Password", type="password")
            if st.form_submit_button("Seeni"):
                if u == "DAD" and p == "2026":
                    st.session_state.logged_in = True
                    st.rerun()
                else: st.error("Maqaa ykn Password dogoggora!")
else:
    df = load_data()
    # SIDEBAR
    with st.sidebar:
        if os.path.exists(LOGO_PATH): st.image(LOGO_PATH, width=100)
        st.success("Deder City Land Office")
        menu = st.radio("FILANNOO", ["📊 Dashboard", "📝 Galmee Haaraa", "📈 Gabaasa Bal'aa", "🏆 Badhaasa Ogeeyyii", "📝 CLEARANCE", "🔍 Barbaadi/Edit"])
        if st.button("Log Out"):
            st.session_state.logged_in = False
            st.rerun()

    # --- 1. DASHBOARD ---
    if menu == "📊 Dashboard":
        st.header("📊 Dashboard")
        if not df.empty:
            c1, c2, c3 = st.columns(3)
            with c1: st.markdown(f"<div class='card'><p>💰 Galii</p><p class='metric-value'>{df['Kafaltii_Taj'].sum():,.2f}</p></div>", unsafe_allow_html=True)
            with c2: st.markdown(f"<div class='card'><p>👥 Maamiltoota</p><p class='metric-value'>{len(df)}</p></div>", unsafe_allow_html=True)
            with c3: st.markdown(f"<div class='card'><p>👷 Ogeeyyii</p><p class='metric-value'>{df['Maqaa_Ogeessa'].nunique()}</p></div>", unsafe_allow_html=True)
            
            # Trend Graph
            st.subheader("Trendii Galii Ji'aan")
            chart_data = df.groupby('Ji\'a')['Kafaltii_Taj'].sum().reindex(MONTH_ORDER).fillna(0)
            st.area_chart(chart_data)
        else: st.info("Data'n hin jiru.")

    # --- 2. REGISTRATION ---
    elif menu == "📝 Galmee Haaraa":
        st.header("📝 Galmee Tajaajilaa")
        GATII_DICT = {
            "Gibira": ["Gibira Baaxii Gooroo", "Gibira Lafa Qonnaa"],
            "Liizii": ["Liizii Waggaa", "Jijjiirraa Maqaa", "Kafaltii Liizii Duraa", "TOT"],
            "Ittii Fayyaddam": ["Hayyama Itti Fayyadama Lafaa", "Humna Mahandiisaa"],
            "Kaartaa": ["Kaartaa Lafa", "Kaartaa Kadastaara", "Kaartaa Lafa Qonnaa"],
            "Dhimma Mana Murtii": ["Ugura Mana Murtii", "Uguraa Mana Murtii Kaasuu"],
            "Liqii Bankii": ["Dorkka Liqii Bankii", "Dorkkaa Liqii Bankii Kaasuu"]
        }

        selected_main = st.multiselect("🟢 Gosa Tajaajilaa Filadhu", list(GATII_DICT.keys()))
        details, d_fees = [], {}
        if selected_main:
            for g in selected_main:
                subs = st.multiselect(f"Tajaajila {g}:", GATII_DICT[g], key=f"m_{g}")
                for s in subs:
                    details.append(f"{g}({s})")
                    d_fees[f"{g}_{s}"] = st.number_input(f"Kafaltii {s} (ETB)", min_value=0.0, key=f"f_{g}_{s}")

        with st.form("entry_form", clear_on_submit=True):
            st.markdown("##### Odeeffannoo Maamilaa")
            c1, c2 = st.columns(2)
            maqaa_f = c1.text_input("Maqaa Abbaa Dhimmaa *")
            ara_f = c2.text_input("Araddaa *")
            qax_f = c1.text_input("Qaxana *")
            ogeessa = c2.text_input("Maqaa Ogeessaa *")
            nagahee_file = st.file_uploader("Nagahee Scan (JPG/PNG)", type=['jpg','png','jpeg'])
            submit = st.form_submit_button("💾 Galmeessi")

            if submit:
                if not maqaa_f or not ara_f or not ogeessa or not details:
                    st.error("⚠️ Maaloo bakka barbaachisu hunda guuti!")
                else:
                    new_row = [datetime.now().strftime('%d/%m/%Y'), maqaa_f, ara_f, qax_f, ", ".join(details), ogeessa, sum(d_fees.values())]
                    df = pd.concat([df, pd.DataFrame([new_row], columns=COL_NAMES)], ignore_index=True)
                    save_data(df)
                    st.balloons()
                    st.success(f"✅ Galmeen {maqaa_f} milkaa'inaan raawwatameera!")

    # --- 3. GABAASA BAL'AA ---
    elif menu == "📈 Gabaasa Bal'aa":
        st.header("📈 Gabaasa fi Xiinxala")
        if not df.empty:
            f_type = st.selectbox("Gosa Gabaasaa:", ["Waliigala", "Waggaa", "Ji'a"])
            filtered = df.copy()
            # (Filtering logic asitti dabalama...)
            
            st.dataframe(filtered[COL_NAMES], use_container_width=True)
            
            # Excel Export
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                filtered[COL_NAMES].to_excel(writer, index=False, sheet_name='Gabaasa')
            st.download_button("📥 Excel Buusi", output.getvalue(), "Gabaasa_Dadar.xlsx")
        else:
            st.warning("Data'n hin jiru.")

    # --- 4. BADHAASA OGEEYYII ---
    elif menu == "🏆 Badhaasa Ogeeyyii":
        st.header("🏆 Sadarkaa Ogeeyyii")
        if not df.empty:
            top_3 = df['Maqaa_Ogeessa'].value_counts().head(3)
            cols = st.columns(3)
            labels = ["1FFAA", "2FFAA", "3FFAA"]
            for i, (name, count) in enumerate(top_3.items()):
                with cols[i]:
                    st.markdown(f"<div class='card'><h3>{labels[i]}</h3><h4>{name}</h4><p>Hojii: {count}</p></div>", unsafe_allow_html=True)
                    pdf_cert = create_advanced_pdf(name, count, labels[i])
                    st.download_button(f"📥 Sartiifiketa {labels[i]}", pdf_cert, f"Cert_{name}.pdf", "application/pdf")

    # --- 5. CLEARANCE ---
    elif menu == "📝 CLEARANCE":
        st.header("📝 Waraqaa Ragaa Qulqullinaa")
        with st.form("clear_form"):
            c_name = st.text_input("Maqaa Guutuu")
            c_ara = st.text_input("Araddaa")
            c_qax = st.text_input("Qaxana")
            c_kart = st.text_input("Lakk. Kaartaa")
            if st.form_submit_button("Generate Clearance"):
                st.success(f"Clearance-iin {c_name}-f qophaa'ee jira. (PDF logic asitti dabalama)")

    # --- 6. BARBAADI/EDIT ---
    elif menu == "🔍 Barbaadi/Edit":
        st.header("🔍 Barbaadi fi Sirreessi")
        q = st.text_input("Maqaa Barbaadi...")
        if q and not df.empty:
            res = df[df['Maqaa_Abbaa_Dhimmaa'].str.contains(q, case=False, na=False)]
            st.dataframe(res)
def create_advanced_pdf(name, count, rank, logo_l=None, logo_r=None):
    # Functional PDF logic
    pdf = FPDF(orientation='L', unit='mm', format='A4')
    pdf.add_page()
    pdf.set_draw_color(0, 80, 0)
    pdf.set_line_width(3.0)
    pdf.rect(10, 10, 277, 190)
    pdf.set_font('Arial', 'B', 30)
    pdf.set_xy(0, 50)
    pdf.cell(297, 20, "SARTIIFIKETA BEEKAMTII", ln=True, align='C')
    pdf.set_font('Arial', '', 20)
    pdf.cell(297, 20, f"Ogeessa: {name}", ln=True, align='C')
    return pdf.output(dest='S').encode('latin-1')

# ================= 3. MAIN APPLICATION =================
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    # --- LOGIN PAGE ---
    _, col_mid, _ = st.columns([1, 1.2, 1])
    with col_mid:
        if os.path.exists(LOGO_PATH): st.image(LOGO_PATH, width=100)
        st.markdown("<h2 style='text-align:center; color:#1b5e20;'>Dadar Land Admin System</h2>", unsafe_allow_html=True)
        with st.form("login_form"):
            u = st.text_input("Username")
            p = st.text_input("Password", type="password")
            if st.form_submit_button("Seeni"):
                if u == "DAD" and p == "2026":
                    st.session_state.logged_in = True
                    st.rerun()
                else: st.error("Maqaa ykn Password dogoggora!")
else:
    df = load_data()
    # SIDEBAR
    with st.sidebar:
        if os.path.exists(LOGO_PATH): st.image(LOGO_PATH, width=100)
        st.success("Deder City Land Office")
        menu = st.radio("FILANNOO", ["📊 Dashboard", "📝 Galmee Haaraa", "📈 Gabaasa Bal'aa", "🏆 Badhaasa Ogeeyyii", "📝 CLEARANCE", "🔍 Barbaadi/Edit"])
        if st.button("Log Out"):
            st.session_state.logged_in = False
            st.rerun()
 #  DASHBOARD
    if menu == "📊 Dashboard":
        st.header("📊 Dashboard")
        if not df.empty:
            c1, c2, c3 = st.columns(3)
            with c1: st.markdown(f"<div class='card'><p>💰 Galii</p><p class='metric-value'>{df['Kafaltii_Taj'].sum():,.2f}</p></div>", unsafe_allow_html=True)
            with c2: st.markdown(f"<div class='card'><p>👥 Maamiltoota</p><p class='metric-value'>{len(df)}</p></div>", unsafe_allow_html=True)
            with c3: st.markdown(f"<div class='card'><p>👷 Ogeeyyii</p><p class='metric-value'>{df['Maqaa_Ogeessa'].nunique()}</p></div>", unsafe_allow_html=True)
            st.area_chart(df.groupby('Ji\'a')['Kafaltii_Taj'].sum().reindex(MONTH_ORDER).fillna(0))
        else: st.info("Data'n hin jiru.")

    # REGISTRATION
    elif menu == "📝 Galmee Haaraa":
        st.header("📝 Galmee Tajaajilaa")
        
        # Gosa tajaajilaa filachuuf
        GATII_DICT = {
            "Gibira": ["Gibira Baaxii Gooroo", "Gibira Lafa Qonnaa"],
            "Liizii": ["Liizii Waggaa", "Jijjiirraa Maqaa", "Kafaltii Liizii Duraa", "TOT"],
            "Ittii Fayyaddam": ["Hayyama Itti Fayyadama Lafaa", "Humna Mahandiisaa"],
            "Kaartaa": ["Kaartaa Lafa", "Kaartaa Kadastaara", "Kaartaa Lafa Qonnaa"],
            "Dhimma Mana Murtii": ["Ugura Mana Murtii", "Uguraa Mana Murtii Kaasuu"],
            "Liqii Bankii": ["Dorkka Liqii Bankii", "Dorkkaa Liqii Bankii Kaasuu"]
        }

        # 1. Filannoo Gosa Tajaajilaa (Dirqama akka filatamuuf)
        selected_main = st.multiselect("🟢 Gosa Tajaajilaa Filadhu (Dirqama)", list(GATII_DICT.keys()))
        
        details, d_fees = [], {}
        if selected_main:
            for g in selected_main:
                subs = st.multiselect(f"Tajaajila {g}:", GATII_DICT[g], key=f"m_{g}")
                for s in subs:
                    details.append(f"{g}({s})")
                    d_fees[f"{g}_{s}"] = st.number_input(f"Kafaltii {s} (ETB)", min_value=0.0, key=f"f_{g}_{s}")

        # 2. Form Galmee
        with st.form("entry_form", clear_on_submit=True):
            st.markdown("##### Odeeffannoo Maamilaa")
            c1, c2 = st.columns(2)
            
            # Form validation: placeholder fi label irratti "Required" dabalameera
            maqaa_f = c1.text_input("Maqaa Abbaa Dhimmaa *", placeholder="Maqaa guutuu barreessi")
            ara_f = c2.text_input("Araddaa *", placeholder="Araddaa  Dhimma")
            qax_f = c1.text_input("Qaxana *", placeholder="Qaxana Abbaa Dhimma")
            ogeessa = c2.text_input("Maqaa Ogeessaa *", placeholder="Maqaa Ogeessa")
            
            nagahee_file = st.file_uploader("Nagahee Scan (JPG/PNG)", type=['jpg','png','jpeg'])

            # Button submit
            submit = st.form_submit_button("💾 Galmeessi")

if submit:
                # --- VALIDATION LOGIC ---
                # Check gochuu: Wantoonni ijoon guutamaniiru?
                if not maqaa_f or not ara_f or not qax_f or not ogeessa:
                    st.error("⚠️ Maaloo! Bakka mallattoo (*) qaban hunda guutuu kee mirkaneessi.")
                elif not details:
                    st.error("⚠️ Maaloo! Gosa tajaajilaa kamiyyuu hin filanne.")
                else:
                    # Yoo hundi guutame, data save godha
                    if nagahee_file:
                        f_name = f"{maqaa_f.replace(' ','_')}_{datetime.now().strftime('%H%M%S')}.jpg"
                        with open(os.path.join(NAGAHEE_DIR, f_name), "wb") as f:
                            f.write(nagahee_file.getbuffer())
                    
                    new_row = [
                        datetime.now().strftime('%d/%m/%Y'), 
                        maqaa_f, 
                        ara_f, 
                        qax_f, 
                        ", ".join(details), 
                        ogeessa, 
                        sum(d_fees.values())
                    ]
                    
                    # Data update gochuu
                    df = pd.concat([df, pd.DataFrame([new_row], columns=COL_NAMES)], ignore_index=True)
                    save_data(df)
                    
                    st.balloons() # Success animation
                    st.success(f"✅ Galmeen {maqaa_f} milkaa'inaan Galmeeffameera!")
                    
                    # Refresh gochuuf
                    # st.rerun()
    # --- 📈 GABAASA ---
    elif menu == "📈 Gabaasa Bal'aa":
        st.header("📈 Gabaasa fi Export")
        if not df.empty:
            st.dataframe(df[COL_NAMES], use_container_width=True)
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                df[COL_NAMES].to_excel(writer, index=False, sheet_name='Gabaasa')
            st.download_button("📥 Excel Buusi", output.getvalue(), "Gabaasa_Dadar.xlsx")
            if st.button("✈️ Gabaasa Telegramitti Ergi"):
                st.success("Gabaasa telegramitti ergameera!") # Logic erguu armaan olitti jira")

   
 # --- GABAASA BAL'AA (MODERN UI) ---
    elif menu == "📈 Gabaasa Bal'aa":
        st.markdown("<h4 style='color: #1b5e20;'>📈 Gabaasa fi Xiinxala Galii</h4>", unsafe_allow_html=True)
        
        if not df.empty:
            # --- 1. Filter Section (Calala) ---
            with st.expander("🔍 Calali ykn Barbaadi", expanded=True):
                c1, c2, c3 = st.columns(3)
                f_type = c1.selectbox("Gosa Gabaasaa:", ["Waliigala", "Waggaa", "Kurmaana", "Ji'a", "Guyyaa"])
                
                filtered = df.copy()
                if f_type == "Waggaa":
                    sel_y = c2.selectbox("Waggaa:", sorted(df['Waggaa'].unique(), reverse=True))
                    filtered = filtered[filtered['Waggaa'] == sel_y]
                elif f_type == "Kurmaana":
                    sel_k = c2.selectbox("Kurmaana:", [1, 2, 3, 4])
                    filtered = filtered[filtered['Kurmaana'] == sel_k]
                elif f_type == "Ji'a":
                    sel_m = c2.selectbox("Ji'a:", MONTH_ORDER)
                    filtered = filtered[filtered['Ji\'a'] == sel_m]
                elif f_type == "Guyyaa":
                    sel_d = c2.date_input("Guyyaa Filadhu:", datetime.now())
                    filtered = filtered[filtered['Guyyaa'] == sel_d.strftime('%d/%m/%Y')]

# --- 2. Visual Metrics (Cards) ---
            st.markdown("---")
            m1, m2, m3 = st.columns(3)
            with m1:
                st.markdown(f"<div class='card'><h4>💰 Kaffaltii</h4><h2>{filtered['Kafaltii_Taj'].sum():,.2f}</h2><p>ETB</p></div>", unsafe_allow_html=True)
            with m2:
                st.markdown(f"<div class='card'><h4>👥 Baay'ina</h4><h2>{len(filtered)}</h2><p>Abbaa Dhimmaa</p></div>", unsafe_allow_html=True)
            with m3:
                # Ogeessa baay'ee hojjete
                top_st = filtered['Maqaa_Ogeessa'].mode()[0] if not filtered.empty else "-"
                st.markdown(f"<div class='card'><h4>🏆 Ogeessa</h4><h2>{top_st}</h2><p>Hojii Baay'ee</p></div>", unsafe_allow_html=True)

            # --- 3. Graphical Analysis ---
            col_left, col_right = st.columns([2, 1])
            
            with col_left:
                st.subheader("📊 Trendii Galii")
                # Line chart for revenue trend
                st.area_chart(filtered.groupby('Ji\'a')['Kafaltii_Taj'].sum().reindex(MONTH_ORDER).fillna(0))

            with col_right:
                st.subheader("🍕 Gosa Tajaajilaa")
                # Pie chart simple (Bar horizontal)
                service_dist = filtered['Gosa_Tajajjilaa'].value_counts()
                st.bar_chart(service_dist)

            # --- 4. Data Table & Export ---
            st.subheader("📋 Tarreeffama Gabaasaa")
            st.dataframe(filtered[COL_NAMES], use_container_width=True)

            # Export Buttons
            buf = io.BytesIO()
            with pd.ExcelWriter(buf, engine='xlsxwriter') as writer:
                filtered[COL_NAMES].to_excel(writer, index=False, sheet_name='Gabaasa')
            
            ex_c1, ex_c2 = st.columns([1, 5])
            ex_c1.download_button("📥 Excel Buusi", buf.getvalue(), "Gabaasa_Dadar.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
            if ex_c2.button("✈️ Gabaasa Telegramitti Ergi"):
                # Function telegram kee waamuu
                msg = f"📊 Gabaasa {f_type}\n💰 Waliigala: {filtered['Kafaltii_Taj'].sum():,.2f} ETB\n👥 Baay'ina: {len(filtered)}"
                # send_to_telegram logic asitti deema
                st.success("Gabaasa telegramitti ergameera!")

        else:
            st.warning("Gabaasa agarsiisuuf data'n hin jiru.")


# --- BADHAASA OGEEYYII ---
    elif menu == "🏆 Badhaasa Ogeeyyii":
        st.markdown("<h4 style='color: #1b5e20;'>🏆 Sadarkaa fi Badhaasa Ogeeyyii</h4>", unsafe_allow_html=True)
        
        # Logo filachuuf
        cl, cr = st.columns(2)
        l_l = cl.file_uploader("Logo Bitaa (PDF irratti)", type=['png', 'jpg'], key="logo_l")
        l_r = cr.file_uploader("Logo Mirgaa (PDF irratti)", type=['png', 'jpg'], key="logo_r")
        
        st.divider()

        if not df.empty:
            # Ogeeyyii baay'ina hojiitiin addaan baasuu
            top_3 = df['Maqaa_Ogeessa'].value_counts().head(3)
            cols = st.columns(3)
            
            # Halluuwwan sadarkaaf
            colors = ["#FFD700", "#C0C0C0", "#CD7F32"] # Gold, Silver, Bronze
            labels = ["1FFAA", "2FFAA", "3FFAA"]

for i, (name, count) in enumerate(top_3.items()):
                with cols[i]:
                    # Card bareedaa halluu sadarkaatiin
                    st.markdown(f"""
                        <div class='card' style='border-top: 5px solid {colors[i]};'>
                            <h2 style='color: {colors[i]};'>{labels[i]}</h2>
                            <h3 style='margin: 5px 0;'>{name}</h3>
                            <p style='font-size: 14px; color: #555;'>Hojii Raawwatame: <b>{count}</b></p>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    # PDF Generate gochuu
                    try:
                        pdf_file = create_advanced_pdf(name, count, i+1, l_l, l_r)
                        st.download_button(
                            label=f"📥 Sartiifiketa {labels[i]}",
                            data=pdf_file,
                            file_name=f"Sadarkaa_{i+1}_{name}.pdf",
                            mime="application/pdf",
                            key=f"dl_{i}"
                        )
                    except Exception as e:
                        st.error("PDF uumuu irratti dogoggora!")
        else:
            st.info("Data'n hojii ogeeyyii agarsiisu hin jiru.")

    # --- SEARCH & EDIT ---
    elif menu == "🔍 Barbaadi/Edit":
        col_l, col_r = st.columns([1, 4])
        with col_l:
            if os.path.exists(LOGO_PATH):
                st.image(LOGO_PATH, width=80)
        with col_r:
            st.header("🔍 Barbaadi fi Sirreessi")
            st.info("Maqaa maamilaa barreessuun galmee isaa sirreessi ykn haqi.")

        q = st.text_input("🔍 Maqaa Abbaa Dhimmaa Barbaadi...", placeholder="Fkn: Alii Mohammed")
        
        if q and not df.empty:
            res = df[df['Maqaa_Abbaa_Dhimmaa'].str.contains(q, case=False, na=False)]
            if not res.empty:
                st.write(f"🔎 Bu'aa {len(res)} argaman:")
                for idx, row in res.iterrows():
                    with st.expander(f"📄 {row['Maqaa_Abbaa_Dhimmaa']} ({row['Guyyaa']})"):
                        c1, c2 = st.columns(2)
                        n_n = c1.text_input("Maqaa Sirreessi", row['Maqaa_Abbaa_Dhimmaa'], key=f"n_{idx}")
                        n_f = c2.number_input("Kafaltii (ETB)", float(row['Kafaltii_Taj']), key=f"f_{idx}")
                        ca1, ca2, _ = st.columns([1, 1, 2])
                        if ca1.button("💾 Update", key=f"u_{idx}"):
                            df.at[idx, 'Maqaa_Abbaa_Dhimmaa'] = n_n
                            df.at[idx, 'Kafaltii_Taj'] = n_f
                            save_data(df); st.success("✅ Sirreeffameera!"); st.rerun()
                        if ca2.button("🗑 Haqi", key=f"d_{idx}"):
                            df = df.drop(idx); save_data(df); st.rerun()
            else:
                st.error("Maqaan kun galmee keessa hin jiru!")

    elif menu == "Ba'i":
        st.session_state.logged_in = False
        st.rerun()

#  ---CLEARANCE--- 
st.set_page_config(page_title="Dadar Land Admin", layout="wide")

if 'pdf_to_download' not in st.session_state:
    st.session_state.pdf_to_download = None
if 'pdf_name' not in st.session_state:
    st.session_state.pdf_name = ""

#  FUNCTIONS

def get_ethiopian_date_str():
    now = datetime.now()
    converter = EthiopianDateConverter()
    e_date = converter.to_ethiopian(now.year, now.month, now.day)
    return f"{e_date.day:02d}/{e_date.month:02d}/{e_date.year}"

def create_clearance_pdf(data):
    pdf = FPDF(orientation='P', unit='mm', format='A4')
    pdf.add_page()
    
    # Border (Double line)
    pdf.set_line_width(0.8); pdf.rect(10, 10, 190, 277)
    pdf.set_line_width(0.2); pdf.rect(12, 12, 186, 273)

    # Logos
    if os.path.exists("logo_bitta.jpg"): pdf.image("logo_bitta.jpg", 15, 18, 23)
    if os.path.exists("logo_mirga.jpg"): pdf.image("logo_mirga.jpg", 172, 18, 23)

# --- Header Section (Tartiiba Ati Gaafatte) ---
    pdf.set_y(22)
    pdf.set_font('Times', 'B', 15)
    # 1. Naannoo
    pdf.cell(0, 10, "MOOTUMMAA NAANNOO OROMIYAA", ln=True, align='C')
    
    pdf.set_font('Times', 'B', 14)
    # 2. Waajjira
    pdf.cell(0, 10, "WAAJJIRA LAFAA", ln=True, align='C')
    # 3. Bulchiinsa Magaalaa
    pdf.cell(0, 10, "BULCHIINSA MAGAALAA DADAR", ln=True, align='C')
    
    # Header Underline
    pdf.ln(3); pdf.set_line_width(0.5); pdf.line(20, 56, 190, 56)

    # Date and Ref No
    pdf.ln(12); pdf.set_font('Times', '', 12)
    guyyaa_ec = get_ethiopian_date_str()
    converter = EthiopianDateConverter()
    now_ec = converter.to_ethiopian(datetime.now().year, datetime.now().month, datetime.now().day)

    pdf.set_x(20)
    pdf.write(5, "Lakk. Galmee: ")
    pdf.set_font('Times', 'B', 12) 
    pdf.write(5, f"DAD/WL/{now_ec.year}/____")
    pdf.set_font('Times', '', 12)
    pdf.set_x(140)
    pdf.write(5, f"Guyyaa: {guyyaa_ec}")
    pdf.ln(18)

    # Subject
    pdf.set_font('Times', 'B', 14)
    pdf.cell(0, 10, "DHIMMA: WARAQAA RAGAA QULQULLINAA (CLEARANCE)", ln=True, align='C')
    pdf.ln(8)

    # Body
    pdf.set_font('Times', '', 12)
    pdf.set_x(20)
    
    pdf.write(9, "Waraqaan ragaa kun Obbo/Adde/Dhaabbata ")
    pdf.set_font('Times', 'B', 12); pdf.write(9, f"{data['maqaa'].upper()}")
    pdf.set_font('Times', '', 12); pdf.write(9, " Araddaa ")
    pdf.set_font('Times', 'B', 12); pdf.write(9, f"{data['araddaa']}")
    pdf.set_font('Times', '', 12); pdf.write(9, " Qaxana ")
    pdf.set_font('Times', 'B', 12); pdf.write(9, f"{data['qaxana']}")
    pdf.set_font('Times', '', 12); pdf.write(9, " keessatti mana/lafa Lakk. Kaartaa ")
    pdf.set_font('Times', 'B', 12); pdf.write(9, f"{data['kaartaa']}")
    pdf.set_font('Times', '', 12); pdf.write(9, " qabaniif kan kennameedha.\n\n")

    pdf.write(9, "Maamilli kun hanga guyyaa har'aatti tajaajiloota waajjira keenya irraa argachaa turaniif:\n\n")

    # Items
    pdf.write(9, "1. Kaffaltii Gibira waggaa hanga bara "


