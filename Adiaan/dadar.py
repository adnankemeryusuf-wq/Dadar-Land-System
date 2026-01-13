import streamlit as st
import pandas as pd
import os
import io
import requests
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont

# --- CONFIGURATION TELEGRAM ---
BOT_TOKEN = "8357193631:AAHCuSnXzjZTQaglkmcS0gq-EvqnkIQLDBI"
CHAT_ID_MANAGER = "7329587700"

# ================= 1. CONFIG & STYLING =================
st.set_page_config(page_title="Dadar Land Admin Pro", layout="wide", page_icon="🏢")

st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #f1f8e9 0%, #ffffff 100%); }
    [data-testid="stSidebar"] { background-color: #1b5e20 !important; }
    [data-testid="stSidebar"] * { color: #ffffff !important; }
    div.stForm { background: white; border-radius: 15px; padding: 25px; border: 2px solid #2e7d32; box-shadow: 0px 4px 15px rgba(0,0,0,0.1); }
    .stButton>button { background: linear-gradient(90deg, #4caf50, #2e7d32); color: white; border-radius: 8px; font-weight: bold; width: 100%; height: 45px; }
    
    /* Dashboard & Award Cards */
    .metric-container { display: flex; justify-content: space-between; gap: 10px; margin-bottom: 25px; }
    .card { background: white; padding: 20px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); text-align: center; flex: 1; border-top: 5px solid #2e7d32; }
    .award-card { background: white; padding: 20px; border-radius: 15px; text-align: center; box-shadow: 2px 2px 10px rgba(0,0,0,0.1); }
    </style>
    """, unsafe_allow_html=True)

# ================= 2. DATA & SETTINGS =================
DATA_FILE = "dadar_final_report.txt"
COL_NAMES = ['Guyyaa', 'Maqaa_Abbaa_Dhimmaa', 'Araddaa', 'Qaxana', 'Gosa_Tajajjilaa', 'Maqaa_Ogeessa', 'Kafaltii_Taj']

GATII_DICT = {
    "Gibira": ["Gibira Baaxii Gooroo", "Gibira Lafa Qonnaa", "Gibira Manaa"],
    "Liizii": ["Liizii Waggaa", "Jijjiirraa Maqaa", "Kafaltii Liizii Duraa", "TOT"],
    "Ittii Fayyaddam": ["Hayyama Itti Fayyadama Lafaa", "Humna Mahandiisaa"],
    "Kaartaa": ["Kaartaa Manaa", "Kaartaa Kadastaara", "Kaartaa Lafa Qonna Magaalaa", "Kaartaa Haaromsuu"],
    "Dhimma Dangaa": ["Kafaltii Humna Mandisaa"],
    "Dhimma Mana Murtii": ["Ugura Mana Murtii", "Uguraa Mana Murtii Kaasuu"],
    "Liqii Bankii": ["Dorkka Liqii Bankii", "Dorkkaa Liqii Bankii Kaasuu"]
}

MONTH_ORDER = ["Fulbaana", "Onkololeessa", "Sadaasa", "Muddee", "Amajjii", "Guraandhala", "Bitootessa", "Eebila", "Caamsaa", "Waxabajjii", "Adooleessa", "Hagayya"]
MONTH_MAP = {9: "Fulbaana", 10: "Onkololeessa", 11: "Sadaasa", 12: "Muddee", 1: "Amajjii", 2: "Guraandhala", 3: "Bitootessa", 4: "Eebila", 5: "Caamsaa", 6: "Waxabajjii", 7: "Adooleessa", 8: "Hagayya"}
WEEKDAY_MAP = {0: "Wixata", 1: "Filatama", 2: "Roobii", 3: "Kamisa", 4: "Jimmata", 5: "Sanbata", 6: "Dilbata"}

def load_data():
    if not os.path.exists(DATA_FILE) or os.stat(DATA_FILE).st_size == 0:
        return pd.DataFrame(columns=COL_NAMES)
    df = pd.read_csv(DATA_FILE, sep="|", names=COL_NAMES, header=None, encoding='utf-8')
    df['Date_Obj'] = pd.to_datetime(df['Guyyaa'], format='%d/%m/%Y', errors='coerce')
    df['Waggaa'] = df['Date_Obj'].dt.year
    df['Ji\'a'] = df['Date_Obj'].dt.month.map(MONTH_MAP)
    df['Torbee'] = (df['Date_Obj'].dt.day - 1) // 7 + 1
    df['Guyyaa_Torbee'] = df['Date_Obj'].dt.dayofweek.map(WEEKDAY_MAP)
    df['Kurmaana'] = df['Date_Obj'].dt.month.apply(lambda x: 1 if x in [9,10,11,12] else (2 if x in [1,2,3] else (3 if x in [4,5,6] else 4)))
    return df

def save_data(df_to_save):
    df_to_save[COL_NAMES].to_csv(DATA_FILE, sep="|", index=False, header=False, encoding="utf-8")

# ================= 3. SARTIIFIKEETA GENERATOR =================
def create_dadar_cert(name, count, rank, logo_file=None):
    width, height = 1123, 794
    img = Image.new('RGB', (width, height), (255, 255, 255))
    draw = ImageDraw.Draw(img)

    # Halluuwwan: 1st=Gold, 2nd=Silver, 3rd=Bronze (CD7F32)
    rank_colors = {1: "#D4AF37", 2: "#C0C0C0", 3: "#CD7F32"}
    rank_text = {1: "1FFAA (GOLD)", 2: "2FFAA (SILVER)", 3: "3FFAA (BRONZE)"}
    main_color = rank_colors.get(rank, "#1b5e20")

    # Border
    draw.rectangle([20, 20, width-20, height-20], outline=main_color, width=15)
    draw.rectangle([45, 45, width-45, height-45], outline="#f1f1f1", width=2)

    if logo_file:
        logo = Image.open(logo_file).convert("RGBA").resize((130, 130))
        img.paste(logo, (width//2 - 65, 60), logo)

    try:
        f_header = ImageFont.truetype("arialbd.ttf", 45)
        f_name = ImageFont.truetype("arialbd.ttf", 55)
        f_body = ImageFont.truetype("arial.ttf", 30)
    except:
        f_header = f_name = f_body = ImageFont.load_default()

    draw.text((width//2, 210), "SARTIIFIKETA BEEKAMTII", fill=main_color, font=f_header, anchor="mm")
    draw.text((width//2, 260), "Waajjira Lafaa Bulchiinsa Magaalaa Dadar", fill="#333", font=f_body, anchor="mm")
    draw.text((width//2, 340), "Sartiifiketiin Gootummaa Hojii kun kan kennameef:", fill="#555", font=f_body, anchor="mm")
    draw.text((width//2, 420), f"Obbo/Adde: {name.upper()}", fill=main_color, font=f_name, anchor="mm")
    
    msg = (f"Waggaa 2026 keessatti tajaajila saffisaa, iftoomina qabuu fi amannamaa ta'een\n"
           f"Abbootii Dhimmaa {count} tajaajiluun bu'aa qabeessa ta'anii waan argamaniif\n"
           f"beekamtii {rank_text[rank]} kanaan badhaafamaniiru.")
    draw.text((width//2, 540), msg, fill="#333", font=f_body, anchor="mm", align="center")

    draw.line([150, 700, 450, 700], fill="black", width=2)
    draw.text((300, 715), "Itti Gaafatamaa Waajjiraa", font=f_body, fill="black", anchor="mm")
    draw.line([673, 700, 973, 700], fill="black", width=2)
    draw.text((823, 715), "Guyyaa: " + datetime.now().strftime("%d/%m/%Y"), font=f_body, fill="black", anchor="mm")

    return img

# ================= 4. APP LOGIC =================
if 'logged_in' not in st.session_state: st.session_state.logged_in = False

if not st.session_state.logged_in:
    _, col_mid, _ = st.columns([1, 1.2, 1])
    with col_mid:
        st.markdown("<h2 style='text-align:center; color:#1b5e20;'>🏢 Admin Login</h2>", unsafe_allow_html=True)
        u, p = st.text_input("Username"), st.text_input("Password", type="password")
        if st.button("Seeni"):
            if u == "admin" and p == "123":
                st.session_state.logged_in = True; st.rerun()
            else: st.error("Dogoggora!")
else:
    with st.sidebar:
        st.markdown("### 🏢 DADAR LAND SYSTEM")
        menu = st.radio("FILANNOO", ["📊 Dashboard", "📝 Galmee Haaraa", "📈 Gabaasa Bal'aa", "🏆 Badhaasa Ogeeyyii", "🔍 Barbaadi/Edit", "Ba'i"])

    df = load_data()

    if menu == "📊 Dashboard":
        st.markdown("<h1 style='text-align: center; color: #1b5e20;'>📊 Dashboard</h1>", unsafe_allow_html=True)
        if not df.empty:
            t_income = df['Kafaltii_Taj'].sum()
            t_clients = len(df)
            st.markdown(f"""
                <div class="metric-container">
                    <div class="card"><p style="color:#666;">💰 WALIIGALA GALII</p><h2 style="color:#2e7d32;">{t_income:,.2f} ETB</h2></div>
                    <div class="card"><p style="color:#666;">👥 TAJAAJILAMTOOTA</p><h2 style="color:#2e7d32;">{t_clients}</h2></div>
                </div>
            """, unsafe_allow_html=True)
            st.area_chart(df.groupby('Ji\'a')['Kafaltii_Taj'].sum().reindex(MONTH_ORDER).fillna(0))

    elif menu == "📝 Galmee Haaraa":
        st.header("📝 Galmee Tajaajilaa")
        selected_main = st.multiselect("🟢 Gosa Tajaajilaa", list(GATII_DICT.keys()))
        details, d_fees = [], {}
        if selected_main:
            for g in selected_main:
                subs = st.multiselect(f"Filannoo {g}:", GATII_DICT[g], key=f"m_{g}")
                for s in subs:
                    details.append(f"{g}({s})")
                    d_fees[f"{g}_{s}"] = st.number_input(f"Kafaltii {s}", min_value=0.0, key=f"f_{g}_{s}")
        
        with st.form("entry", clear_on_submit=True):
            c1, c2 = st.columns(2)
            maqaa_f, ara_f = c1.text_input("Maqaa Abbaa Dhimmaa"), c2.text_input("Araddaa")
            qax_f, ogeessa = c1.text_input("Qaxana"), c2.text_input("Maqaa Ogeessaa")
            if st.form_submit_button("💾 Galmeessi"):
                if maqaa_f and details:
                    new = [datetime.now().strftime('%d/%m/%Y'), maqaa_f, ara_f, qax_f, ", ".join(details), ogeessa, sum(d_fees.values())]
                    df = pd.concat([df, pd.DataFrame([new], columns=COL_NAMES)], ignore_index=True)
                    save_data(df); st.success("Galmeeffameera!")

    elif menu == "🏆 Badhaasa Ogeeyyii":
        st.header("🏆 Badhaasa Ogeessa Cimaa Tartiiba 1-3")
        if not df.empty:
            u_logo = st.file_uploader("Logo Waajjiraa Galchi", type=["png", "jpg", "jpeg"])
            top_performers = df['Maqaa_Ogeessa'].value_counts().head(3)
            
            col_ranks = st.columns(3)
            medals = ["🥇 1FFAA", "🥈 2FFAA", "🥉 3FFAA"]
            styles = ["#D4AF37", "#C0C0C0", "#CD7F32"]

            for i, (name, count) in enumerate(top_performers.items()):
                with col_ranks[i]:
                    st.markdown(f"""<div class="award-card" style="border-top: 10px solid {styles[i]};">
                        <h2 style="color:{styles[i]};">{medals[i]}</h2><h3>{name}</h3><p>Abbaa Dhimmaa: <b>{count}</b></p></div>""", unsafe_allow_html=True)
                    if st.button(f"Sartiifiikeeta {i+1}ffaa", key=f"btn_{i}"):
                        cert = create_dadar_cert(name, count, i+1, u_logo)
                        st.image(cert, use_container_width=True)
                        buf = io.BytesIO(); cert.save(buf, format="PNG")
                        st.download_button(f"📥 Download {i+1}ffaa", buf.getvalue(), f"Cert_{name}.png", "image/png")
        else: st.warning("Data'n hin jiru.")

    elif menu == "📈 Gabaasa Bal'aa":
        # ... (Koodii gabaasaa fi calalii kanaan duraa asitti ni dabalama)
        st.header("📈 Gabaasa")
        st.dataframe(df[COL_NAMES])

    elif menu == "🔍 Barbaadi/Edit":
        q = st.text_input("Maqaa barreessi...")
        if q:
            res = df[df['Maqaa_Abbaa_Dhimmaa'].str.contains(q, case=False, na=False)]
            st.dataframe(res)

    elif menu == "Ba'i": st.session_state.logged_in = False; st.rerun()
