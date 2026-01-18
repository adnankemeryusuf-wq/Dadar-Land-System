import streamlit as st
import pandas as pd
import os, io, requests
from datetime import datetime
from fpdf import FPDF

# ================= 1. CONFIGURATION =================
LOGO_PATH = "Adiaan/logo.png"
DATA_FILE = "dadar_final_report.txt"
NAGAHEE_DIR = "Adiaan/nagahee"
COL_NAMES = ['Guyyaa', 'Maqaa_Abbaa_Dhimmaa', 'Araddaa', 'Qaxana', 'Gosa_Tajajjilaa', 'Maqaa_Ogeessa', 'Kafaltii_Taj']

if not os.path.exists(NAGAHEE_DIR): os.makedirs(NAGAHEE_DIR, exist_ok=True)

# --- CORE FUNCTIONS ---
def load_data():
    if not os.path.exists(DATA_FILE) or os.stat(DATA_FILE).st_size == 0:
        return pd.DataFrame(columns=COL_NAMES)
    df = pd.read_csv(DATA_FILE, sep="|", names=COL_NAMES, header=None)
    df['Date_Obj'] = pd.to_datetime(df['Guyyaa'], format='%d/%m/%Y', errors='coerce')
    return df

def save_data(df_to_save):
    df_to_save[COL_NAMES].to_csv(DATA_FILE, sep="|", index=False, header=False, encoding="utf-8")

# ================= 2. UI SETUP =================
st.set_page_config(page_title="Dadar Land System", layout="wide")

df = load_data()
menu = st.sidebar.radio("FILANNOO", ["📊 Dashboard", "📝 Galmee Haaraa", "🏆 Badhaasa", "📈 Gabaasa"])

# ================= 3. DASHBOARD =================
if menu == "📊 Dashboard":
    st.title("📊 Dashboard Waliigalaa")
    c1, c2, c3 = st.columns(3)
    c1.metric("Waliigala Galii", f"{df['Kafaltii_Taj'].sum():,.2f} ETB")
    c2.metric("Baay'ina Maamilaa", len(df))
    c3.metric("Ogeeyyii Hojjetan", df['Maqaa_Ogeessa'].nunique())
    
# ================= 4. REGISTRATION (GALMEE) =================
elif menu == "📝 Galmee Haaraa":
    st.header("📝 Galmee Tajaajilaa Haaraa")
    
    # --- RAMADDII TAJAAJILAA (Dictionary) ---
    GATII_DICT = {
        "🏷️ Gibira & Kaffaltii": ["Gibira Baaxii Gooroo", "Gibira Lafa Qonnaa", "Kaffaltii Liizii Waggaa", "Kaffaltii Liizii Duraa", "TOT (Turnover Tax)"],
        "📜 Kaartaa & Qabiyyee": ["Kaartaa Haaraa", "Kaartaa Bakka Bu'aa", "Kaartaa Kadastaaraa", "Jijjiirraa Maqaa (Gift/Sale)", "Sirreeffama Daangaa", "Ganda Irraa gara Magaalaatti"],
        "🏗️ Pilaanii & Ijaarsa": ["Pilaanii Magaalaa", "Itti Fayyadama Lafaa (Land Use)", "Humna Mahandisummaa"],
        "⚖️ Dhimma Seeraa": ["Ugura Mana Murtii", "Ugura Kaasuu", "Waliigaltee Liqii Baankii", "Waliigaltee Hiikuu", "Dhimma Dhala (Inheritance)"],
        "📂 Tajaajila Biroo": ["Waraqaa Ragaa (Clearance)", "Deebii Iyyannoo"]
    }

    selected_cats = st.multiselect("🟢 Gosa Tajaajilaa Filadhu", list(GATII_DICT.keys()))
    
    details, d_fees = [], {}
    
    # Formataa bifa Expander qabun kaffaltii guuchisuu
    for cat in selected_cats:
        with st.expander(f"Kaffaltii {cat} Guuti", expanded=True):
            subs = st.multiselect(f"Tajaajiloota {cat} keessaa filadhu:", GATII_DICT[cat], key=f"sel_{cat}")
            for s in subs:
                details.append(f"{cat}({s})")
                d_fees[f"{cat}_{s}"] = st.number_input(f"Kaffaltii {s} (ETB):", min_value=0.0, key=f"in_{cat}_{s}")

    st.divider()
    
    # --- ODEEFFANNOO MAAMILAA ---
    with st.form("customer_form", clear_on_submit=True):
        st.subheader("Maqaa Maamilaa fi Odeeffannoo Biroo")
        col1, col2 = st.columns(2)
        m_maqaa = col1.text_input("Maqaa Maamilaa *")
        m_qaxana = col2.text_input("Qaxana")
        m_araddaa = col1.text_input("Araddaa *")
        m_ogeessa = col2.text_input("Ogeessa Raawwate *")
        
        nagahee_img = st.file_uploader("Nagahee Scan (JPG/PNG)", type=['jpg','png','jpeg'])
        
        if st.form_submit_button("💾 Galmeessi"):
            if not m_maqaa or not m_araddaa or not details:
                st.error("⚠️ Maaloo, bakka mallattoo (*) qaban hunda guuti!")
            else:
                # Nagahee Save gochuu
                if nagahee_img:
                    path = os.path.join(NAGAHEE_DIR, f"{m_maqaa}_{datetime.now().strftime('%H%M%S')}.jpg")
                    with open(path, "wb") as f: f.write(nagahee_img.getbuffer())
                
                # Data dabalachuu
                new_data = [
                    datetime.now().strftime('%d/%m/%Y'), m_maqaa, m_araddaa, m_qaxana, 
                    ", ".join(details), m_ogeessa, sum(d_fees.values())
                ]
                df = pd.concat([df, pd.DataFrame([new_data], columns=COL_NAMES)], ignore_index=True)
                save_data(df)
                st.success(f"✅ Galmeen {m_maqaa} milkaa'inaan raawwatameera!")
                st.balloons()

# ================= 5. GABAASA =================
elif menu == "📈 Gabaasa":
    st.header("📈 Gabaasa Galmee fi Kafaltii")
    if not df.empty:
        st.dataframe(df[COL_NAMES], use_container_width=True)
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Gabaasa CSV Buufadhu", csv, "gabaasa_dadar.csv", "text/csv")
    else:
        st.info("Galmeen agarsiifamu hin jiru.")

# ================= 6. BADHAASA =================
elif menu == "🏆 Badhaasa":
    st.header("🏆 Sadarkaa Ogeeyyii")
    if not df.empty:
        top = df['Maqaa_Ogeessa'].value_counts().head(3)
        for i, (name, count) in enumerate(top.items()):
            st.write(f"**Sadarkaa {i+1}ffaa:** {name} (Hojii {count} raawwate)")
