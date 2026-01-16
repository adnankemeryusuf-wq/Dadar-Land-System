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
    
    # Faayila dubbisuu
    df = pd.read_csv(DATA_FILE, sep="|", names=COL_NAMES, header=None, encoding='utf-8')
    
    # 1. Kaffaltii gara lakkoofsaatti jijjiiri (NaN gara 0.0 tti)
    df['Kafaltii_Taj'] = pd.to_numeric(df['Kafaltii_Taj'], errors='coerce').fillna(0.0)
    
    # 2. Guyyaa sirreessi
    df['Date_Obj'] = pd.to_datetime(df['Guyyaa'], format='%d/%m/%Y', errors='coerce')
    
    # 3. Waggaa, Ji'a fi Kurmaana uumi (Dashboard-f barbaachisaa dha)
    df['Waggaa'] = df['Date_Obj'].dt.year
    df['Ji\'a'] = df['Date_Obj'].dt.month.map(MONTH_MAP)
    
    # Kurmaana Itiyoophiyaatti hunda'ee (9-12=Q1, 1-3=Q2, 4-6=Q3, 7-8=Q4)
    df['Kurmaana'] = df['Date_Obj'].dt.month.apply(
        lambda x: 1 if x in [9,10,11,12] else (2 if x in [1,2,3] else (3 if x in [4,5,6] else 4))
    )
    
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
        st.title("📊 Dashboard Waliigalaa")
        if not df.empty:
            c1, c2, c3 = st.columns(3)
            with c1: st.markdown(f"<div class='card'><h4>💰 Galii</h4><h2>{df['Kafaltii_Taj'].sum():,.2f}</h2><p>ETB</p></div>", unsafe_allow_html=True)
            with c2: st.markdown(f"<div class='card'><h4>👥 Maamiltoota</h4><h2>{len(df)}</h2><p>Waliigala</p></div>", unsafe_allow_html=True)
            with c3: st.markdown(f"<div class='card'><h4>👷 Ogeeyyii</h4><h2>{df['Maqaa_Ogeessa'].nunique()}</h2><p>Aktiiwii</p></div>", unsafe_allow_html=True)
        else: st.info("Data'n galmeeffame hin jiru.")

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


Message Copilot or @ mention a tab
                            df.at[idx, 'Kafaltii_Taj'] = n_f
                            save_data(df); st.success("✅ Sirreeffameera!"); st.rerun()
                        if ca2.button("🗑 Haqi", key=f"d_{idx}"):
                            df = df.drop(idx); save_data(df); st.rerun()
            else:
                st.error("Maqaan kun galmee keessa hin jiru!")

    elif menu == "Ba'i":
        st.session_state.logged_in = False
        st.rerun()

# --- SEARCH & EDIT ---
elif menu == "🔍 Barbaadi/Edit":
    col_l, col_r = st.columns([1, 4])
    with col_l:
        if os.path.exists(LOGO_PATH):
            st.image(LOGO_PATH, width=80)
    with col_r:
        st.header("🔍 Barbaadi fi Sirreessi")
        st.info("Maqaa maamilaa barreessuun galmee isaa sirreessi ykn haqi.")
    
    # Kutaalee Copilot ykn Maqaa namootaa as jiran hunda haqi
