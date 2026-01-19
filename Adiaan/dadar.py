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


if not os.path.exists(NAGAHEE_DIR):
    os.makedirs(NAGAHEE_DIR)

st.set_page_config(
    page_title=" Dadar Land Administration Customer Registration System ", 
    page_icon="🏢", 
    layout="wide"
)

# Halluu fi Style
st.markdown("""
    <style>
    .stApp { background: #f4f7f9; }
    div.stForm { background: white; border-radius: 12px; padding: 20px; border: 1px solid #ddd; }
    .card { background: white; padding: 15px; border-radius: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); text-align: center; }
    </style>
    """, unsafe_allow_html=True)

# ================= 2. SERVICE LIST (GOSA TAJAAJILAA) =================
# Gosa tajaajilaa hunda akka gosa gurguddaatti addaan baasuu
SERVICE_STRUCTURE = {
    "🏷 Gibira & Kaffaltii": [
        "Gibira Baaxii Gooroo", "Gibira Lafa Qonnaa", "Kaffaltii Liizii Waggaa", 
        "Kaffaltii Liizii Duraa", "TOT (Turnover Tax)", "Kaffaltii Jijjiirraa Maqaa (Gift/Sale)"
    ],
    "📜 Kaartaa & Qabiyyee": [
        "Kaartaa Haaraa", "Kaartaa Bakka Bu'aa", "Kaartaa Kadastaaraa", 
        "Jijjiirraa Maqaa (Gift/Sale)", "Sirreeffama Daangaa", "Kaartaa Lafa Qoonnaa"
    ],
    "🏗 Pilaanii & Ijaarsa": [
      "Pilaanii Magaalaa", "Itti Fayyadama Lafaa (Land Use)", 
       "Humna Mahandisummaa"
    ],
    "⚖️ Dhimma Seeraa": [
        "Ugura Mana Murtii", "Ugura Kaasuu", "Waliigaltee Liqii Baankii", 
        "Waliigaltee Hiikuu", "Dhimma Dhala (Inheritance)"
    ],
    "📂 Tajaajila Biroo": [
        "Waraqaa Ragaa (Clearance)", "Deebii Iyyannoo)"
    ],
    "⚖️ Adabbii & Seeressuu": [
        "Adabbii Ijaarsa Seeraan Alaa",
        "Kaffaltii Seeressuu (Regularization)",
        "Adabbii Faallaa Pilaanii"
    ],
}
COL_NAMES = ['Guyyaa', 'Maqaa_Abbaa_Dhimmaa', 'Araddaa', 'Qaxana', 'Gosa_Tajajjilaa', 'Maqaa_Ogeessa', 'Kafaltii_Taj']

# ================= 3. CORE FUNCTIONS =================
def load_data():
    if not os.path.exists(DATA_FILE) or os.stat(DATA_FILE).st_size == 0:
        return pd.DataFrame(columns=COL_NAMES)
    return pd.read_csv(DATA_FILE, sep="|", names=COL_NAMES, header=None, encoding='utf-8')

def save_data(df_to_save):
    df_to_save[COL_NAMES].to_csv(DATA_FILE, sep="|", index=False, header=False, encoding="utf-8")

def create_certificate(name, count, rank, l_l, l_r, sig):
    pdf = FPDF(orientation='L', unit='mm', format='A4')
    pdf.add_page()
    
    # Border
    pdf.set_draw_color(0, 100, 0); pdf.set_line_width(2); pdf.rect(10, 10, 277, 190)
    
    # Logo
    if l_l: 
        with open("tmp_l.png", "wb") as f: f.write(l_l.getbuffer())
        pdf.image("tmp_l.png", 20, 15, 30)
    
    pdf.set_y(50); pdf.set_font('Arial', 'B', 30); pdf.cell(0, 10, "SARTIIFIKEETA BEEKAMTII", 0, 1, 'C')
    pdf.set_font('Arial', '', 20); pdf.cell(0, 20, f"Obbo/Adde: {name}", 0, 1, 'C')
    pdf.set_font('Arial', '', 14); pdf.multi_cell(0, 10, f"Waggaa 2026 keessatti maamiltoota {count} tajaajiluun sadarkaa {rank}ffaa argataniiru.", align='C')
    
    # Signature
    if sig:
        with open("tmp_sig.png", "wb") as f: f.write(sig.getbuffer())
        pdf.image("tmp_sig.png", 50, 160, 30)
    
    pdf.line(40, 180, 100, 180); pdf.set_xy(40, 182); pdf.cell(60, 10, "Itti Gaafatamaa", align='C')
    return pdf.output(dest='S').encode('latin-1', 'replace')

# ================= 4. MAIN NAVIGATION =================
if 'logged_in' not in st.session_state: st.session_state.logged_in = False


if not st.session_state.logged_in:
    # Login Section
    st.title("🔐 Dadar Land Admin Login")
    u = st.text_input("Username")
    p = st.text_input("Password", type="password")
    if st.button("Seeni"):
        if u == "DAD" and p == "2026": 
            st.session_state.logged_in = True
            st.rerun()
else:
    df = load_data()
    menu = st.sidebar.radio("FILANNOO", ["📊 Dashboard", "📝 Galmee Haaraa", "🏆 Badhaasa", "📈 Gabaasa"])

# --- REGISTRATION ---
    if menu == "📝 Galmee Haaraa":
       
        
        # Filannoo Tajaajilaa
        st.subheader("🟢 Gosa Tajaajilaa Filadhu")
        selected_cats = st.multiselect("Ramaddii Tajaajilaa:", list(SERVICE_STRUCTURE.keys()))
        
        final_services = []
        total_fee = 0
        
        if selected_cats:
            cols = st.columns(len(selected_cats))
            for i, cat in enumerate(selected_cats):
                with cols[i]:
                    st.write(f"{cat}")
                    subs = st.multiselect(f"Tajaajiloota {cat}:", SERVICE_STRUCTURE[cat], key=cat)
                    for s in subs:
                        fee = st.number_input(f"Kaffaltii {s}:", min_value=0.0, key=f"fee_{s}")
                        final_services.append(s)
                        total_fee += fee

        st.divider()
        
        with st.form("reg_form"):
            c1, c2 = st.columns(2)
            name = c1.text_input("Maqaa Abbaa Dhimmaa")
            ara = c2.text_input("Araddaa")
            qax = c1.text_input("Qaxana")
            ogeessa = c2.text_input("Ogeessa Raawwate")
            
            # Nagahee Upload
            nagahee = st.file_uploader("Nagahee Scan (Image)", type=['jpg','png','jpeg'])
            
            if st.form_submit_button("💾 Galmeessi"):
                if name and final_services:
                    # Save Image
                    if nagahee:
                        f_path = os.path.join(NAGAHEE_DIR, f"{name}_{datetime.now().strftime('%H%M%S')}.jpg")
                        with open(f_path, "wb") as f: f.write(nagahee.getbuffer())
                    
                    # Save Data
                    new_row = [datetime.now().strftime('%d/%m/%Y'), name, ara, qax, ", ".join(final_services), ogeessa, total_fee]
                    df = pd.concat([df, pd.DataFrame([new_row], columns=COL_NAMES)], ignore_index=True)
                    save_data(df)
                    st.success(f"✅ Galmeeffameera! Waliigala: {total_fee} ETB")
                else:
                    st.error("Maaloo odeeffannoo guutuu galchi!")

     # --- 1. DASHBOARD ---
    if menu == "📊 Dashboard":
        st.header("📊 Dashboard Herregaa fi Gali")
        if not df.empty:
            df_tot = df[df['Gosa_Tajajjilaa'].str.contains('TOT', case=False, na=False)]
            c1, c2, c3 = st.columns(3)
            c1.metric("💰 Waliigala Galii", f"{df['Kafaltii_Taj'].sum():,.2f} ETB")
            c2.metric("📈 Galii TOT (2%)", f"{df_tot['Kafaltii_Taj'].sum():,.2f} ETB")
            c3.metric("👥 Maamiltoota", len(df))
            
            st.plotly_chart(px.pie(df, values='Kafaltii_Taj', names='Araddaa', hole=0.4, title="Galii Araddaa dhaan"), use_container_width=True)
            
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                df.to_excel(writer, index=False)
            st.download_button("📥 Excel Download", output.getvalue(), "Gabaasa_Full.xlsx")

if menu == "📈 Gabaasa Bal'aa":
        st.header("📈 Gabaasa & Calaltuu")
        if not df.empty:
            with st.sidebar:
                st.markdown("---")
                f_type = st.radio("Filtarii:", ["Waggaa", "Kurmaana", "Ji'a", "Torbee", "Guyyaa"])
                sel_y = st.selectbox("Waggaa", sorted(df['Waggaa'].dropna().unique(), reverse=True))
                filtered = df[df['Waggaa'] == sel_y]
                if f_type == "Kurmaana": filtered = filtered[filtered['Kurmaana'] == st.selectbox("Q", [1,2,3,4])]
                elif f_type == "Ji'a": filtered = filtered[filtered['Ji\'a'] == st.selectbox("Ji'a", MONTH_ORDER)]
                elif f_type == "Torbee":
                    sel_m, sel_w = st.selectbox("Ji'a", MONTH_ORDER), st.selectbox("Torbee", [1,2,3,4])
                    filtered = filtered[(filtered['Ji\'a'] == sel_m) & (filtered['Torbee'] == sel_w)]
                elif f_type == "Guyyaa": filtered = filtered[filtered['Guyyaa_Torbee'] == st.selectbox("Guyyaa", list(WEEKDAY_MAP.values()))]

            st.dataframe(filtered[COL_NAMES], use_container_width=True)
            st.metric("Galii Filtarii", f"{filtered['Kafaltii_Taj'].sum():,.2f} ETB")

  # --- BADHAASA OGEEYYII (PDF) ---
elif menu == "🏆 Badhaasa Ogeeyyii":
    st.header("🏆 Sartiifiikeeta Ogeeyyii Cimaa")

    if not df.empty:
        top_3 = df['Maqaa_Ogeessa'].value_counts().head(3)
        medals = ["🥇 1FFAA", "🥈 2FFAA", "🥉 3FFAA"]

        # Upload both logos once
        with st.form("logo_upload_form"):
            logo_bita = st.file_uploader("Upload Logo Bita (Left)", type=["png","jpg","jpeg"])
            logo_mirga = st.file_uploader("Upload Logo Mirga (Right)", type=["png","jpg","jpeg"])
            submit_logos = st.form_submit_button("✅ Upload Logos")

        if submit_logos:
            cols = st.columns(3)

            for i, (name, count) in enumerate(top_3.items()):
                with cols[i]:
                    # Card display
                    st.markdown(
                        f"<div class='card'><h2>{medals[i]}</h2>"
                        f"<h3>{name}</h3>"
                        f"<p>Abbootii Dhimmaa: {count}</p></div>", 
                        unsafe_allow_html=True
                    )

                    # Generate PDF certificate
                    pdf_bytes = create_pdf_cert(
                        name=name,
                        count=count,
                        rank=i+1,
                        logo_left=logo_bita,
                        logo_right=logo_mirga
                    )

                    # Dynamic filename
                    safe_name = name.replace(" ", "_")
                    medal_icon = ["1FFAA", "2FFAA", "3FFAA"][i]
                    file_name = f"Certificate_{medal_icon}_{safe_name}.pdf"

                    # Individual download button
                    st.download_button(
                        f"📥 Download {name} PDF",
                        pdf_bytes,
                        file_name,
                        mime="application/pdf"
                    )
    else:
        st.warning("Data'n hin jiru.")

# --- 5. SEARCH / EDIT ---
elif menu == "🔍 Barbaadi/Edit":
    st.header("🔍 Barbaadi / Edit Galmee")
    q = st.text_input("Maqaa Barbaadi...")

    if q:
        res = df[df['Maqaa_Abbaa_Dhimmaa'].str.contains(q, case=False, na=False)]
        if res.empty:
            st.info("Ragaan hin argamne.")
        else:
            for idx, row in res.iterrows():
                with st.expander(f"📄 {row['Maqaa_Abbaa_Dhimmaa']}"):
                    st.write(f"Araddaa: {row['Araddaa']}")
                    st.write(f"Qaxana: {row['Qaxana']}")
                    st.write(f"Tajaajila: {row['Gosa_Tajajjilaa']}")
                    st.write(f"Ogeessa: {row['Maqaa_Ogeessa']}")
                    st.write(f"Kafaltii: {row['Kafaltii_Taj']}")
                    
                    # Delete confirmation
                    if st.button("🗑 Haqi", key=f"del_{idx}"):
                        confirm = st.checkbox(f"Dhugaa haquu barbaaddaa {row['Maqaa_Abbaa_Dhimmaa']}?")
                        if confirm:
                            df = df.drop(idx)
                            save_data(df)
                            st.success(f"{row['Maqaa_Abbaa_Dhimmaa']} haqameera")
                            st.experimental_rerun()

# --- 6. LOGOUT ---
elif menu == "Ba'i":
    st.session_state.logged_in = False
    st.experimental_rerun()





# --- LOGIN LOGIC ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    # Fuula Login irratti logo agarsiisuuf
    if os.path.exists(LOGO_PATH):
        st.image(LOGO_PATH, width=120)
    
    st.title("W/Bulchiinsa Lafaa Magaalaa Dadar")
    with st.form("Login"):
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")
        if st.form_submit_button("Login"):
            if u == USER_NAME and p == PASS_WORD:
                st.session_state.logged_in = True
                st.rerun()
            else:
                st.error("Login Dogoggora!")
else:
    # --- SIDEBAR (Logo & Menu) ---
    if os.path.exists(LOGO_PATH):
        st.sidebar.image(LOGO_PATH, use_container_width=True)
    
    st.sidebar.title("Main Menu")
    menu = ["Galmee Haaraa", "Gabaasa Excel (Telegram)", "Barbaadi (Search)", "Logout"]
    choice = st.sidebar.selectbox("Filannoo", menu)

    # --- MAIN HEADER (Logo & Title) ---
    col1, col2 = st.columns([1, 5])
    with col1:
        if os.path.exists(LOGO_PATH):
            st.image(LOGO_PATH, width=80)
    with col2:
        st.title("W/Bulchiinsa Lafaa Magaalaa Dadar")







