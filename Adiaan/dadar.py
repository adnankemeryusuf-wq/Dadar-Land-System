import streamlit as st
import pandas as pd
import os
import io
import requests
from datetime import datetime
from fpdf import FPDF
import plotly.express as px
from ethiopian_date import EthiopianDateConverter

# ================= 1. CONFIGURATION & STYLE =================
# 1. Jalqaba variable kana qopheessi
LOGO_PATH = "Adiaan/logo.png"

# 2. Page config irratti variable sana fayyadami (Waraabbii malee)
st.set_page_config(
    page_title="Dadar Land Customer Registration System", 
    page_icon=LOGO_PATH if os.path.exists(LOGO_PATH) else "🏢", 
    layout="wide"
)
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

# ================= 2. CORE FUNCTIONS =================
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

def create_advanced_pdf(name, count, rank, logo_left=None, logo_right=None):
    # Orientation 'L' (Landscape), A4
    pdf = FPDF(orientation='L', unit='mm', format='A4')
    pdf.add_page()
    
    # --- Halluuwwan Sadarkaatti Hunda'an ---
    if rank == 1:
        rank_color = (255, 215, 0)   # Gold
        rank_text = "1FFAA"
    elif rank == 2:
        rank_color = (192, 192, 192) # Silver
        rank_text = "2FFAA"
    else:
        rank_color = (205, 127, 50)  # Bronze
        rank_text = "3FFAA"

    deep_green = (0, 80, 0)
    bg_color = (255, 255, 255) # White background for clarity


# --- 1. Background fi Border (Dynamic Border Color) ---
    pdf.set_fill_color(*bg_color)
    pdf.rect(10, 10, 277, 190, 'F')
    
    # Border inni gubbaa (Magariisa)
    pdf.set_draw_color(*deep_green)
    pdf.set_line_width(3.0)
    pdf.rect(10, 10, 277, 190)
    
    # Border inni keessaa (Halluu Sadarkaa: Gold/Silver/Bronze)
    pdf.set_draw_color(*rank_color)
    pdf.set_line_width(1.5)
    pdf.rect(13, 13, 271, 184)

    # --- 2. Logo Handling (Safe Temporary Files) ---
    def save_temp_logo(logo_file, prefix):
        if logo_file:
            ext = logo_file.name.split('.')[-1].lower()
            temp_path = f"temp_{prefix}.{ext}"
            with open(temp_path, "wb") as f:
                f.write(logo_file.getbuffer())
            return temp_path
        return None

    path_l = save_temp_logo(logo_left, "left")
    path_r = save_temp_logo(logo_right, "right")

    if path_l: pdf.image(path_l, x=20, y=18, w=25)
    if path_r: pdf.image(path_r, x=250, y=18, w=25)

    # --- 3. Mata Duree ---
    pdf.set_y(45)
    pdf.set_text_color(*rank_color)
    pdf.set_font('Arial', 'B', 35) 
    pdf.cell(0, 15, "SARTIIFIKETA BEEKAMTII", ln=True, align='C')
    
    pdf.set_y(62)
    pdf.set_text_color(*deep_green)
    pdf.set_font('Arial', 'B', 22)
    pdf.cell(0, 12, "Waajjira Lafaa Bulchiinsa Magaalaa Dadar", ln=True, align='C')

    # --- 4. Sadarkaa fi Maqaa ---
    pdf.set_y(90)
    pdf.set_text_color(50, 50, 50)
    pdf.set_font('Arial', 'I', 18)
    pdf.cell(0, 10, f"Badhaasa Sadarkaa {rank_text} Waggaa 2026", ln=True, align='C')

    pdf.ln(5)
    pdf.set_text_color(*deep_green)
    pdf.set_font('Arial', 'B', 30) 
    pdf.cell(0, 25, f"Obbo/Adde: {name.upper()}", ln=True, align='C')

    # --- 5. Gumaacha Hojii ---
    pdf.set_y(140)
    pdf.set_text_color(60, 60, 60)
    pdf.set_font('Arial', '', 14)
    msg = f"Tajaajilamtoota {count} saffisaa fi qulqullinaan tajaajiluun gumaacha guddaa waan gumaachaniif badhaasa kanaan galateeffamaniiru."
    pdf.multi_cell(0, 10, msg, align='C')

    # --- 6. Mallattoo ---
    pdf.set_y(175)
    pdf.set_draw_color(*deep_green)
    pdf.line(40, 175, 100, 175)
    pdf.set_xy(40, 177); pdf.set_font('Arial', 'B', 12)
    pdf.cell(60, 8, "Mallattoo Itti Gaafatamaa", align='C')

    pdf.line(190, 175, 250, 175)
    pdf.set_xy(190, 177); pdf.cell(60, 8, f"Guyyaa: {datetime.now().strftime('%d/%m/%Y')}", align='C')

    return pdf.output(dest='S').encode('latin-1')
# ================= 3. MAIN APP =================
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    _, col_mid, _ = st.columns([1, 1.2, 1])
    with col_mid:
        if os.path.exists(LOGO_PATH):
            st.image(LOGO_PATH, width=100)
        st.markdown("<h2 style='text-align:center; color: #1b5e20;'>Dadar Land Administration Customer Registration System</h2>", unsafe_allow_html=True)
        with st.form("login_form"):
            st.markdown("####  Login")
            u = st.text_input("Username", placeholder="admin")
            p = st.text_input("Password", type="password", placeholder="••••••••")
            if st.form_submit_button("Seeni"):
                if u == "DAD" and p == "2026":
                    st.session_state.logged_in = True
                    st.rerun()
                else:
                    st.error("Maqaan ykn Koodiin dogoggora!")
else:
    df = load_data()
    with st.sidebar:
        if os.path.exists(LOGO_PATH): 
            st.image(LOGO_PATH, width=100)
        st.success("Deder City Land Office")
        menu = st.radio("FILANNOO", ["📊 Dashboard", "📝 Galmee Haaraa", "📈 Gabaasa Bal'aa", "🏆 Badhaasa Ogeeyyii", "🔍 Barbaadi/Edit"])
        if st.button("Log Out"):
            st.session_state.logged_in = False
            st.rerun()

   # --- DASHBOARD ---
    if menu == "📊 Dashboard":
        st.markdown("<h2 style='color: #1b5e20;'>📊 Dashboard Waliigalaa</h2>", unsafe_allow_html=True)
        if not df.empty:
            c1, c2, c3 = st.columns(3)
            with c1:
                rev = float(df['Kafaltii_Taj'].sum())
                st.markdown(f"<div class='card'><p>💰 Galii Waliigalaa</p><p class='metric-value'>{rev:,.2f} ETB</p></div>", unsafe_allow_html=True)
            with c2:
                st.markdown(f"<div class='card'><p>👥 Maamiltoota</p><p class='metric-value'>{len(df)}</p></div>", unsafe_allow_html=True)
            with c3:
                top_og = df['Maqaa_Ogeessa'].mode()[0] if not df['Maqaa_Ogeessa'].empty else "-"
                st.markdown(f"<div class='card'><p>🏆 Ogeessa Filatamaa</p><p class='metric-value'>{top_og}</p></div>", unsafe_allow_html=True)
            
            st.markdown("---")
            st.subheader("📈 Trendii Galii Ji'aan")
            trend_data = df.groupby('Ji\'a')['Kafaltii_Taj'].sum().reindex(MONTH_ORDER).fillna(0)
            st.area_chart(trend_data)
        else:
            st.info("Data'n galmeeffame hin jiru.")
   # --- GALMEE HAARAA ---
elif menu == "📝 Galmee Haaraa":
    st.header("📝 Galmee Tajaajilaa Haaraa")
    GATII_DICT = {
        "🏷️ Gibira & Kaffaltii": ["Gibira Baaxii Gooroo", "Gibira Lafa Qonnaa", "Kaffaltii Liizii Waggaa", "Kaffaltii Liizii Duraa", "TOT (Turnover Tax)"],
        "📜 Kaartaa & Qabiyyee": ["Kaartaa Haaraa", "Kaartaa Bakka Bu'aa", "Kaartaa Kadastaaraa", "Jijjiirraa Maqaa (Gift/Sale)", "Sirreeffama Daangaa", "Ganda Irraa gara Magaalaatti"],
        "🏗️ Pilaanii & Ijaarsa": ["Pilaanii Magaalaa", "Itti Fayyadama Lafaa (Land Use)", "Humna Mahandisummaa"],
        "⚖️ Dhimma Seeraa": ["Ugura Mana Murtii", "Ugura Kaasuu", "Waliigaltee Liqii Baankii", "Waliigaltee Hiikuu", "Dhimma Dhala (Inheritance)"],
        "📂 Tajaajila Biroo": ["Waraqaa Ragaa (Clearance)", "Deebii Iyyannoo"]
    }
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




import streamlit as st
import pandas as pd
import os
import io
import requests
from datetime import datetime
from fpdf import FPDF
import plotly.express as px
from ethiopian_date import EthiopianDateConverter

# ================= 1. CONFIGURATION & STYLE =================
# 1. Jalqaba variable kana qopheessi
LOGO_PATH = "Adiaan/logo.png"
NAGAHEE_DIR = "nagahee_scan"
# Folder nagahee itti kuusnu yoo hin jirre uumuuf
if not os.path.exists(NAGAHEE_DIR):
    os.makedirs(NAGAHEE_DIR)
# 2. Page config irratti variable sana fayyadami (Waraabbii malee)
st.set_page_config(
    page_title="Dadar Land Customer Registration System", 
    page_icon=LOGO_PATH if os.path.exists(LOGO_PATH) else "🏢", 
    layout="wide"
)
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

# ================= 2. CORE FUNCTIONS =================
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

def create_advanced_pdf(name, count, rank, logo_left=None, logo_right=None):
    # Orientation 'L' (Landscape), A4
    pdf = FPDF(orientation='L', unit='mm', format='A4')
    pdf.add_page()
    
    # --- Halluuwwan Sadarkaatti Hunda'an ---
    if rank == 1:
        rank_color = (255, 215, 0)   # Gold
        rank_text = "1FFAA"
    elif rank == 2:
        rank_color = (192, 192, 192) # Silver
        rank_text = "2FFAA"
    else:
        rank_color = (205, 127, 50)  # Bronze
        rank_text = "3FFAA"

    deep_green = (0, 80, 0)
    bg_color = (255, 255, 255) # White background for clarity


# --- 1. Background fi Border (Dynamic Border Color) ---
    pdf.set_fill_color(*bg_color)
    pdf.rect(10, 10, 277, 190, 'F')
    
    # Border inni gubbaa (Magariisa)
    pdf.set_draw_color(*deep_green)
    pdf.set_line_width(3.0)
    pdf.rect(10, 10, 277, 190)
    
    # Border inni keessaa (Halluu Sadarkaa: Gold/Silver/Bronze)
    pdf.set_draw_color(*rank_color)
    pdf.set_line_width(1.5)
    pdf.rect(13, 13, 271, 184)

    # --- 2. Logo Handling (Safe Temporary Files) ---
    def save_temp_logo(logo_file, prefix):
        if logo_file:
            ext = logo_file.name.split('.')[-1].lower()
            temp_path = f"temp_{prefix}.{ext}"
            with open(temp_path, "wb") as f:
                f.write(logo_file.getbuffer())
            return temp_path
        return None

    path_l = save_temp_logo(logo_left, "left")
    path_r = save_temp_logo(logo_right, "right")

    if path_l: pdf.image(path_l, x=20, y=18, w=25)
    if path_r: pdf.image(path_r, x=250, y=18, w=25)

    # --- 3. Mata Duree ---
    pdf.set_y(45)
    pdf.set_text_color(*rank_color)
    pdf.set_font('Arial', 'B', 35) 
    pdf.cell(0, 15, "SARTIIFIKETA BEEKAMTII", ln=True, align='C')
    
    pdf.set_y(62)
    pdf.set_text_color(*deep_green)
    pdf.set_font('Arial', 'B', 22)
    pdf.cell(0, 12, "Waajjira Lafaa Bulchiinsa Magaalaa Dadar", ln=True, align='C')

    # --- 4. Sadarkaa fi Maqaa ---
    pdf.set_y(90)
    pdf.set_text_color(50, 50, 50)
    pdf.set_font('Arial', 'I', 18)
    pdf.cell(0, 10, f"Badhaasa Sadarkaa {rank_text} Waggaa 2026", ln=True, align='C')

    pdf.ln(5)
    pdf.set_text_color(*deep_green)
    pdf.set_font('Arial', 'B', 30) 
    pdf.cell(0, 25, f"Obbo/Adde: {name.upper()}", ln=True, align='C')

    # --- 5. Gumaacha Hojii ---
    pdf.set_y(140)
    pdf.set_text_color(60, 60, 60)
    pdf.set_font('Arial', '', 14)
    msg = f"Tajaajilamtoota {count} saffisaa fi qulqullinaan tajaajiluun gumaacha guddaa waan gumaachaniif badhaasa kanaan galateeffamaniiru."
    pdf.multi_cell(0, 10, msg, align='C')

    # --- 6. Mallattoo ---
    pdf.set_y(175)
    pdf.set_draw_color(*deep_green)
    pdf.line(40, 175, 100, 175)
    pdf.set_xy(40, 177); pdf.set_font('Arial', 'B', 12)
    pdf.cell(60, 8, "Mallattoo Itti Gaafatamaa", align='C')

    pdf.line(190, 175, 250, 175)
    pdf.set_xy(190, 177); pdf.cell(60, 8, f"Guyyaa: {datetime.now().strftime('%d/%m/%Y')}", align='C')

    return pdf.output(dest='S').encode('latin-1')
# ================= 3. MAIN APP =================
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    _, col_mid, _ = st.columns([1, 1.2, 1])
    with col_mid:
        if os.path.exists(LOGO_PATH):
            st.image(LOGO_PATH, width=100)
        st.markdown("<h2 style='text-align:center; color: #1b5e20;'>Dadar Land Administration Customer Registration System</h2>", unsafe_allow_html=True)
        with st.form("login_form"):
            st.markdown("####  Login")
            u = st.text_input("Username", placeholder="admin")
            p = st.text_input("Password", type="password", placeholder="••••••••")
            if st.form_submit_button("Seeni"):
                if u == "DAD" and p == "2026":
                    st.session_state.logged_in = True
                    st.rerun()
                else:
                    st.error("Maqaan ykn Koodiin dogoggora!")
else:
    df = load_data()
    with st.sidebar:
        if os.path.exists(LOGO_PATH): 
            st.image(LOGO_PATH, width=100)
        st.success("Deder City Land Office")
        menu = st.radio("FILANNOO", ["📊 Dashboard", "📝 Galmee Haaraa", "📈 Gabaasa Bal'aa", "🏆 Badhaasa Ogeeyyii", "🔍 Barbaadi/Edit"])
        if st.button("Log Out"):
            st.session_state.logged_in = False
            st.rerun()

   # --- DASHBOARD ---
    if menu == "📊 Dashboard":
        st.markdown("<h2 style='color: #1b5e20;'>📊 Dashboard Waliigalaa</h2>", unsafe_allow_html=True)
        if not df.empty:
            c1, c2, c3 = st.columns(3)
            with c1:
                rev = float(df['Kafaltii_Taj'].sum())
                st.markdown(f"<div class='card'><p>💰 Galii Waliigalaa</p><p class='metric-value'>{rev:,.2f} ETB</p></div>", unsafe_allow_html=True)
            with c2:
                st.markdown(f"<div class='card'><p>👥 Maamiltoota</p><p class='metric-value'>{len(df)}</p></div>", unsafe_allow_html=True)
            with c3:
                top_og = df['Maqaa_Ogeessa'].mode()[0] if not df['Maqaa_Ogeessa'].empty else "-"
                st.markdown(f"<div class='card'><p>🏆 Ogeessa Filatamaa</p><p class='metric-value'>{top_og}</p></div>", unsafe_allow_html=True)
            
            st.markdown("---")
            st.subheader("📈 Trendii Galii Ji'aan")
            trend_data = df.groupby('Ji\'a')['Kafaltii_Taj'].sum().reindex(MONTH_ORDER).fillna(0)
            st.area_chart(trend_data)
        else:
            st.info("Data'n galmeeffame hin jiru.")
    # --- REGISTRATION ---
    elif menu == "📝 Galmee Haaraa":
        st.header("📝 Galmee Tajaajilaa")
        GATII_DICT = {
            "Gibira": ["Gibira Baaxii Gooroo", "Gibira Lafa Qonnaa"],
            "Liizii": ["Liizii Waggaa", "Jijjiirraa Maqaa", "Kafaltii Liizii Duraa", "TOT"],
            "Ittii Fayyaddam": ["Hayyama Itti Fayyadama Lafaa", "Humna Mahandiisaa"],
            "Kaartaa": ["Kaartaa Lafa", "Kaartaa Kadastaara", "Kaartaa Lafa Qonnaa"],
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

# --- UPLOAD NAGAHEE ---
            nagahee_file = st.file_uploader("Nagahee Scan (JPG/PNG)", type=['jpg','png','jpeg'])
            
            if st.form_submit_button("💾 Galmeessi"):
                if maqaa and ogeessa and details:
                    if nagahee_file:
                        f_name = f"{maqaa.replace(' ','_')}_{datetime.now().strftime('%H%M%S')}.jpg"
                        with open(os.path.join(NAGAHEE_DIR, f_name), "wb") as f:
                            f.write(nagahee_file.getbuffer())
                    
                    new_data = [datetime.now().strftime('%d/%m/%Y'), maqaa, ara, qax, ", ".join(details), ogeessa, sum(d_fees.values())]
                    df = pd.concat([df, pd.DataFrame([new_data], columns=COL_NAMES)], ignore_index=True)
                    save_data(df)
                    st.success("✅ Galmeeffameera!")
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





import streamlit as st
import pandas as pd
import os
import io
import requests
from datetime import datetime
from fpdf import FPDF

# ================= 1. CONFIGURATION & STYLE =================
LOGO_PATH = "Adiaan/logo.png"
NAGAHEE_DIR = "nagahee_scan"
DATA_FILE = "dadar_final_report.txt"
BOT_TOKEN = "8357193631:AAHCuSnXzjZTQaglkmcS0gq-EvqnkIQLDBI"
CHAT_ID_MANAGER = "7329587700"

if not os.path.exists(NAGAHEE_DIR):
    os.makedirs(NAGAHEE_DIR)

st.set_page_config(
    page_title="Dadar Land Administration", 
    page_icon=LOGO_PATH if os.path.exists(LOGO_PATH) else "🏢", 
    layout="wide"
)

# Custom CSS for UI
st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #f1f8e9 0%, #ffffff 100%); }
    [data-testid="stSidebar"] { background-color: #1b5e20 !important; }
    [data-testid="stSidebar"] * { color: #ffffff !important; }
    div.stForm { background: white; border-radius: 15px; padding: 25px; border: 2px solid #2e7d32; box-shadow: 0px 4px 15px rgba(0,0,0,0.1); }
    .card { background: white; padding: 20px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); text-align: center; border-top: 5px solid #2e7d32; margin-bottom: 10px; }
    .metric-value { font-size: 24px; font-weight: bold; color: #2e7d32; }
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

# ================= 3. MAIN APP LOGIC =================
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    # --- LOGIN PAGE ---
    _, col_mid, _ = st.columns([1, 1.2, 1])
    with col_mid:
        if os.path.exists(LOGO_PATH): st.image(LOGO_PATH, width=100)
        st.markdown("<h2 style='text-align:center;'>Dadar Land Admin</h2>", unsafe_allow_html=True)
        with st.form("login_form"):
            u = st.text_input("Username")
            p = st.text_input("Password", type="password")
            if st.form_submit_button("Seeni"):
                if u == "DAD" and p == "2026":
                    st.session_state.logged_in = True
                    st.rerun()
                else: st.error("Maqaan ykn Koodiin dogoggora!")
else:
    # --- LOGGED IN AREA ---
    df = load_data()
    
    with st.sidebar:
        if os.path.exists(LOGO_PATH): st.image(LOGO_PATH, width=100)
        st.success("Deder City Land Office")
        menu = st.radio("FILANNOO", ["📊 Dashboard", "📝 Galmee Haaraa", "📈 Gabaasa Bal'aa", "🏆 Badhaasa Ogeeyyii", "🔍 Barbaadi/Edit"])
        if st.button("Log Out"):
            st.session_state.logged_in = False
            st.rerun()

    # 1. DASHBOARD
    if menu == "📊 Dashboard":
        st.header("📊 Dashboard")
        if not df.empty:
            c1, c2, c3 = st.columns(3)
            with c1: st.markdown(f"<div class='card'><p>💰 Galii</p><p class='metric-value'>{df['Kafaltii_Taj'].sum():,.2f}</p></div>", unsafe_allow_html=True)
            with c2: st.markdown(f"<div class='card'><p>👥 Maamiltoota</p><p class='metric-value'>{len(df)}</p></div>", unsafe_allow_html=True)
            with c3: st.markdown(f"<div class='card'><p>👷 Ogeeyyii</p><p class='metric-value'>{df['Maqaa_Ogeessa'].nunique()}</p></div>", unsafe_allow_html=True)
            st.area_chart(df.groupby('Ji\'a')['Kafaltii_Taj'].sum().reindex(MONTH_ORDER).fillna(0))
        else: st.info("Data'n hin jiru.")

    # 2. REGISTRATION
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
    # 3. GABAASA
    elif menu == "📈 Gabaasa Bal'aa":
        st.header("📈 Gabaasa")
        st.dataframe(df[COL_NAMES])

    # 4. BADHAASA
    elif menu == "🏆 Badhaasa Ogeeyyii":
        st.header("🏆 Ogeeyyii Filatamoa")
        if not df.empty:
            top_3 = df['Maqaa_Ogeessa'].value_counts().head(3)
            for i, (name, count) in enumerate(top_3.items()):
                st.write(f"{i+1}. {name} - {count} Hojii")
    
    # 5. SEARCH/EDIT
    elif menu == "🔍 Barbaadi/Edit":
        q = st.text_input("Maqaa Barbaadi")
        if q:
            res = df[df['Maqaa_Abbaa_Dhimmaa'].str.contains(q, case=False, na=False)]
            st.dataframe(res)

import streamlit as st
import pandas as pd
import os
import io
import requests
from datetime import datetime
from fpdf import FPDF
import plotly.express as px

# ================= 1. CONFIGURATION & STYLE =================
LOGO_PATH = "Adiaan/logo.png"
NAGAHEE_DIR = "nagahee_scan"
DATA_FILE = "dadar_final_report.txt"
BOT_TOKEN = "8357193631:AAHCuSnXzjZTQaglkmcS0gq-EvqnkIQLDBI"
CHAT_ID_MANAGER = "7329587700"

# Folderoota barbaachisoo uumuu
if not os.path.exists(NAGAHEE_DIR):
    os.makedirs(NAGAHEE_DIR)

st.set_page_config(
    page_title="Dadar Land Administration System", 
    page_icon="🏢", 
    layout="wide"
)

# Style Bareedaa (CSS)
st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #f1f8e9 0%, #ffffff 100%); }
    [data-testid="stSidebar"] { background-color: #1b5e20 !important; }
    [data-testid="stSidebar"] * { color: #ffffff !important; }
    div.stForm { background: white; border-radius: 15px; padding: 25px; border: 2px solid #2e7d32; box-shadow: 0px 4px 15px rgba(0,0,0,0.1); }
    .card { background: white; padding: 20px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); text-align: center; border-top: 5px solid #2e7d32; margin-bottom: 10px; }
    .metric-value { font-size: 24px; font-weight: bold; color: #2e7d32; }
    .stButton>button { background: linear-gradient(90deg, #4caf50, #2e7d32); color: white; border-radius: 8px; font-weight: bold; }
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
        menu = st.radio("FILANNOO", ["📊 Dashboard", "📝 Galmee Haaraa", "📈 Gabaasa Bal'aa", "🏆 Badhaasa Ogeeyyii", "🔍 Barbaadi/Edit"])
        if st.button("Log Out"):
            st.session_state.logged_in = False
            st.rerun()
 # 1. DASHBOARD
    if menu == "📊 Dashboard":
        st.header("📊 Dashboard")
        if not df.empty:
            c1, c2, c3 = st.columns(3)
            with c1: st.markdown(f"<div class='card'><p>💰 Galii</p><p class='metric-value'>{df['Kafaltii_Taj'].sum():,.2f}</p></div>", unsafe_allow_html=True)
            with c2: st.markdown(f"<div class='card'><p>👥 Maamiltoota</p><p class='metric-value'>{len(df)}</p></div>", unsafe_allow_html=True)
            with c3: st.markdown(f"<div class='card'><p>👷 Ogeeyyii</p><p class='metric-value'>{df['Maqaa_Ogeessa'].nunique()}</p></div>", unsafe_allow_html=True)
            st.area_chart(df.groupby('Ji\'a')['Kafaltii_Taj'].sum().reindex(MONTH_ORDER).fillna(0))
        else: st.info("Data'n hin jiru.")

    # 2. REGISTRATION
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
                st.success("Gabaasa telegramitti ergameera!") # Logic erguu armaan olitti jira

    # --- 🏆 BADHAASA OGEEYYII ---
    elif menu == "🏆 Badhaasa Ogeeyyii":
        st.header("🏆 Sadarkaa fi Badhaasa Ogeeyyii")
        if not df.empty:
            top_3 = df['Maqaa_Ogeessa'].value_counts().head(3)
            cols = st.columns(3)
            for i, (name, count) in enumerate(top_3.items()):
                with cols[i]:
                    st.markdown(f"<div class='card'><h2>{i+1}ffaa</h2><h3>{name}</h3><p>Hojii: {count}</p></div>", unsafe_allow_html=True)
                    pdf_b = create_certificate(name, count, "", "STAFF", i+1)
                    st.download_button(f"📥 Sartifiikeetii {i+1}", pdf_b, f"Badhaasa_{name}.pdf", key=f"staff_{i}")
        else: st.info("Data'n hojii ogeeyyii hin jiru.")

    # 4. BADHAASA
    elif menu == "🏆 Badhaasa Ogeeyyii":
        st.header("🏆 Ogeeyyii Filatamoa")
        if not df.empty:
            top_3 = df['Maqaa_Ogeessa'].value_counts().head(3)
            for i, (name, count) in enumerate(top_3.items()):
                st.write(f"{i+1}. {name} - {count} Hojii")
    
    # 5. SEARCH/EDIT
    elif menu == "🔍 Barbaadi/Edit":
        q = st.text_input("Maqaa Barbaadi")
        if q:
            res = df[df['Maqaa_Abbaa_Dhimmaa'].str.contains(q, case=False, na=False)]
            st.dataframe(res)






    if menu == "📊 Dashboard":
        st.header("📊 Dashboard Waliigalaa")
        if not df.empty:
            c1, c2, c3 = st.columns(3)
            c1.markdown(f"<div class='card'><p>💰 Galii Waliigalaa</p><p class='metric-value'>{df['Kafaltii_Taj'].sum():,.2f} ETB</p></div>", unsafe_allow_html=True)
            c2.markdown(f"<div class='card'><p>👥 Maamiltoota</p><p class='metric-value'>{len(df)}</p></div>", unsafe_allow_html=True)
            top_og = df['Maqaa_Ogeessa'].mode()[0] if not df.empty else "-"
            c3.markdown(f"<div class='card'><p>🏆 Ogeessa Cimaa</p><p class='metric-value'>{top_og}</p></div>", unsafe_allow_html=True)
            st.area_chart(df.groupby('Ji\'a')['Kafaltii_Taj'].sum().reindex(MONTH_ORDER).fillna(0))

    elif menu == "📝 Galmee Haaraa":
        st.header("📝 Galmee Tajaajilaa")
        GATII_DICT = {"Gibira": ["Gibira Lafa Qonnaa", "Gibira Manaa"], "Liizii": ["Liizii Waggaa", "Jijjiirraa Maqaa", "TOT"]}
        
        with st.form("entry_form"):
            maqaa = st.text_input("Maqaa Abbaa Dhimmaa")
            ara = st.text_input("Araddaa")
            qax = st.text_input("Qaxana")
            ogeessa = st.text_input("Maqaa Ogeessaa")
            gosa = st.multiselect("Gosa Tajaajilaa", sum(GATII_DICT.values(), []))
            kaffaltii = st.number_input("Kaffaltii (ETB)", min_value=0.0)
            
            if st.form_submit_button("💾 Galmeessi"):
                if maqaa and ogeessa:
                    new_row = [datetime.now().strftime('%d/%m/%Y'), maqaa, ara, qax, ", ".join(gosa), ogeessa, kaffaltii]
                    df = pd.concat([df, pd.DataFrame([new_row], columns=COL_NAMES)], ignore_index=True)
                    save_data(df)
                    st.success("Galmeeffameera!")

    elif menu == "📈 Gabaasa Bal'aa":
        st.header("📈 Gabaasa Bal'aa")
        if not df.empty:
            f_type = st.selectbox("Calali:", ["Waliigala", "Waggaa", "Ji'a"])
            filtered = df.copy() # Calala dabalataa asitti galchuun ni danda'ama
            
            # Export Buttons
            st.subheader("📥 Gabaasa Buufadhu")
            ex1, ex2, ex3 = st.columns(3)
            
            # Excel
            buf_ex = io.BytesIO()
            with pd.ExcelWriter(buf_ex, engine='xlsxwriter') as writer:
                filtered[COL_NAMES].to_excel(writer, index=False)
            ex1.download_button("📊 Excel Buusi", buf_ex.getvalue(), "Gabaasa.xlsx")
            
            # PPT
            ppt_file = create_ppt_report(filtered, f_type)
            ex2.download_button("🖥️ PPT Buusi", ppt_file, "Gabaasa.pptx")
            
            st.dataframe(filtered[COL_NAMES], use_container_width=True)

    if st.sidebar.button("Log Out"):
        st.session_state.logged_in = False
        st.rerun()


# Session State qopheessuu
if 'pdf_to_download' not in st.session_state:
    st.session_state.pdf_to_download = None
if 'pdf_name' not in st.session_state:
    st.session_state.pdf_name = ""

# ================= 2. CORE FUNCTIONS =================

def load_data():
    if not os.path.exists(DATA_FILE) or os.stat(DATA_FILE).st_size == 0:
        return pd.DataFrame(columns=COL_NAMES)
    return pd.read_csv(DATA_FILE, sep="|", names=COL_NAMES, header=None, encoding="utf-8")

def save_data(df_to_save):
    df_to_save[COL_NAMES].to_csv(DATA_FILE, sep="|", index=False, header=False, encoding="utf-8")

def get_ethiopian_date_str():
    now = datetime.now()
    converter = EthiopianDateConverter()
    e_date = converter.to_ethiopian(now.year, now.month, now.day)
    return f"{e_date[2]:02d}/{e_date[1]:02d}/{e_date[0]}"

# --- WARAQAA RAGAA (CLEARANCE) PDF ---
def create_clearance_pdf(data):
    pdf = FPDF(orientation='P', unit='mm', format='A4')
    pdf.add_page()
    
    # Border
    pdf.set_line_width(0.8); pdf.rect(10, 10, 190, 277)
    
    # Logos
    if os.path.exists("logo_bitta.jpg"): pdf.image("logo_bitta.jpg", 15, 15, 25)
    if os.path.exists("logo_mirga.jpg"): pdf.image("logo_mirga.jpg", 170, 15, 25)

    # Header
    pdf.set_y(22); pdf.set_font('Arial', 'B', 15)
    pdf.cell(0, 8, "MOOTUMMAA NAANNOO OROMIYAA", ln=True, align='C')
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 8, "WAAJJIRA LAFAA BULCHIINSA MAGAALAA DADAR", ln=True, align='C')
    
    pdf.ln(5); pdf.set_line_width(0.5); pdf.line(20, 48, 190, 48)

    # Date & Ref
    converter = EthiopianDateConverter()
    now_ec = converter.to_ethiopian(datetime.now().year, datetime.now().month, datetime.now().day)
    guyyaa_ec = get_ethiopian_date_str()
    
    pdf.ln(8); pdf.set_font('Arial', '', 12); pdf.set_x(20)
    pdf.cell(90, 5, f"Lakk. Galmee: DAD/WL/{now_ec[0]}/____", align='L')
    pdf.cell(80, 5, f"Guyyaa: {guyyaa_ec}", ln=True, align='R')

    # Subject
    pdf.ln(10); pdf.set_font('Arial', 'BU', 14)
    pdf.cell(0, 10, "WARAQAA RAGAA QULQULLINAA (CLEARANCE)", ln=True, align='C')

    # Body
    pdf.set_y(90); pdf.set_font('Arial', '', 12); pdf.set_x(20)
    text_content = (
        f"Waraqaan ragaa kun Obbo/Adde/Dhaabbata {data['maqaa'].upper()} Araddaa {data['araddaa']} "
        f"Qaxana {data['qaxana']} keessatti tajaajila argachaa turaniif kan kennameedha.\n\n"
        f"Maamilli kun hanga guyyaa har'aatti ({guyyaa_ec}) tatti tajaajiloota waajjira keenya irraa:\n\n"
        f"1. Kaffaltii Gibira waggaa hanga bara {data['bara_gibiraa']} kaffalaniiru.\n"
        f"2. Qabiyyee Lakk. Kaartaa {data['kaartaa']} qabaniif kaffaltii barbaachisu raawwataniiru.\n"
        f"3. Qabiyyeen kun DHORKAA kamirrayyuu bilisa ta'uu isaa mirkaneessina.\n\n"
        f"Kanaafuu, dhimma '{data['dhimma']}' raawwachuuf ragaa kana akka dhiyeeffatan ni mirkaneessina."
    )
    pdf.multi_cell(170, 9, text_content, align='L')

    # Signature
    pdf.set_y(230); pdf.set_font('Arial', 'B', 12); pdf.set_x(120)
    pdf.cell(0, 8, "Itti Gaafatamaa Waajjiraa", ln=True)
    pdf.set_x(120); pdf.cell(0, 8, "Mallattoo: ____________", ln=True)
    
    return pdf.output(dest='S').encode('latin-1')

# ================= 3. UI LAYOUT =================
st.set_page_config(page_title="Dadar Land Management", layout="wide")
df = load_data()

menu = st.sidebar.radio("FILANNOO", ["📊 Dashboard", "📝 Galmee", "CLEARANCE", "🏆 Badhaasa", "📈 Gabaasa"])

# --- DASHBOARD ---
if menu == "📊 Dashboard":
    st.title("📊 Dashboard")
    
    c1, c2, c3 = st.columns(3)
    c1.metric("Waliigala Galii", f"{df['Kafaltii_Taj'].sum():,.2f} ETB")
    c2.metric("Maamiltoota", len(df))
    c3.metric("Ogeeyyii", df['Maqaa_Ogeessa'].nunique())

# --- GALMEE & CLEARANCE ---
elif menu == "📝 Galmee & Clearance":
    st.header("📝 Galmee fi Qophii Clearance")
    
    # Logo Configuration in Sidebar
    st.sidebar.subheader("⚙️ Qindaa'ina Mallattoo")
    up_bitta = st.sidebar.file_uploader("Logo Bittaa", type=['png', 'jpg'])
    if up_bitta:
        img_b = Image.open(up_bitta).convert("RGB").save("logo_bitta.jpg")
    
    up_mirga = st.sidebar.file_uploader("Logo Mirgaa", type=['png', 'jpg'])
    if up_mirga:
        img_m = Image.open(up_mirga).convert("RGB").save("logo_mirga.jpg")

    if st.session_state.pdf_to_download:
        st.success("📄 Clearance qophaa'eera!")
        st.download_button("📥 PDF BUUFADHU", st.session_state.pdf_to_download, st.session_state.pdf_name)
        if st.button("Galmee Haaraa"): 
            st.session_state.pdf_to_download = None
            st.rerun()

    with st.form("clearance_form"):
        c1, c2 = st.columns(2)
        m_maqaa = c1.text_input("Maqaa Maamilaa *")
        m_ogeessa = c2.text_input("Maqaa Ogeessa Galmeessu *")
        m_araddaa = c1.text_input("Araddaa *")
        m_qaxana = c2.text_input("Qaxana")
        m_kaartaa = c1.text_input("Lakk. Kaartaa")
        m_bara = c2.text_input("Bara Gibiraa (Fkn: 2017)")
        m_dhimma = st.selectbox("Dhimma Maaliif?", ["Gurgurtaa", "Liqii Bankii", "Kennaa", "Waliigaltee"])
        m_kaffaltii = st.number_input("Kaffaltii Tajaajilaa (ETB)", min_value=0.0)
        m_dhorkaa = st.checkbox("Dhorkaa irraa bilisa ta'uu nan mirkaneessa")

        if st.form_submit_button("💾 GALMEESSI FI PDF UUMI"):
            if m_maqaa and m_ogeessa and m_dhorkaa:
                # Save to Data
                new_row = [get_ethiopian_date_str(), m_maqaa, m_araddaa, m_qaxana, "Clearance", m_ogeessa, m_kaffaltii]
                df = pd.concat([df, pd.DataFrame([new_row], columns=COL_NAMES)], ignore_index=True)
                save_data(df)
                
                # Generate PDF
                data_map = {'maqaa': m_maqaa, 'araddaa': m_araddaa, 'qaxana': m_qaxana, 'kaartaa': m_kaartaa, 'bara_gibiraa': m_bara, 'dhimma': m_dhimma}
                st.session_state.pdf_to_download = create_clearance_pdf(data_map)
                st.session_state.pdf_name = f"Clearance_{m_maqaa.replace(' ', '_')}.pdf"
                st.rerun()
            else: st.error("Maaloo odeeffannoo guutuu galchi!")

# --- GABAASA ---
elif menu == "📈 Gabaasa":
    st.header("📈 Gabaasa Galmee Waliigalaa")
    st.dataframe(df, use_container_width=True)
    
    if st.button("🚀 Excel Gara Telegram-itti Ergi"):
        # (Asitti logic Telegram kee itti fufi)
        st.info("Gabaasni gara maanjaraatti ergamaa jira...")

# --- BADHAASA ---
elif menu == "🏆 Badhaasa":
    st.header("🏆 Ogeeyyii Baay'ee Hojjetan")
    if not df.empty:
        st.bar_chart(df['Maqaa_Ogeessa'].value_counts())



