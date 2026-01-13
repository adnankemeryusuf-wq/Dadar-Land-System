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
    
    /* Medal Style Cards */
    .award-card {
        background: white; padding: 25px; border-radius: 20px;
        text-align: center; box-shadow: 0 10px 20px rgba(0,0,0,0.1);
        border-bottom: 8px solid #2e7d32; transition: 0.3s;
    }
    .award-card:hover { transform: translateY(-10px); }
    .gold { border-color: #D4AF37; }
    .silver { border-color: #C0C0C0; }
    .bronze { border-color: #CD7F32; }
    </style>
    """, unsafe_allow_html=True)

# ================= 2. DATA MANAGEMENT =================
DATA_FILE = "dadar_final_report.txt"
COL_NAMES = ['Guyyaa', 'Maqaa_Abbaa_Dhimmaa', 'Araddaa', 'Qaxana', 'Gosa_Tajajjilaa', 'Maqaa_Ogeessa', 'Kafaltii_Taj']

def load_data():
    if not os.path.exists(DATA_FILE) or os.stat(DATA_FILE).st_size == 0:
        return pd.DataFrame(columns=COL_NAMES)
    df = pd.read_csv(DATA_FILE, sep="|", names=COL_NAMES, header=None, encoding='utf-8')
    return df

def save_data(df_to_save):
    df_to_save[COL_NAMES].to_csv(DATA_FILE, sep="|", index=False, header=False, encoding="utf-8")

# ================= 3. ORIGINAL CERTIFICATE GENERATOR =================
def create_original_cert(name, count, rank, logo_file=None):
    # A4 Landscape (1123 x 794)
    width, height = 1123, 794
    img = Image.new('RGB', (width, height), (255, 255, 255))
    draw = ImageDraw.Draw(img)

    # Halluuwwan Badhaasaa
    rank_colors = {1: "#D4AF37", 2: "#95a5a6", 3: "#d35400"}
    rank_titles = {1: "1ffaa (Gold)", 2: "2ffaa (Silver)", 3: "3ffaa (Bronze)"}
    main_color = rank_colors.get(rank, "#1b5e20")

    # 1. Border Orjinala (Double Frame)
    draw.rectangle([20, 20, width-20, height-20], outline=main_color, width=15)
    draw.rectangle([40, 40, width-40, height-40], outline="#ecf0f1", width=2)
    
    # 2. Logo / Medal Icon Place
    if logo_file:
        logo = Image.open(logo_file).convert("RGBA").resize((130, 130))
        img.paste(logo, (width//2 - 65, 60), logo)

    # 3. Fonts (Loading System Fonts)
    try:
        f_title = ImageFont.truetype("arial.ttf", 70)
        f_sub = ImageFont.truetype("arial.ttf", 35)
        f_name = ImageFont.truetype("arial.ttf", 55)
    except:
        f_title = ImageFont.load_default()
        f_sub = ImageFont.load_default()
        f_name = ImageFont.load_default()

    # 4. Barreeffama Saratifiketaa
    draw.text((width//2, 230), "WARAQAA RAGAA BADHAASAA", fill=main_color, font=f_title, anchor="mm")
    draw.text((width//2, 300), f"Ogeessa Cimaa Tartiiba {rank_titles[rank]}", fill="#7f8c8d", font=f_sub, anchor="mm")
    
    draw.text((width//2, 380), "Ragaan kun kabajaa fi nishaanidhaan kan kennameef:", fill="#34495e", font=f_sub, anchor="mm")
    draw.text((width//2, 460), name.upper(), fill="#2c3e50", font=f_name, anchor="mm")
    
    msg = f"Waggaa tajaajilaa 2026 keessatti tajaajilamtoota {count} tajaajiluun\nbu'aa olaanaa galmeessisuu keessaniif ragaan kun kennameera."
    draw.text((width//2, 560), msg, fill="#5d6d7e", font=f_sub, anchor="mm", align="center")

    # 5. Bottom Signatures
    draw.line([150, 700, 400, 700], fill="black", width=2)
    draw.text((275, 715), "Guyyaa", font=f_sub, fill="black", anchor="mm")
    
    draw.line([723, 700, 973, 700], fill="black", width=2)
    draw.text((848, 715), "Mallattoo Hoogganaa", font=f_sub, fill="black", anchor="mm")

    return img

# ================= 4. MAIN APP =================
if 'logged_in' not in st.session_state: st.session_state.logged_in = False

if not st.session_state.logged_in:
    _, col_log, _ = st.columns([1, 1, 1])
    with col_log:
        st.title("🔐 Login")
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")
        if st.button("SEENI"):
            if u == "admin" and p == "123": st.session_state.logged_in = True; st.rerun()
else:
    df = load_data()
    with st.sidebar:
        st.title("🏢 DADAR LAND")
        menu = st.radio("FILANNOO", ["📊 Dashboard", "📝 Galmee Haaraa", "📈 Gabaasa Bal'aa", "🏆 Badhaasa Ogeeyyii", "🔍 Barbaadi/Edit", "🚪 Ba'i"])

    if menu == "📊 Dashboard":
        st.header("📊 Dashboard")
        c1, c2 = st.columns(2)
        c1.metric("Waliigala Galii", f"{df['Kafaltii_Taj'].sum():,.2f} ETB")
        c2.metric("Tajaajilamtoota", len(df))
        st.area_chart(df.groupby('Maqaa_Ogeessa')['Kafaltii_Taj'].sum())

    elif menu == "🏆 Badhaasa Ogeeyyii":
        st.header("🏆 Badhaasa Ogeessa Cimaa Waggaa")
        if not df.empty:
            st.info("Logo mana hojii ykn Nishaan (Medal) filadhu")
            u_logo = st.file_uploader("Logo Galchi", type=["png", "jpg"])
            
            # Ranking Logic
            top_3 = df['Maqaa_Ogeessa'].value_counts().head(3)
            
            cols = st.columns(3)
            ranks = ["gold", "silver", "bronze"]
            medals = ["🥇", "🥈", "🥉"]

            for i, (name, count) in enumerate(top_3.items()):
                with cols[i]:
                    st.markdown(f"""
                        <div class="award-card {ranks[i]}">
                            <h1 style='font-size: 50px;'>{medals[i]}</h1>
                            <h3>{name}</h3>
                            <p>Abbaa Dhimmaa: <b>{count}</b></p>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    if st.button(f"Hojjedhu ({i+1}ffaa)", key=f"btn_{i}"):
                        cert_img = create_original_cert(name, count, i+1, u_logo)
                        st.image(cert_img, use_container_width=True)
                        
                        buf = io.BytesIO()
                        cert_img.save(buf, format="PNG")
                        st.download_button(f"📥 Download Cert {i+1}", buf.getvalue(), f"Award_{name}.png", "image/png")
        else:
            st.warning("Data'n hin jiru.")

    elif menu == "📝 Galmee Haaraa":
        # ... (Kutaa galmee isa duraa hunda asitti ni dabalama)
        st.write("Galmee haaraa asitti guuti...")

    elif menu == "🚪 Ba'i":
        st.session_state.logged_in = False
        st.rerun()
