import streamlit as st
import pandas as pd
import os
import io
from datetime import datetime
from fpdf import FPDF

# ================= 1. CONFIGURATION =================
DATA_FILE = "dadar_final_report.txt"
COL_NAMES = ['Guyyaa', 'Maqaa_Abbaa_Dhimmaa', 'Araddaa', 'Qaxana', 'Gosa_Tajajjilaa', 'Maqaa_Ogeessa', 'Kafaltii_Taj']

# Service List (Ati kan qopheessite)
SERVICE_STRUCTURE = {
    "🏷 Gibira & Kaffaltii": ["Gibira Baaxii Gooroo", "Gibira Lafa Qonnaa", "Kafaltii Liizii Waggaa", "Kafaltii Liizii Duraa"],
    "📜 Kaartaa & Qabiyyee": ["Kaartaa Haaraa", "Kaartaa Bakka Bu'aa", "Jijjiirraa Maqaa (Gift/Sale)"],
    "🏗 Pilaanii & Ijaarsa": ["Hayyama Ijaarsaa", "Pilaanii Magaalaa", "Humna Mahandisummaa"],
    "⚖️ Dhimma Seeraa": ["Ugura Mana Murtii", "Ugura Kaasuu", "Waliigaltee Liqii Baankii"]
}

def load_data():
    if not os.path.exists(DATA_FILE) or os.stat(DATA_FILE).st_size == 0:
        return pd.DataFrame(columns=COL_NAMES)
    return pd.read_csv(DATA_FILE, sep="|", names=COL_NAMES, header=None, encoding='utf-8')

def save_data(df_to_save):
    df_to_save[COL_NAMES].to_csv(DATA_FILE, sep="|", index=False, header=False, encoding="utf-8")

# ================= 2. INTERFACE =================
if 'logged_in' not in st.session_state: st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("🔐 Dadar Land Admin Login")
    u = st.text_input("Username")
    p = st.text_input("Password", type="password")
    if st.button("Seeni"):
        if u == "DAD" and p == "2026": 
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

