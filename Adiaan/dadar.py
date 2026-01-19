import streamlit as st
import pandas as pd
import os
import io
from datetime import datetime
from fpdf import FPDF
import plotly.express as px

# ================= 1. CONFIGURATION & DIRECTORIES =================
DATA_FILE = "dadar_final_report.txt"
BACKUP_DIR = "backups"
NAGAHEE_DIR = "nagahee_scan"

for folder in [BACKUP_DIR, NAGAHEE_DIR]:
    if not os.path.exists(folder): os.makedirs(folder)

st.set_page_config(page_title="Dadar Land Admin", page_icon="🏢", layout="wide")

# Custom CSS for Modern UI
st.markdown("""
    <style>
    /* Global Background */
    .stApp { background-color: #f8fafc; }
    
    /* Login & Form Cards */
    div.stForm { 
        background-color: white; 
        border-radius: 15px; 
        padding: 30px; 
        box-shadow: 0 10px 25px rgba(0,0,0,0.05); 
        border: none;
    }
    
    /* Metrics Styling */
    [data-testid="stMetricValue"] { color: #065f46; font-size: 28px; font-weight: bold; }
    
    /* Sidebar Styling */
    .css-1647y6u { background-color: #1e293b; }
    
    /* Professional Cards */
    .card {
        background: white;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        text-align: center;
        border-left: 5px solid #10b981;
        margin-bottom: 20px;
    }
    
    /* Hide Default Headers */
    #MainMenu, footer, header {visibility: hidden;}
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
# ================= 2. CORE LOGIC =================
COL_NAMES = ['Guyyaa', 'Maqaa_Abbaa_Dhimmaa', 'Araddaa', 'Qaxana', 'Gosa_Tajajjilaa', 'Maqaa_Ogeessa', 'Kafaltii_Taj']

def load_data():
    if not os.path.exists(DATA_FILE) or os.stat(DATA_FILE).st_size == 0:
        return pd.DataFrame(columns=COL_NAMES)
    df = pd.read_csv(DATA_FILE, sep="|", names=COL_NAMES, header=None, encoding='utf-8')
    df['Kafaltii_Taj'] = pd.to_numeric(df['Kafaltii_Taj'], errors='coerce').fillna(0)
    return df

def save_data(df_to_save):
    df_to_save[COL_NAMES].to_csv(DATA_FILE, sep="|", index=False, header=False, encoding="utf-8")
    ts = datetime.now().strftime('%Y%m%d_%H%M%S')
    df_to_save[COL_NAMES].to_csv(f"{BACKUP_DIR}/backup_{ts}.txt", sep="|", index=False, header=False)

# --- PDF GENERATOR (High Quality) ---
def generate_pro_pdf(type, name, data_row, logo_file=None):
    pdf = FPDF(orientation='P', unit='mm', format='A4')
    pdf.add_page()
    
    # Elegant Double Border
    pdf.set_draw_color(16, 185, 129); pdf.set_line_width(0.8)
    pdf.rect(10, 10, 190, 277)
    pdf.set_draw_color(30, 41, 59); pdf.set_line_width(0.2)
    pdf.rect(12, 12, 186, 273)

    if logo_file:
        with open("temp_logo.png", "wb") as f: f.write(logo_file.getbuffer())
        pdf.image("temp_logo.png", 90, 15, 30)

    pdf.set_y(50)
    pdf.set_font('Arial', 'B', 16); pdf.cell(0, 8, "BULCHIINSA MAGAALAA DADAR", 0, 1, 'C')
    pdf.set_font('Arial', '', 12); pdf.cell(0, 8, "WAJJIRA LAFA FI MANAA", 0, 1, 'C')
    
    pdf.ln(10)
    pdf.set_font('Arial', 'B', 14); pdf.set_text_color(16, 185, 129)
    title = "WARAQAA RAGAA QULQULLUMMAA" if type == "Clearance" else "SARTIIFIKEETA BEEKAMTII"
    pdf.cell(0, 10, title, "B", 1, 'C')
    
    pdf.set_text_color(0, 0, 0); pdf.ln(15)
    pdf.set_font('Arial', '', 12)
    
    if type == "Clearance":
        content = (f"Obbo/Adde {name}, Araddaa {data_row['Araddaa']} keessatti kan argaman "
                   f"tajaajila '{data_row['Gosa_Tajajjilaa']}' ilaalchisee kaffaltii irraa barbaadamu "
                   f"Birrii {data_row['Kafaltii_Taj']:,.2f} guutummaatti kaffalanii galmeessisanii jiru. "
                   f"\n\nKanaafuu, dhimmi isaanii raawwatamee waan jiruuf waraqaan qulqullummaa kun akka kennamuuf ta'eera.")
    else:
        content = (f"Ogeessi Maqaan isaa/ishee {name} jedhamu, waggaa 2026 keessatti "
                   f"maamiltoota baay'ee tajaajiluun beekamtii ol-aanaa argataniiru.")

    pdf.multi_cell(0, 10, content, align='L')
    
    # Signature Section
    pdf.set_y(240)
    pdf.set_font('Arial', 'B', 10)
    pdf.cell(90, 10, "Mallattoo Ogeessaa", 0, 0, 'L')
    pdf.cell(90, 10, "Mallattoo Itti Gaafatamaa", 0, 1, 'R')
    pdf.line(10, 260, 60, 260); pdf.line(140, 260, 190, 260)
    
    return pdf.output(dest='S').encode('latin-1', 'replace')

# ================= 3. APP INTERFACE =================
if 'logged_in' not in st.session_state: st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.markdown("<br><br>", unsafe_allow_html=True)
    col_l, col_m, col_r = st.columns([1,2,1])
    with col_m:
        st.markdown("<h2 style='text-align: center; color: #1e293b;'>🏢 Dadar Land System</h2>", unsafe_allow_html=True)
        with st.form("Login"):
            u = st.text_input("Username")
            p = st.text_input("Password", type="password")
            if st.form_submit_button("SEENI", use_container_width=True):
                if u == "DAD" and p == "2026":
                    st.session_state.logged_in, st.session_state.role = True, "admin"
                    st.rerun()
                elif u == "ogeessa" and p == "1234":
                    st.session_state.logged_in, st.session_state.role = True, "user"
                    st.rerun()
                else: st.error("Maaloo odeeffannoo sirrii galchi!")
else:
    df = load_data()
    
    # Sidebar
    with st.sidebar:
        st.markdown("<h2 style='color: white;'>Dadar Land</h2>", unsafe_allow_html=True)
        st.write(f"Logged in as: **{st.session_state.role.upper()}**")
        st.divider()
        menu = st.radio("MENU", ["📊 Dashboard", "📝 Galmee Haaraa", "🏆 Badhaasa", "🔍 Barbaadi & Clearance"])
        if st.button("Logout", use_container_width=True):
            st.session_state.logged_in = False
            st.rerun()

    # --- DASHBOARD ---
    if menu == "📊 Dashboard":
        st.title("📊 Dashboard Gabaasaa")
        if not df.empty:
            # Metrics
            c1, c2, c3 = st.columns(3)
            c1.metric("Waliigala Galii", f"{df['Kafaltii_Taj'].sum():,.2f} ETB")
            c2.metric("Maamiltoota", f"{len(df)}")
            c3.metric("Ogeeyyii", f"{df['Maqaa_Ogeessa'].nunique()}")
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            # Charts
            col_chart1, col_chart2 = st.columns(2)
            with col_chart1:
                fig1 = px.pie(df, values='Kafaltii_Taj', names='Araddaa', hole=0.5, title="Galii Araddaadhaan", color_discrete_sequence=px.colors.sequential.Emerald)
                st.plotly_chart(fig1, use_container_width=True)
            with col_chart2:
                fig2 = px.bar(df, x='Maqaa_Ogeessa', y='Kafaltii_Taj', color='Gosa_Tajajjilaa', title="Raawwii Ogeeyyii")
                st.plotly_chart(fig2, use_container_width=True)
            
            # Download Data
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Gabaasa Guutuu (CSV) Buufadhu", csv, "Gabaasa_Dadar.csv", "text/csv")

    # --- REGISTRATION ---
    elif menu == "📝 Galmee Haaraa":
        st.title("📝 Galmee Tajaajilaa Haaraa")
        with st.form("RegForm"):
            c1, c2 = st.columns(2)
            name = c1.text_input("Maqaa Abbaa Dhimmaa")
            ara = c1.text_input("Araddaa")
            gosa = c2.selectbox("Gosa Tajaajilaa", ["Jijjiirraa Maqaa (Sale)", "Kaartaa Haaraa", "Waraqaa Qulqullummaa", "TOT 2%", "Adabbii"])
            fee = c2.number_input("Kaffaltii (ETB)", min_value=0.0)
            og = c1.text_input("Maqaa Ogeessaa")
            
            if st.form_submit_button("💾 GALMEESSI"):
                if name and og:
                    # Auto-calculate TOT if selected
                    final_fee = fee * 0.02 if "TOT" in gosa else fee
                    new_row = [datetime.now().strftime('%d/%m/%Y'), name, ara, "-", gosa, og, final_fee]
                    df = pd.concat([df, pd.DataFrame([new_row], columns=COL_NAMES)], ignore_index=True)
                    save_data(df)
                    st.success(f"Milkaa'inaan Galmeeffameera! Kaffaltii: {final_fee:,.2f} ETB")

    # --- SEARCH & CLEARANCE ---
    elif menu == "🔍 Barbaadi & Clearance":
        st.title("🔍 Barbaadi fi Waraqaa Ragaa")
        search = st.text_input("Maqaa ykn Araddaa barreessi...")
        
        if search and not df.empty:
            results = df[df['Maqaa_Abbaa_Dhimmaa'].str.contains(search, case=False) | df['Araddaa'].str.contains(search, case=False)]
            
            if not results.empty:
                for idx, row in results.iterrows():
                    with st.container():
                        st.markdown(f"""
                            <div class="card">
                                <h4>{row['Maqaa_Abbaa_Dhimmaa']}</h4>
                                <p>Tajaajila: {row['Gosa_Tajajjilaa']} | Kaffaltii: {row['Kafaltii_Taj']} ETB</p>
                            </div>
                        """, unsafe_allow_html=True)
                        
                        # Generate Clearance
                        pdf_data = generate_pro_pdf("Clearance", row['Maqaa_Abbaa_Dhimmaa'], row)
                        st.download_button(f"📥 Download Clearance PDF", pdf_data, f"Clearance_{row['Maqaa_Abbaa_Dhimmaa']}.pdf", key=f"btn_{idx}")
                        
                        if st.session_state.role == "admin":
                            if st.button("🗑 Haqi", key=f"del_{idx}"):
                                df = df.drop(idx); save_data(df); st.rerun()
            else:
                st.warning("Ragaan wal-fakkaatu hin argamne.")

    # --- AWARDS ---
    elif menu == "🏆 Badhaasa":
        st.title("🏆 Beekamtii Ogeeyyii")
        logo_up = st.file_uploader("Logo Wajjiraa Upload (PDF irratti akka mul'atuuf)", type=['png', 'jpg'])
        
        if not df.empty:
            top_3 = df['Maqaa_Ogeessa'].value_counts().head(3)
            cols = st.columns(3)
            for i, (og_name, count) in enumerate(top_3.items()):
                with cols[i]:
                    st.markdown(f"<div class='card'><h2># {i+1}</h2><h3>{og_name}</h3><p>Tajaajila: {count}</p></div>", unsafe_allow_html=True)
                    cert = generate_pro_pdf("Cert", og_name, {}, logo_up)
                    st.download_button(f"📥 Download Certificate", cert, f"Cert_{og_name}.pdf")

