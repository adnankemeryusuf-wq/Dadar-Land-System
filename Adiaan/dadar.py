import streamlit as st
import pandas as pd
import os
import io
import base64
from datetime import datetime
from reportlab.lib.pagesizes import A4, landscape
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.lib.colors import gold, silver, brown, green, black, hexColor

# ================= 1. CONFIGURATION & STYLE =================
LOGO_PATH = "Adiaan/logo.png"
DATA_FILE = "dadar_final_report.txt"
NAGAHEE_DIR = "Adiaan/nagahee"

# Folder-oota barbaachisoo uumuu
if not os.path.exists(NAGAHEE_DIR):
    os.makedirs(NAGAHEE_DIR, exist_ok=True)

st.set_page_config(
    page_title="Dadar Land Customer Registration", 
    page_icon="🏢", 
    layout="wide"
)

# ================= 2. CORE FUNCTIONS =================
COL_NAMES = ['Guyyaa', 'Maqaa_Abbaa_Dhimmaa', 'Araddaa', 'Qaxana', 'Gosa_Tajajjilaa', 'Maqaa_Ogeessa', 'Kafaltii_Taj']
MONTH_MAP = {9: "Fulbaana", 10: "Onkololeessa", 11: "Sadaasa", 12: "Muddee", 1: "Amajjii", 2: "Guraandhala", 3: "Bitootessa", 4: "Eebila", 5: "Caamsaa", 6: "Waxabajjii", 7: "Adooleessa", 8: "Hagayya"}
MONTH_ORDER = ["Fulbaana", "Onkololeessa", "Sadaasa", "Muddee", "Amajjii", "Guraandhala", "Bitootessa", "Eebila", "Caamsaa", "Waxabajjii", "Adooleessa", "Hagayya"]

def save_data(df_to_save):
    try:
        df_to_save[COL_NAMES].to_csv(DATA_FILE, sep="|", index=False, header=False, encoding="utf-8")
        return True
    except Exception as e:
        st.error(f"Error saving data: {e}")
        return False

def load_data():
    if not os.path.exists(DATA_FILE) or os.stat(DATA_FILE).st_size == 0:
        return pd.DataFrame(columns=COL_NAMES)
    try:
        df = pd.read_csv(DATA_FILE, sep="|", names=COL_NAMES, header=None, encoding='utf-8')
        df['Date_Obj'] = pd.to_datetime(df['Guyyaa'], format='%d/%m/%Y', errors='coerce')
        df['Waggaa'] = df['Date_Obj'].dt.year
        df['Ji\'a'] = df['Date_Obj'].dt.month.map(MONTH_MAP)
        return df
    except:
        return pd.DataFrame(columns=COL_NAMES)

def get_base64_img(path):
    if os.path.exists(path):
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return ""

# ================= 3. PDF GENERATOR (REPORTLAB) =================
def create_advanced_pdf(name, count, rank, logo_l=None, logo_r=None):
    packet = io.BytesIO()
    c = canvas.Canvas(packet, pagesize=landscape(A4))
    width, height = landscape(A4)

    rank_colors = {1: gold, 2: silver, 3: hexColor("#CD7F32")}
    theme_color = rank_colors.get(rank, green)

    # Borders
    c.setStrokeColor(theme_color)
    c.setLineWidth(5); c.rect(12*mm, 12*mm, width-(24*mm), height-(24*mm))
    c.setLineWidth(1); c.rect(14*mm, 14*mm, width-(28*mm), height-(28*mm))

    # Logo Drawing Logic
    def draw_logo(img_source, x, y):
        try:
            if img_source is not None:
                img_data = io.BytesIO(img_source.getvalue())
                c.drawImage(img_data, x, y, width=35*mm, height=35*mm, preserveAspectRatio=True, mask='auto')
            elif os.path.exists(LOGO_PATH):
                c.drawImage(LOGO_PATH, x, y, width=35*mm, height=35*mm, preserveAspectRatio=True, mask='auto')
        except: pass

    draw_logo(logo_l, 20*mm, height-50*mm)
    draw_logo(logo_r, width-55*mm, height-50*mm)

    c.setFont("Helvetica-Bold", 45); c.setFillColor(theme_color)
    c.drawCentredString(width/2, height-75*mm, "SARTIIFIKEETA BEEKAMTII")

    c.setFont("Helvetica-Oblique", 22); c.setFillColor(black)
    c.drawCentredString(width/2, height-95*mm, f"Badhaasa Milkaa'ina Sadarkaa {rank}ffaa")

    c.setFont("Helvetica-Bold", 30)
    c.drawCentredString(width/2, height-120*mm, str(name).upper())

    c.setFont("Helvetica", 18)
    line1 = f"Ogeessa kanaan waggaa 2026 keessa tajaajilamtoota {count} tajaajiluun"
    line2 = f"sadarkaa {rank}ffaa waan qabataniif beekamtiin kun kennameef."
    c.drawCentredString(width/2, height-140*mm, line1)
    c.drawCentredString(width/2, height-150*mm, line2)

    c.setFont("Helvetica-Bold", 14)
    c.drawString(30*mm, 40*mm, f"Guyyaa: {datetime.now().strftime('%d/%m/%Y')}")
    c.line(width-90*mm, 40*mm, width-30*mm, 40*mm)
    c.drawCentredString(width-60*mm, 35*mm, "Itti Gaafatamaa Waajjiraa")

    c.showPage(); c.save()
    packet.seek(0)
    return packet.getvalue()

# ================= 4. UI STYLE =================
img_b64 = get_base64_img(LOGO_PATH)
st.markdown(f"""
    <style>
    .header-container {{ display: flex; align-items: center; background-color: white; padding: 15px; border-radius: 12px; border-bottom: 5px solid #2e7d32; margin-bottom: 25px; box-shadow: 0px 4px 10px rgba(0,0,0,0.05); }}
    .logo-img {{ width: 90px; height: 90px; margin-right: 25px; }}
    .card {{ background: white; padding: 20px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); text-align: center; border-top: 5px solid #2e7d32; }}
    </style>
    """, unsafe_allow_html=True)

# ================= 5. MAIN APP =================
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    _, col_mid, _ = st.columns([1, 1.2, 1])
    with col_mid:
        if os.path.exists(LOGO_PATH): st.image(LOGO_PATH, width=120)
        st.markdown("<h2 style='text-align:center;'>Systemii Galmee Dadar</h2>", unsafe_allow_html=True)
        with st.form("login"):
            u = st.text_input("Username")
            p = st.text_input("Password", type="password")
            if st.form_submit_button("Seeni"):
                if u == "DAD" and p == "2026":
                    st.session_state.logged_in = True; st.rerun()
                else: st.error("Dogoggora Username ykn Password!")
else:
    # Header
    logo_src = f"data:image/png;base64,{img_b64}" if img_b64 else ""
    st.markdown(f'<div class="header-container"><img src="{logo_src}" class="logo-img"><div><h1 style="margin:0; font-size: 28px;">BULCHIINSA MAGAALAA DADAR</h1><h2 style="margin:0; font-size: 20px; color: #4caf50;">WAAJJIRA LAFAA</h2></div></div>', unsafe_allow_html=True)
    
    df = load_data()
    menu = st.sidebar.radio("FILANNOO", ["📊 Dashboard", "📝 Galmee Haaraa", "🏆 Badhaasa Ogeeyyii", "🔍 Barbaadi/Edit", "Ba'i"])

    # --- 1. DASHBOARD ---
    if menu == "📊 Dashboard":
        st.header("📊 Dashboard")
        if not df.empty:
            c1, c2, c3 = st.columns(3)
            with c1: st.markdown(f"<div class='card'><p>💰 Galii</p><h3>{df['Kafaltii_Taj'].sum():,.2f} ETB</h3></div>", unsafe_allow_html=True)
            with c2: st.markdown(f"<div class='card'><p>👥 Maamiltoota</p><h3>{len(df)}</h3></div>", unsafe_allow_html=True)
            with c3: st.markdown(f"<div class='card'><p>👷 Ogeeyyii</p><h3>{df['Maqaa_Ogeessa'].nunique()}</h3></div>", unsafe_allow_html=True)
            st.area_chart(df.groupby('Ji\'a')['Kafaltii_Taj'].sum().reindex(MONTH_ORDER).fillna(0))
        else: st.info("Data'n hojii hin jiru.")

    # --- 2. GALMEE HAARAA ---
    elif menu == "📝 Galmee Haaraa":
        st.header("📝 Galmee Tajaajilaa")
        GATII_DICT = {
            "Gibira": ["Gibira Baaxii Gooroo", "Gibira Lafa Qonnaa", "Gibira Manaa"],
            "Liizii": ["Liizii Waggaa", "Jijjiirraa Maqaa", "Kafaltii Liizii Duraa"],
            "Ittii Fayyaddam": ["Hayyama Itti Fayyadama Lafaa", "Humna Mahandiisaa"],
            "Kaartaa": ["Kaartaa Lafa", "Kaartaa Kadastaara", "Suphaa Kaartaa"]
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
            c1, c2 = st.columns(2)
            maqaa_f = c1.text_input("Maqaa Abbaa Dhimmaa *")
            ara_f = c2.text_input("Araddaa *")
            qax_f = c1.text_input("Qaxana *")
            ogeessa = c2.text_input("Maqaa Ogeessaa *")
            nagahee_file = st.file_uploader("Nagahee Scan (JPG/PNG)", type=['jpg','png','jpeg'])
            
            if st.form_submit_button("💾 Galmeessi"):
                if not (maqaa_f and ara_f and ogeessa) or not details:
                    st.error("⚠️ Maaloo, bakka (*) qaban guuti!")
                else:
                    if nagahee_file:
                        f_name = f"{maqaa_f.replace(' ','_')}_{datetime.now().strftime('%H%M%S')}.jpg"
                        with open(os.path.join(NAGAHEE_DIR, f_name), "wb") as f: f.write(nagahee_file.getbuffer())
                    
                    new_row = [datetime.now().strftime('%d/%m/%Y'), maqaa_f, ara_f, qax_f, ", ".join(details), ogeessa, sum(d_fees.values())]
                    df = pd.concat([df, pd.DataFrame([new_row], columns=COL_NAMES)], ignore_index=True)
                    if save_data(df):
                        st.success(f"✅ Galmeen {maqaa_f} raawwatameera!"); st.balloons()

    # --- 3. BADHAASA ---
    elif menu == "🏆 Badhaasa Ogeeyyii":
        st.header("🏆 Badhaasa & Sartiifiikeeta Ogeeyyii")
        cl, cr = st.columns(2)
        l_file = cl.file_uploader("Logo Bitaa (Optional)", type=['png', 'jpg'], key="logo_l")
        r_file = cr.file_uploader("Logo Mirgaa (Optional)", type=['png', 'jpg'], key="logo_r")

        if not df.empty and 'Maqaa_Ogeessa' in df.columns:
            top_3 = df['Maqaa_Ogeessa'].value_counts().head(3)
            cols = st.columns(3)
            for i, (name, count) in enumerate(top_3.items(), 1):
                with cols[i-1]:
                    st.markdown(f"<div class='card'><h2 style='color: gold;'>{i}FFAA</h2><h4>{name}</h4><p>Hojii: {count}</p></div><br>", unsafe_allow_html=True)
                    pdf_data = create_advanced_pdf(name, count, i, l_file, r_file)
                    st.download_button(label=f"📥 PDF {i}ffaa Buusi", data=pdf_data, file_name=f"Cert_{name}.pdf", mime="application/pdf", key=f"dl_{i}")
        else: st.warning("Data'n hin jiru.")

    # --- 4. SEARCH & EDIT ---
    elif menu == "🔍 Barbaadi/Edit":
        st.header("🔍 Barbaadi fi Sirreessi")
        q = st.text_input("Maqaa Abbaa Dhimmaa Barbaadi...")
        if q and not df.empty:
            results = df[df['Maqaa_Abbaa_Dhimmaa'].str.contains(q, case=False, na=False)]
            for idx, row in results.iterrows():
                with st.expander(f"📄 {row['Maqaa_Abbaa_Dhimmaa']} - {row['Guyyaa']}"):
                    c1, c2 = st.columns(2)
                    n_n = c1.text_input("Maqaa Sirreessi", row['Maqaa_Abbaa_Dhimmaa'], key=f"n_{idx}")
                    n_f = c2.number_input("Kafaltii (ETB)", float(row['Kafaltii_Taj']), key=f"f_{idx}")
                    if st.button("💾 Update", key=f"u_{idx}"):
                        df.at[idx, 'Maqaa_Abbaa_Dhimmaa'] = n_n
                        df.at[idx, 'Kafaltii_Taj'] = n_f
                        if save_data(df): st.success("Sirreeffameera!"); st.rerun()
                    if st.button("🗑 Haqi", key=f"d_{idx}"):
                        df = df.drop(idx)
                        if save_data(df): st.warning("Haqameera!"); st.rerun()

    # --- 5. LOGOUT ---
    elif menu == "Ba'i":
        st.session_state.logged_in = False
        st.rerun()
