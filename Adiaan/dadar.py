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

st.set_page_config(
    page_title="Dadar Land Customer Registration System", 
    page_icon="🏢", 
    layout="wide"
)

# Koodii iccitii (Security)
BOT_TOKEN = "8357193631:AAHCuSnXzjZTQaglkmcS0gq-EvqnkIQLDBI"
CHAT_ID_MANAGER = "7329587700"
DATA_FILE = "dadar_final_report.txt"

COL_NAMES = ['Guyyaa', 'Maqaa_Abbaa_Dhimmaa', 'Araddaa', 'Qaxana', 'Gosa_Tajajjilaa', 'Maqaa_Ogeessa', 'Kafaltii_Taj']
MONTH_ORDER = ["Fulbaana", "Onkololeessa", "Sadaasa", "Muddee", "Amajjii", "Guraandhala", "Bitootessa", "Eebila", "Caamsaa", "Waxabajjii", "Adooleessa", "Hagayya"]
MONTH_MAP = {9: "Fulbaana", 10: "Onkololeessa", 11: "Sadaasa", 12: "Muddee", 1: "Amajjii", 2: "Guraandhala", 3: "Bitootessa", 4: "Eebila", 5: "Caamsaa", 6: "Waxabajjii", 7: "Adooleessa", 8: "Hagayya"}

# Miidhagina Fuula (CSS)
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
    # Data qulqulleessanii galmeessuu
    df_to_save[COL_NAMES].to_csv(DATA_FILE, sep="|", index=False, header=False, encoding="utf-8")

def send_to_telegram(caption, file_bytes=None, file_name=None):
    if file_bytes:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendDocument"
        files = {'document': (file_name, file_bytes)}
        data = {'chat_id': CHAT_ID_MANAGER, 'caption': caption}
        return requests.post(url, files=files, data=data)
    else:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        data = {'chat_id': CHAT_ID_MANAGER, 'text': caption}
        return requests.post(url, data=data)

def create_advanced_pdf(name, count, rank, logo_l_path=None, logo_r_path=None):
    pdf = FPDF(orientation='L', unit='mm', format='A4')
    pdf.add_page()
    
    # Halluuwwan
    colors = {1: (255, 215, 0), 2: (192, 192, 192), 3: (205, 127, 50)}
    rank_color = colors.get(rank, (0, 80, 0))
    rank_txt = f"{rank}FFAA"

    # Border
    pdf.set_draw_color(27, 94, 32) # Dark Green
    pdf.set_line_width(2)
    pdf.rect(5, 5, 287, 200)
    
    # Logos
    if logo_l_path: pdf.image(logo_l_path, 15, 15, 30)
    if logo_r_path: pdf.image(logo_r_path, 250, 15, 30)

    # Content
    pdf.set_y(50)
    pdf.set_font("Arial", 'B', 30)
    pdf.set_text_color(*rank_color)
    pdf.cell(0, 20, "SARTIIFIKETA BEEKAMTII", ln=True, align='C')
    
    pdf.set_font("Arial", 'B', 20)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 10, "Waajjira Lafaa Bulchiinsa Magaalaa Dadar", ln=True, align='C')
    
    pdf.ln(20)
    pdf.set_font("Arial", 'I', 18)
    pdf.cell(0, 10, f"Badhaasa Sadarkaa {rank_txt}", ln=True, align='C')
    
    pdf.set_font("Arial", 'B', 25)
    pdf.cell(0, 20, f"Obbo/Adde: {name}", ln=True, align='C')
    
    pdf.set_font("Arial", '', 14)
    msg = f"Tajaajilamtoota {count} saffisaa fi qulqullinaan tajaajiluun gumaacha guddaa waan gumaachaniif badhaasa kanaan galateeffamaniiru."
    pdf.multi_cell(0, 10, msg, align='C')
    
    return pdf.output(dest='S').encode('latin-1')

# ================= 3. MAIN APP =================
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    _, col_mid, _ = st.columns([1, 1.2, 1])
    with col_mid:
        st.markdown("<h2 style='text-align:center; color: #1b5e20;'>Dadar Land Admin System</h2>", unsafe_allow_html=True)
        with st.form("login_form"):
            u = st.text_input("Username")
            p = st.text_input("Password", type="password")
            if st.form_submit_button("Seeni"):
                if u == "DAD" and p == "2026":
                    st.session_state.logged_in = True
                    st.rerun()
                else: st.error("Dogoggora!")
else:
    df = load_data()
    with st.sidebar:
        st.title("Dadar Land")
        menu = st.radio("FILANNOO", ["📊 Dashboard", "📝 Galmee Haaraa", "📈 Gabaasa Bal'aa", "🏆 Badhaasa Ogeeyyii", "🔍 Barbaadi/Edit"])
        if st.button("Log Out"):
            st.session_state.logged_in = False
            st.rerun()

    # --- DASHBOARD ---
    if menu == "📊 Dashboard":
        st.header("📊 Dashboard")
        c1, c2, c3 = st.columns(3)
        with c1: st.markdown(f"<div class='card'><h4>💰 Galii</h4><h2>{df['Kafaltii_Taj'].sum():,.2f}</h2><p>ETB</p></div>", unsafe_allow_html=True)
        with c2: st.markdown(f"<div class='card'><h4>👥 Maamiltoota</h4><h2>{len(df)}</h2><p>Waliigala</p></div>", unsafe_allow_html=True)
        with c3: st.markdown(f"<div class='card'><h4>👷 Ogeeyyii</h4><h2>{df['Maqaa_Ogeessa'].nunique()}</h2><p>Aktiiwii</p></div>", unsafe_allow_html=True)

    # --- REGISTRATION ---
    elif menu == "📝 Galmee Haaraa":
        st.header("📝 Galmee Tajaajilaa")
        GATII_DICT = {
            "Gibira": ["Gibira Baaxii Gooroo", "Gibira Lafa Qonnaa"],
            "Liizii": ["Liizii Waggaa", "Jijjiirraa Maqaa", "Kafaltii Liizii Duraa", "TOT"],
            "Ittii Fayyaddam": ["Hayyama Itti Fayyadama Lafaa", "Humna Mahandiisaa"],
            "Kaartaa": ["Kaartaa Lafa", "Kaartaa Kadastaara", "Kaartaa Lafa Qonnaa"]
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
            m_name = c1.text_input("Maqaa Abbaa Dhimmaa")
            ara = c2.text_input("Araddaa")
            qax = c1.text_input("Qaxana")
            ogeessa = c2.text_input("Maqaa Ogeessaa")
            
            if st.form_submit_button("💾 Galmeessi"):
                if m_name and ogeessa:
                    new_row = [datetime.now().strftime('%d/%m/%Y'), m_name, ara, qax, ", ".join(details), ogeessa, sum(d_fees.values())]
                    new_df = pd.DataFrame([new_row], columns=COL_NAMES)
                    df = pd.concat([df, new_df], ignore_index=True)
                    save_data(df)
                    st.success("Galmeeffameera!")
                    
                    # Telegram Notification
                    msg = f"✅ Galmee Haaraa:\nMaqaa: {m_name}\nKaffaltii: {sum(d_fees.values()):,.2f} ETB"
                    send_to_telegram(msg)
                    st.rerun()

    # --- GABAASA BAL'AA ---
    elif menu == "📈 Gabaasa Bal'aa":
        st.header("📈 Gabaasa Galii")
        if not df.empty:
            st.dataframe(df[COL_NAMES], use_container_width=True)
            
            # Export to Excel
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                df.to_excel(writer, index=False, sheet_name='Gabaasa')
            
            st.download_button("📥 Excel Buusi", output.getvalue(), "Gabaasa_Dadar.xlsx")
            
            if st.button("✈️ Gabaasa Telegramitti Ergi"):
                txt = f"📊 Gabaasa Waliigalaa:\nGalii: {df['Kafaltii_Taj'].sum():,.2f} ETB\nBaay'ina: {len(df)}"
                send_to_telegram(txt)
                st.success("Gabaasa ergameera!")
        else:
            st.warning("Data'n hin jiru.")

    # --- BADHAASA OGEEYYII ---
    elif menu == "🏆 Badhaasa Ogeeyyii":
        st.header("🏆 Sadarkaa Ogeeyyii")
        if not df.empty:
            top_3 = df['Maqaa_Ogeessa'].value_counts().head(3)
            cols = st.columns(3)
            for i, (name, count) in enumerate(top_3.items()):
                with cols[i]:
                    st.markdown(f"<div class='card'><h3>#{i+1}</h3><h4>{name}</h4><p>Hojii: {count}</p></div>", unsafe_allow_html=True)
                    pdf_bytes = create_advanced_pdf(name, count, i+1)
                    st.download_button(f"📥 Sartiifiketa {name}", pdf_bytes, f"Badhaasa_{name}.pdf", "application/pdf")
        else:
            st.info("Ogeeyyiin galmeeffaman hin jiran.")

    # --- SEARCH & EDIT ---
    elif menu == "🔍 Barbaadi/Edit":
        st.header("🔍 Barbaadi fi Sirreessi")
        q = st.text_input("Maqaa Barbaadi")
        if q and not df.empty:
            res = df[df['Maqaa_Abbaa_Dhimmaa'].str.contains(q, case=False, na=False)]
            for idx, row in res.iterrows():
                with st.expander(f"{row['Maqaa_Abbaa_Dhimmaa']}"):
                    new_n = st.text_input("Maqaa", row['Maqaa_Abbaa_Dhimmaa'], key=f"edit_n_{idx}")
                    new_k = st.number_input("Kafaltii", float(row['Kafaltii_Taj']), key=f"edit_k_{idx}")
                    if st.button("💾 Update", key=f"up_{idx}"):
                        df.at[idx, 'Maqaa_Abbaa_Dhimmaa'] = new_n
                        df.at[idx, 'Kafaltii_Taj'] = new_k
                        save_data(df)
                        st.success("Sirreeffameera!")
                        st.rerun()
                    if st.button("🗑 Haqi", key=f"del_{idx}"):
                        df = df.drop(idx)
                        save_data(df)
                        st.rerun()
