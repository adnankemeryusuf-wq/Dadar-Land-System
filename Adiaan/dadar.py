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
DATA_FILE = "dadar_final_report.txt"
BOT_TOKEN = "8357193631:AAHCuSnXzjZTQaglkmcS0gq-EvqnkIQLDBI"
CHAT_ID_MANAGER = "7329587700"

st.set_page_config(
    page_title="Dadar Land Customer Registration System", 
    page_icon="🏢", 
    layout="wide"
)

COL_NAMES = ['Guyyaa', 'Maqaa_Abbaa_Dhimmaa', 'Araddaa', 'Qaxana', 'Gosa_Tajajjilaa', 'Maqaa_Ogeessa', 'Kafaltii_Taj']
MONTH_ORDER = ["Fulbaana", "Onkololeessa", "Sadaasa", "Muddee", "Amajjii", "Guraandhala", "Bitootessa", "Eebila", "Caamsaa", "Waxabajjii", "Adooleessa", "Hagayya"]
MONTH_MAP = {9: "Fulbaana", 10: "Onkololeessa", 11: "Sadaasa", 12: "Muddee", 1: "Amajjii", 2: "Guraandhala", 3: "Bitootessa", 4: "Eebila", 5: "Caamsaa", 6: "Waxabajjii", 7: "Adooleessa", 8: "Hagayya"}

# --- Bifa Bareedinaa (CSS) ---
st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #f1f8e9 0%, #ffffff 100%); }
    [data-testid="stSidebar"] { background-color: #1b5e20 !important; }
    [data-testid="stSidebar"] * { color: #ffffff !important; }
    div.stForm { background: white; border-radius: 15px; padding: 25px; border: 2px solid #2e7d32; box-shadow: 0px 4px 15px rgba(0,0,0,0.1); }
    .card { background: white; padding: 20px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); text-align: center; border-top: 5px solid #2e7d32; margin-bottom: 10px; }
    .stButton>button { background: linear-gradient(90deg, #4caf50, #2e7d32); color: white; border-radius: 8px; font-weight: bold; width: 100%; }
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
    df_to_save[COL_NAMES].to_csv(DATA_FILE, sep="|", index=False, header=False, encoding="utf-8")

def create_advanced_pdf(name, count, rank):
    pdf = FPDF(orientation='L', unit='mm', format='A4')
    pdf.add_page()
    
    ranks = {1: ((255, 215, 0), "1FFAA"), 2: ((192, 192, 192), "2FFAA"), 3: ((205, 127, 50), "3FFAA")}
    rank_color, rank_text = ranks.get(rank, ((0, 80, 0), "Beekamtii"))

    pdf.set_draw_color(0, 80, 0) # Green Border
    pdf.set_line_width(3.0)
    pdf.rect(10, 10, 277, 190)
    
    pdf.set_y(50)
    pdf.set_text_color(*rank_color)
    pdf.set_font('Arial', 'B', 35)
    pdf.cell(0, 15, "SARTIIFIKETA BEEKAMTII", ln=True, align='C')
    
    pdf.set_y(90)
    pdf.set_text_color(40, 40, 40)
    pdf.set_font('Arial', 'B', 30)
    pdf.cell(0, 20, f"Obbo/Adde: {name.upper()}", ln=True, align='C')
    
    return pdf.output(dest='S').encode('latin-1', 'replace')

# ================= 3. APP LOGIC =================
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    # --- LOGIN ---
    _, col_mid, _ = st.columns([1, 1.2, 1])
    with col_mid:
        st.markdown("<h2 style='text-align:center;'>🏢 Dadar Land System</h2>", unsafe_allow_html=True)
        with st.form("login_form"):
            u = st.text_input("Username")
            p = st.text_input("Password", type="password")
            if st.form_submit_button("Seeni"):
                if u == "DAD" and p == "2026":
                    st.session_state.logged_in = True
                    st.rerun()
                else: st.error("Maqaan ykn Koodiin dogoggora!")
else:
    df = load_data()
    # --- SIDEBAR ---
    with st.sidebar:
        st.success("Deder City Land Office")
        menu = st.radio("FILANNOO", ["📊 Dashboard", "📝 Galmee Haaraa", "📈 Gabaasa Bal'aa", "🏆 Badhaasa", "🔍 Barbaadi"])
        if st.button("Log Out"):
            st.session_state.logged_in = False
            st.rerun()

    # --- DASHBOARD ---
    if menu == "📊 Dashboard":
        st.title("📊 Dashboard Waliigalaa")
        c1, c2, c3 = st.columns(3)
        c1.markdown(f"<div class='card'><h4>💰 Galii</h4><h2>{df['Kafaltii_Taj'].sum():,.2f}</h2><p>ETB</p></div>", unsafe_allow_html=True)
        c2.markdown(f"<div class='card'><h4>👥 Maamiltoota</h4><h2>{len(df)}</h2><p>Waliigala</p></div>", unsafe_allow_html=True)
        c3.markdown(f"<div class='card'><h4>👷 Ogeeyyii</h4><h2>{df['Maqaa_Ogeessa'].nunique()}</h2><p>Aktiiwii</p></div>", unsafe_allow_html=True)
        
        if not df.empty:
            st.subheader("Xiinxala Galii")
            st.area_chart(df.groupby('Ji\'a')['Kafaltii_Taj'].sum().reindex(MONTH_ORDER).fillna(0))

    # --- REGISTRATION ---
    elif menu == "📝 Galmee Haaraa":
        st.header("📝 Galmee Tajaajilaa")
        with st.form("reg_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            name = col1.text_input("Maqaa Abbaa Dhimmaa")
            ara = col2.text_input("Araddaa")
            qax = col1.text_input("Qaxana")
            ogeessa = col2.text_input("Maqaa Ogeessaa")
            service = st.text_area("Gosa Tajaajilaa")
            fee = st.number_input("Kafaltii (ETB)", min_value=0.0)
            
            if st.form_submit_button("💾 Galmeessi"):
                if name and ogeessa:
                    new_row = [datetime.now().strftime('%d/%m/%Y'), name, ara, qax, service, ogeessa, fee]
                    df = pd.concat([df, pd.DataFrame([new_row], columns=COL_NAMES)], ignore_index=True)
                    save_data(df)
                    st.success("Galmeeffameera!")
                    st.rerun()

    # --- REPORT & EXPORT ---
    elif menu == "📈 Gabaasa Bal'aa":
        st.header("📈 Gabaasa fi Galii")
        st.dataframe(df[COL_NAMES], use_container_width=True)
        
        # Excel Download
        buf = io.BytesIO()
        with pd.ExcelWriter(buf, engine='xlsxwriter') as writer:
            df[COL_NAMES].to_excel(writer, index=False, sheet_name='Gabaasa')
        
        st.download_button(
            label="📥 Gabaasa Excel Buusi",
            data=buf.getvalue(),
            file_name=f"Gabaasa_Dadar_{datetime.now().strftime('%Y-%m-%d')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    # --- AWARDS ---
    elif menu == "🏆 Badhaasa":
        st.header("🏆 Ogeeyyii Cimoo")
        if not df.empty:
            top_3 = df['Maqaa_Ogeessa'].value_counts().head(3)
            cols = st.columns(3)
            for i, (name, count) in enumerate(top_3.items()):
                with cols[i]:
                    st.markdown(f"<div class='card'><h3>{name}</h3><p>Hojii: {count}</p></div>", unsafe_allow_html=True)
                    pdf_bytes = create_advanced_pdf(name, count, i+1)
                    st.download_button(f"📥 Sartiifiketa {i+1}", data=pdf_bytes, file_name=f"Badhaasa_{name}.pdf")

    # --- SEARCH/EDIT ---
    elif menu == "🔍 Barbaadi":
        st.header("🔍 Barbaadi / Sirreessi")
        q = st.text_input("Maqaa Barbaadi")
        if q:
            res = df[df['Maqaa_Abbaa_Dhimmaa'].str.contains(q, case=False, na=False)]
            st.write(res)
            st.session_state.logged_in = True
            st.rerun()
else:
    df = load_data()
    menu = st.sidebar.radio("FILANNOO", ["📊 Dashboard", "📝 Galmee Haaraa", "📈 Gabaasa"])

    # --- REGISTRATION LOGIC ---
    if menu == "📝 Galmee Haaraa":
        st.header("📝 Galmee Tajaajilaa Haaraa")
        
        with st.form("entry_form"):
            col1, col2 = st.columns(2)
            name = col1.text_input("Maqaa Abbaa Dhimmaa")
            ara = col2.text_input("Araddaa")
            qax = col1.text_input("Qaxana")
            ogeessa = col2.text_input("Maqaa Ogeessaa")
            
            st.markdown("---")
            st.subheader("Filannoo Tajaajilaa")
            
            selected_services = []
            total_fee = 0.0
            
            # Gosa tajaajilaa hunda keessa deemuun 'checkbox' uumuu
            for category, services in SERVICE_STRUCTURE.items():
                with st.expander(category):
                    for s in services:
                        if st.checkbox(s, key=s):
                            fee = st.number_input(f"Kaffaltii {s}", min_value=0.0, key=f"fee_{s}")
                            selected_services.append(s)
                            total_fee += fee
            
            submitted = st.form_submit_button("💾 Galmeessi")
            
            if submitted:
                if name and ogeessa and selected_services:
                    new_row = [
                        datetime.now().strftime('%d/%m/%Y'),
                        name, ara, qax, 
                        ", ".join(selected_services), 
                        ogeessa, 
                        total_fee
                    ]
                    # Update & Save
                    new_df = pd.DataFrame([new_row], columns=COL_NAMES)
                    df = pd.concat([df, new_df], ignore_index=True)
                    save_data(df)
                    st.success(f"Galmeen {name} milkaa'inaan raawwatameera! Total: {total_fee} ETB")
                else:
                    st.error("Maaloo! Maqaa fi Gosa tajaajilaa filadhu.")

    # --- DASHBOARD ---
    elif menu == "📊 Dashboard":
        st.header("Dashboard Waliigalaa")
        if not df.empty:
            c1, c2 = st.columns(2)
            c1.metric("Waliigala Galii", f"{df['Kafaltii_Taj'].sum():,.2f} ETB")
            c2.metric("Baay'ina Maamilaa", len(df))
            st.bar_chart(df.groupby('Maqaa_Ogeessa')['Kafaltii_Taj'].sum())
        else:
            st.info("Hanga ammaatti data'n hin galmeeffamne.")
    pdf.add_page()
    
    # Border
    pdf.set_draw_color(46, 125, 50) 
    pdf.set_line_width(3)
    pdf.rect(10, 10, 277, 190)
    
    # Logo on PDF
    if os.path.exists(LOGO_PATH):
        pdf.image(LOGO_PATH, 130, 15, 30)
    
    pdf.set_y(50)
    pdf.set_font('Arial', 'B', 24)
    title = "WARAQAA QULQULLUMMAA" if type=="Clearance" else "SARTIIFIKEETA BEEKAMTII"
    pdf.cell(0, 15, title, 0, 1, 'C')
    
    pdf.ln(10)
    pdf.set_font('Arial', '', 16)
    if type == "Clearance":
        msg = f"Obbo/Adde {name}, Araddaa {araddaa} keessatti kan argaman, kaffaltii mootummaa irraa jiru hunda xumuruu isaanii fi qabiyyeen isaanii kamirraayyuu bilisa ta'uu isaa ni mirkaneessina."
    else:
        msg = f"Sartiifikeetii kun Ogeessa {ogeessa} tajaajila ol'aana kennuun maamiltoota {name} tajaajileef badhaasa beekamtii kennameedha."
    
    pdf.multi_cell(0, 10, msg, align='C')
    pdf.set_y(160)
    pdf.cell(0, 10, f"Guyyaa: {datetime.now().strftime('%d/%m/%Y')} | Mallattoo & Chaappaa: ________________", 0, 1, 'C')
    return pdf.output(dest='S').encode('latin-1', 'replace')

# ================= 3. UI STYLE =================
st.set_page_config(page_title="Dadar Land Admin", page_icon="🏢", layout="wide")
st.markdown("""
    <style>
    .stApp { background-color: #f4f7f6; }
    .login-box { background: white; padding: 40px; border-radius: 20px; box-shadow: 0 10px 25px rgba(0,0,0,0.1); border-top: 10px solid #2e7d32; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

# ================= 4. LOGIN CENTERED =================
if 'logged_in' not in st.session_state: st.session_state.logged_in = False

if not st.session_state.logged_in:
    _, col, _ = st.columns([1, 1.2, 1])
    with col:
        st.markdown('<div style="margin-top:80px;"></div>', unsafe_allow_html=True)
        st.markdown('<div class="login-box">', unsafe_allow_html=True)
        if os.path.exists(LOGO_PATH): 
            st.image(LOGO_PATH, width=120)
        st.header("Dadar Land Admin")
        st.write("Sallamaa Seeni")
        with st.form("Login"):
            u = st.text_input("Username")
            p = st.text_input("Password", type="password")
            if st.form_submit_button("SEENI / LOGIN", use_container_width=True):
                if u == "admin" and p == "2026":
                    st.session_state.logged_in = True
                    st.rerun()
                else: st.error("Maaloo deebisii yaali!")
        st.markdown('</div>', unsafe_allow_html=True)
else:
    # ================= 5. MAIN SYSTEM =================
    df = load_data()
    
    # Sidebar Logo
    if os.path.exists(LOGO_PATH):
        st.sidebar.image(LOGO_PATH, width=100)
    st.sidebar.title("Main Menu")
    menu = st.sidebar.radio("FILANNOO", ["📊 Dashboard", "📝 Galmee Haaraa", "📈 Gabaasa", "🏆 Badhaasa", "🔍 Barbaadi", "Logout"])

    if menu == "Logout":
        st.session_state.logged_in = False
        st.rerun()

    elif menu == "📊 Dashboard":
        st.title("📊 Dashboard")
        c1, c2, c3 = st.columns(3)
        c1.metric("💰 Galii Waliigalaa", f"{df['Kafaltii_Taj'].sum():,.2f} ETB")
        c2.metric("👥 Maamiltoota", len(df))
        c3.metric("👷 Ogeeyyii", df['Maqaa_Ogeessa'].nunique())
        st.plotly_chart(px.bar(df, x='Gosa_Tajajjilaa', y='Kafaltii_Taj', color='Gosa_Tajajjilaa', barmode='group'))

    elif menu == "📝 Galmee Haaraa":
        st.title("📝 Galmee Tajaajilaa Haaraa")
        with st.container(border=True):
            col1, col2 = st.columns(2)
            name = col1.text_input("Maqaa Abbaa Dhimmaa")
            ara = col1.text_input("Araddaa")
            qax = col2.text_input("Qaxana")
            og = col2.text_input("Maqaa Ogeessaa")
            gosa = st.selectbox("Gosa Tajaajilaa", ["Gibira Baaxii", "TOT 2%", "Kaartaa Haaraa", "Clearance", "Liizii Waggaa"])
            fee = st.number_input("Kaffaltii (ETB)", min_value=0.0)
            
            if st.button("💾 GALMEESSI FI EERGI", use_container_width=True):
                if name and og:
                    f_fee = fee * 0.02 if "TOT" in gosa else fee
                    row = [datetime.now().strftime('%d/%m/%Y'), name, ara, qax, gosa, og, f_fee]
                    df = pd.concat([df, pd.DataFrame([row], columns=COL_NAMES)], ignore_index=True)
                    save_data(df)
                    # Send to Telegram
                    send_telegram(f"✅ *Galmee Haaraa*\n👤 Maqaa: {name}\n📍 Araddaa: {ara}\n🛠 Gosa: {gosa}\n💵 Kaffaltii: {f_fee} ETB")
                    st.success(f"✅ Galmeeffameera! Gabaasni Telegram irratti ergameera.")
                else: st.error("Maaloo odeeffannoo guutuu galchi!")

    elif menu == "📈 Gabaasa":
        st.title("📈 Gabaasa Waliigalaa")
        st.dataframe(df, use_container_width=True)
        st.download_button("📥 Excel/CSV Buufadhu", df.to_csv(index=False), "gabaasa_dadar.csv")

    elif menu == "🏆 Badhaasa":
        st.title("🏆 Badhaasa fi Clearance")
        t1, t2 = st.tabs(["📄 Waraqaa Qulqullummaa", "🎖 Badhaasa Ogeeyyii"])
        
        with t1:
            if not df.empty:
                sel_name = st.selectbox("Maqaa Maamilaa Filadhu:", df['Maqaa_Abbaa_Dhimmaa'].unique())
                if st.button("🖨 Clearance Qopheessi"):
                    u_data = df[df['Maqaa_Abbaa_Dhimmaa'] == sel_name].iloc[-1]
                    pdf = create_pdf(u_data['Maqaa_Abbaa_Dhimmaa'], u_data['Araddaa'], u_data['Maqaa_Ogeessa'], "Clearance")
                    st.download_button(f"📥 {sel_name} Clearance Buufadhu", pdf, f"Clearance_{sel_name}.pdf")
            else: st.warning("Ragaan galmeeffame hin jiru.")

        with t2:
            if not df.empty:
                top_og = df['Maqaa_Ogeessa'].value_counts().idxmax()
                count = df['Maqaa_Ogeessa'].value_counts().max()
                st.success(f"Ogeessi Cimaan: {top_og} (Maamiltoota {count} tajaajile)")
                if st.button("🎖 Sartii Badhaasaa Print"):
                    pdf = create_pdf(str(count), "", top_og, "Award")
                    st.download_button(f"📥 Sartii {top_og} Buufadhu", pdf, f"Award_{top_og}.pdf")

    elif menu == "🔍 Barbaadi":
        st.title("🔍 Barbaadi & Haqii")
        q = st.text_input("Maqaa Abbaa Dhimmaa Barbaadi...")
        if q:
            search_res = df[df['Maqaa_Abbaa_Dhimmaa'].str.contains(q, case=False, na=False)]
            st.dataframe(search_res)
            if not search_res.empty:
                if st.button("🗑 Haqii (Delete)"):
                    df = df.drop(search_res.index)
                    save_data(df)
                    st.rerun()


