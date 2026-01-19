import streamlit as st
import pandas as pd
import os
import io
import random
from datetime import datetime
from fpdf import FPDF
import plotly.express as px

# ================= 1. CONFIGURATION & STYLE =================
DATA_FILE = "dadar_final_report.txt"
NAGAHEE_DIR = "nagahee_scan"

if not os.path.exists(NAGAHEE_DIR): os.makedirs(NAGAHEE_DIR)

st.set_page_config(page_title="Dadar Land Admin System", page_icon="🏢", layout="wide")

# CSS for Modern UI
st.markdown("""
    <style>
    .stApp { background: #f8f9fa; }
    div.stForm { background: white; border-radius: 15px; padding: 30px; border: 1px solid #e0e0e0; }
    .card { 
        background: white; padding: 20px; border-radius: 12px; 
        box-shadow: 0 4px 6px rgba(0,0,0,0.1); text-align: center; 
        border-top: 6px solid #006400; margin-bottom: 20px;
    }
    .stMetric { background: white; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    </style>
""", unsafe_allow_html=True)

# ================= 2. CORE FUNCTIONS =================
# Maqaa kutaalee ragaa (Columns) - Qaxana bakka 'Token' itti fayyadamna
COL_NAMES = ['Guyyaa', 'Maqaa_Abbaa_Dhimmaa', 'Araddaa', 'Token', 'Gosa_Tajajjilaa', 'Maqaa_Ogeessa', 'Kafaltii_Taj']

def load_data():
    if not os.path.exists(DATA_FILE) or os.stat(DATA_FILE).st_size == 0:
        return pd.DataFrame(columns=COL_NAMES)
    df = pd.read_csv(DATA_FILE, sep="|", names=COL_NAMES, header=None, encoding='utf-8')
    df['Kafaltii_Taj'] = pd.to_numeric(df['Kafaltii_Taj'], errors='coerce').fillna(0)
    return df

def save_data(df_to_save):
    df_to_save[COL_NAMES].to_csv(DATA_FILE, sep="|", index=False, header=False, encoding="utf-8")

def generate_token():
    return f"DAD-{random.randint(1000, 9999)}"

# PDF Generator for Clearance & Certificates
def generate_pro_pdf(type, name, row_data):
    pdf = FPDF(orientation='P' if type == "Clearance" else 'L', unit='mm', format='A4')
    pdf.add_page()
    
    # Border
    pdf.set_draw_color(0, 80, 0); pdf.set_line_width(1.2)
    pdf.rect(10, 10, 190 if type == "Clearance" else 277, 277 if type == "Clearance" else 190)
    
    # Header
    pdf.set_y(25)
    pdf.set_font('Arial', 'B', 16); pdf.cell(0, 8, "BULCHIINSA MAGAALAA DADAR", 0, 1, 'C')
    pdf.set_font('Arial', 'B', 13); pdf.cell(0, 8, "WAJJIRA LAFA FI MANAA", 0, 1, 'C')
    
    # Token Number at top right
    pdf.set_y(15); pdf.set_x(-60)
    pdf.set_font('Arial', 'B', 10); pdf.cell(40, 8, f"TOKEN: {row_data.get('Token', 'N/A')}", 0, 1, 'R')
    
    pdf.ln(15)
    pdf.set_text_color(180, 0, 0); pdf.set_font('Arial', 'B', 15)
    title = "WARAQAA RAGAA QULQULLUMMAA" if type == "Clearance" else "SARTIIFIKEETA BEEKAMTII"
    pdf.cell(0, 10, title, "B", 1, 'C')
    
    pdf.set_text_color(0, 0, 0); pdf.ln(10); pdf.set_font('Arial', '', 12)
    
    if type == "Clearance":
        content = (
            f"Obbo/Adde {name}, jiraataa Magaalaa Dadar, Araddaa {row_data['Araddaa']} kan ta'an, "
            f"tajaajila '{row_data['Gosa_Tajajjilaa']}' wajjira keenya irraa gaafatanii turan. "
            f"\n\nHaaluma kanaan, kaffaltii tajaajila kanaaf barbaadamu waliigala Birrii {row_data['Kafaltii_Taj']:,.2f} "
            f"guyyaa {row_data['Guyyaa']} kaffalanii galmeessisaniiru. "
            f"\n\nLakkoofsi Token galmee kanaa {row_data.get('Token', 'N/A')} yoo ta'u, "
            f"maamilli kun herrega mootummaa irraa qulqulluu ta'uun isaanii mirkanaa'eera."
        )
    else:
        content = f"Sartiifiikeetni beekamtii kun Ogeessa {name} jedhamuuf waggaa 2026 keessa tajaajila ol-aanaa waan kennaniif kenname."

    pdf.multi_cell(0, 10, content, align='L')
    
    # Signature Lines
    pdf.set_y(-50)
    pdf.cell(90, 10, "Mallattoo Ogeessaa: __________", 0, 0, 'C')
    pdf.cell(90, 10, "Mallattoo Itti Gaafatamaa: __________", 0, 1, 'C')
    
    return pdf.output(dest='S').encode('latin-1', 'replace')

# ================= 3. APP NAVIGATION =================
if 'logged_in' not in st.session_state: st.session_state.logged_in = False

if not st.session_state.logged_in:
    # --- LOGIN PAGE ---
    col_l, col_m, col_r = st.columns([1, 2, 1])
    with col_m:
        st.markdown("<h2 style='text-align: center;'>🔐 Dadar Land Login</h2>", unsafe_allow_html=True)
        with st.form("Login"):
            u = st.text_input("Username")
            p = st.text_input("Password", type="password")
            if st.form_submit_button("SEENI", use_container_width=True):
                if u == "DAD" and p == "2026":
                    st.session_state.logged_in = True
                    st.rerun()
                else: st.error("Username ykn Password dogoggora!")
else:
    df = load_data()
    
    # --- SIDEBAR MENU ---
    with st.sidebar:
        st.markdown("<h2 style='color: #006400;'>🏢 Dadar Admin</h2>", unsafe_allow_html=True)
        st.divider()
        menu = st.radio("FILANNOO:", 
                        ["🏠 Dashboard", "📝 Galmee Haaraa", "🔍 Barbaadi & Haqi", "🏆 Badhaasa", "🚪 Logout"])
        st.divider()
        st.write("System Year: 2026")

    # --- 1. DASHBOARD ---
    if menu == "🏠 Dashboard":
        st.title("📊 Gabaasa Waliigalaa")
        if not df.empty:
            c1, c2, c3 = st.columns(3)
            c1.metric("💰 Galii Waliigalaa", f"{df['Kafaltii_Taj'].sum():,.2f} ETB")
            c2.metric("👥 Maamiltoota", len(df))
            c3.metric("👷 Ogeeyyii", df['Maqaa_Ogeessa'].nunique())
            
            st.plotly_chart(px.pie(df, values='Kafaltii_Taj', names='Araddaa', hole=0.4, title="Galii Araddaadhaan"), use_container_width=True)
            
            # Export to Excel
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                df.to_excel(writer, index=False)
            st.download_button("📥 Gabaasa Excel Buufadhu", buffer.getvalue(), "Gabaasa_Dadar_2026.xlsx")

    # --- 2. REGISTRATION (GALMEE) ---
    elif menu == "📝 Galmee Haaraa":
        st.title("📝 Galmee Tajaajilaa Haaraa")
        token_id = generate_token()
        st.info(f"Lakkoofsa Token Maamila Ammaa: **{token_id}**")
        
        with st.form("reg_form"):
            c1, c2 = st.columns(2)
            name = c1.text_input("Maqaa Abbaa Dhimmaa")
            ara = c2.text_input("Araddaa")
            gosa = st.selectbox("Gosa Tajaajilaa", ["Jijjiirraa Maqaa", "Kaartaa Haaraa", "Waraqaa Qulqullummaa", "TOT 2%", "Adabbii"])
            fee = st.number_input("Kaffaltii (ETB)", min_value=0.0)
            ogeessa = st.text_input("Ogeessa Raawwate")
            
            if st.form_submit_button("💾 GALMEESSI", use_container_width=True):
                if name and ogeessa:
                    new_row = [datetime.now().strftime('%d/%m/%Y'), name, ara, token_id, gosa, ogeessa, fee]
                    df = pd.concat([df, pd.DataFrame([new_row], columns=COL_NAMES)], ignore_index=True)
                    save_data(df)
                    st.success(f"Milkaa'inaan Galmeeffameera! Token: {token_id}")
                else: st.warning("Maaloo maqaafi ogeessa galchi.")

    # --- 3. SEARCH, CLEARANCE & DELETE ---
    elif menu == "🔍 Barbaadi & Haqi":
        st.title("🔍 Barbaadi fi Waraqaa Qulqullummaa")
        q = st.text_input("Maqaa ykn Token galchi...")
        
        if q and not df.empty:
            res = df[df['Maqaa_Abbaa_Dhimmaa'].str.contains(q, case=False, na=False) | df['Token'].str.contains(q, case=False, na=False)]
            
            if not res.empty:
                for idx, row in res.iterrows():
                    with st.expander(f"👤 {row['Maqaa_Abbaa_Dhimmaa']} | Token: {row['Token']}"):
                        col_a, col_b = st.columns([2, 1])
                        with col_a:
                            st.write(f"**Gosa Tajaajilaa:** {row['Gosa_Tajajjilaa']}")
                            st.write(f"**Kaffaltii:** {row['Kafaltii_Taj']:,.2f} ETB")
                            st.write(f"**Guyyaa:** {row['Guyyaa']}")
                        with col_b:
                            # Clearance Download
                            pdf_file = generate_pro_pdf("Clearance", row['Maqaa_Abbaa_Dhimmaa'], row)
                            st.download_button(f"📥 Clearance (PDF)", pdf_file, f"Clearance_{row['Token']}.pdf", key=f"clr_{idx}")
                            
                            # Delete Record
                            if st.button(f"🗑 Haqi", key=f"del_{idx}"):
                                df = df.drop(idx)
                                save_data(df)
                                st.success("Galmeen haqameera!")
                                st.rerun()
            else: st.warning("Ragaan hin argamne.")

    # --- 4. AWARDS ---
    elif menu == "🏆 Badhaasa":
        st.title("🏆 Sartiifiikeeta Beekamtii Ogeeyyii")
        if not df.empty:
            top_og = df['Maqaa_Ogeessa'].value_counts().head(3)
            cols = st.columns(3)
            for i, (name, count) in enumerate(top_og.items()):
                with cols[i]:
                    st.markdown(f"<div class='card'><h2># {i+1}</h2><h3>{name}</h3><p>Tajaajila: {count}</p></div>", unsafe_allow_html=True)
                    cert = generate_pro_pdf("Cert", name, {"Token": "AWARD-2026"})
                    st.download_button(f"📥 Download Cert", cert, f"Cert_{name}.pdf", key=f"crt_{i}")

    # --- 5. LOGOUT ---
    elif menu == "🚪 Logout":
        st.session_state.logged_in = False
        st.rerun()
