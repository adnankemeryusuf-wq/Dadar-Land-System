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
    .card { background: white; padding: 20px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); text-align: center; border-top: 5px solid #2e7d32; }
    .rank-1 { background: #fffdf0; border: 2px solid #d4af37; border-radius: 10px; padding: 10px; }
    .rank-2 { background: #f8f8f8; border: 2px solid #aaa; border-radius: 10px; padding: 10px; }
    .rank-3 { background: #fff5f0; border: 2px solid #cd7f32; border-radius: 10px; padding: 10px; }
    </style>
    """, unsafe_allow_html=True)

# ================= 2. DATA MANAGEMENT =================
DATA_FILE = "dadar_final_report.txt"
COL_NAMES = ['Guyyaa', 'Maqaa_Abbaa_Dhimmaa', 'Araddaa', 'Qaxana', 'Gosa_Tajajjilaa', 'Maqaa_Ogeessa', 'Kafaltii_Taj']

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

# ================= 3. CERTIFICATE GENERATOR =================
def create_staff_cert(name, count, rank, logo_file=None):
    width, height = 1123, 794
    img = Image.new('RGB', (width, height), (255, 255, 255))
    draw = ImageDraw.Draw(img)

    # Halluu akka tartiibaatiin (1st=Gold, 2nd=Silver, 3rd=Bronze)
    colors = {1: "#d4af37", 2: "#aaa9ad", 3: "#cd7f32"}
    rank_text = {1: "1FFAA", 2: "2FFAA", 3: "3FFAA"}
    theme_color = colors.get(rank, "#1b5e20")

    draw.rectangle([20, 20, width-20, height-20], outline=theme_color, width=15)
    
    if logo_file:
        logo = Image.open(logo_file).convert("RGBA").resize((120, 120))
        img.paste(logo, (width//2 - 60, 50), logo)

    try:
        f_big = ImageFont.truetype("arial.ttf", 60)
        f_med = ImageFont.truetype("arial.ttf", 35)
    except:
        f_big = ImageFont.load_default()
        f_med = ImageFont.load_default()

    draw.text((width//2, 220), "BADHAASA OGEESSA CIMAA", fill=theme_color, font=f_big, anchor="mm")
    draw.text((width//2, 290), f"TARTEE {rank_text[rank]}", fill=theme_color, font=f_med, anchor="mm")
    draw.text((width//2, 400), name.upper(), fill="#333", font=f_big, anchor="mm")
    
    msg = f"Waggaa kana keessatti tajaajilamtoota {count} tajaajiluun\nogeessa cimaa ta'uu keessaniif ragaan kun kennameera."
    draw.text((width//2, 520), msg, fill="#555", font=f_med, anchor="mm", align="center")
    
    return img

# ================= 4. APP INTERFACE =================
if 'logged_in' not in st.session_state: st.session_state.logged_in = False

if not st.session_state.logged_in:
    # Login Simplified
    u = st.text_input("Username")
    p = st.text_input("Password", type="password")
    if st.button("Seeni"):
        if u == "admin" and p == "123": st.session_state.logged_in = True; st.rerun()
else:
    df = load_data()
    menu = st.sidebar.radio("MENU", ["📊 Dashboard", "📈 Ogeeyyii Cimaa", "🚪 Ba'i"])

    if menu == "📊 Dashboard":
        st.title("🏢 Dadar Land Dashboard")
        st.write(f"Waliigala Galii: **{df['Kafaltii_Taj'].sum():,.2f} ETB**")
        st.dataframe(df.tail(10), use_container_width=True)

    elif menu == "📈 Ogeeyyii Cimaa":
        st.header("🏆 Badhaasa Ogeeyyii Cimaa Waggaa")
        
        if not df.empty:
            # Logo upload
            user_logo = st.file_uploader("Logo Mana Hojii Galchi", type=["png", "jpg"])
            
            # Tartiba Ogeeyyii
            ranking = df['Maqaa_Ogeessa'].value_counts().head(3)
            
            cols = st.columns(3)
            for i, (name, count) in enumerate(ranking.items(), 1):
                with cols[i-1]:
                    st.markdown(f"<div class='rank-{i}'>", unsafe_allow_html=True)
                    st.markdown(f"### 🥇 {i}. {name}")
                    st.write(f"Tajaajilamtoota: **{count}**")
                    
                    if st.button(f"Saratifikeeta {i}ffaa", key=f"btn_{i}"):
                        cert = create_staff_cert(name, count, i, user_logo)
                        st.image(cert, use_container_width=True)
                        
                        buf = io.BytesIO()
                        cert.save(buf, format="PNG")
                        st.download_button(f"📥 Download {i}ffaa", buf.getvalue(), f"Rank_{i}_{name}.png", "image/png")
                    st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.warning("Data'n hin jiru.")

    elif menu == "🚪 Ba'i":
        st.session_state.logged_in = False
        st.rerun()
