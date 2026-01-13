import streamlit as st
import pandas as pd
import sqlite3
import hashlib
import io
import plotly.express as px
from datetime import datetime
from fpdf import FPDF

# ================= 1. CONFIG & STYLING =================
st.set_page_config(page_title="Dadar Land Admin Pro", layout="wide", page_icon="🏢")

# Akka koodiin keenya bifa bareedaa qabaatuuf
st.markdown("""
    <style>
    .stApp { background: linear-gradient(to bottom right, #f8fafc, #e2e8f0); }
    [data-testid="stSidebar"] { background-color: #0f172a !important; }
    div[data-testid="metric-container"] {
        background-color: #ffffff;
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        border-top: 5px solid #3b82f6;
    }
    </style>
    """, unsafe_allow_html=True)

# ================= 2. DATABASE & SECURITY =================
def hash_password(pwd):
    return hashlib.sha256(pwd.encode()).hexdigest()

def init_db():
    conn = sqlite3.connect("dadar_land.db")
    c = conn.cursor()
    # Teebulii ragaa tajaajilaa
    c.execute('''CREATE TABLE IF NOT EXISTS records 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, yeroo TEXT, maqaa TEXT, 
                  araddaa TEXT, qaxana TEXT, gosa TEXT, ogeessa TEXT, kafaltii REAL)''')
    # Teebulii fayyadamtootaa
    c.execute('''CREATE TABLE IF NOT EXISTS users 
                 (username TEXT PRIMARY KEY, password TEXT, role TEXT)''')
    
    # Admin durumaan jiru (Password: admin123)
    admin_pwd = hash_password("admin123")
    c.execute("INSERT OR IGNORE INTO users VALUES (?, ?, ?)", ("admin", admin_pwd, "Admin"))
    conn.commit()
    conn.close()

# Database jalqabsiisuu
init_db()

def load_data_sql(role, user):
    conn = sqlite3.connect("dadar_land.db")
    if role == "Admin":
        df = pd.read_sql_query("SELECT * FROM records", conn)
    else:
        df = pd.read_sql_query("SELECT * FROM records WHERE ogeessa = ?", conn, params=(user,))
    conn.close()
    return df

# ================= 3. PDF GENERATOR (NAGAHEE) =================
def generate_receipt(data):
    pdf = FPDF(orientation='P', unit='mm', format=(100, 150))
    pdf.add_page()
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 8, "BULCHIINSA LAFAA DADAR", ln=True, align='C')
    pdf.set_font('Arial', '', 10)
    pdf.cell(0, 5, "NAGAHEE KAFALTII", ln=True, align='C')
    pdf.line(10, 25, 90, 25)
    pdf.ln(10)
    pdf.set_font('Arial', '', 9)
    pdf.cell(0, 7, f"Guyyaa: {data['Guyyaa']}", ln=True)
    pdf.cell(0, 7, f"Maqaa: {data['Maqaa']}", ln=True)
    pdf.cell(0, 7, f"Gosa: {data['Gosa']}", ln=True)
    pdf.cell(0, 7, f"Kafaltii: {data['Kafaltii']} ETB", ln=True)
    pdf.ln(5)
    pdf.cell(0, 7, f"Ogeessa: {data['Ogeessa']}", ln=True)
    return pdf.output(dest='S').encode('latin-1', 'replace')

# ================= 4. AUTHENTICATION LOGIC =================
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

# --- LOGOUT FUNC ---
def logout():
    st.session_state.logged_in = False
    st.session_state.user = None
    st.session_state.role = None
    st.rerun()

# ================= 5. MAIN APP =================

if not st.session_state.logged_in:
    # --- FUULA LOGIN ---
    _, col_mid, _ = st.columns([1, 1.5, 1])
    with col_mid:
        st.markdown("<h1 style='text-align: center;'>🏢 Dadar Land Admin</h1>", unsafe_allow_html=True)
        with st.container(border=True):
            u = st.text_input("Username")
            p = st.text_input("Password", type="password")
            if st.button("Seeni", use_container_width=True):
                conn = sqlite3.connect("dadar_land.db")
                c = conn.cursor()
                c.execute("SELECT role FROM users WHERE username=? AND password=?", (u, hash_password(p)))
                res = c.fetchone()
                conn.close()
                if res:
                    st.session_state.logged_in = True
                    st.session_state.user = u
                    st.session_state.role = res[0]
                    st.rerun()
                else:
                    st.error("Username ykn Password dogoggora!")
else:
    # --- SIDEBAR NAV ---
    with st.sidebar:
        st.markdown(f"### 👤 {st.session_state.user} ({st.session_state.role})")
        menu = st.radio("MENU", ["📊 Dashboard", "📝 Galmee Haaraa", "🔍 Barbaadi", "⚙️ Bulchiinsa"])
        st.divider()
        if st.button("🚪 Ba'i (Logout)", use_container_width=True):
            logout()
        
        # Excel Backup (Option A)
        st.divider()
        if st.button("📥 Excel Backup Buufadhu"):
            df_full = load_data_sql("Admin", "")
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                df_full.to_excel(writer, index=False)
            st.download_button("Download Excel Now", output.getvalue(), f"Backup_Dadar_{datetime.now().strftime('%Y%m%d')}.xlsx")

    # Data fe'uu
    df = load_data_sql(st.session_state.role, st.session_state.user)

    # --- MODULES ---
    if menu == "📊 Dashboard":
        st.header("📊 Gabaasa Gabaabaa")
        if not df.empty:
            c1, c2, c3 = st.columns(3)
            c1.metric("Baay'ina Tajaajilaa", len(df))
            c2.metric("Kafaltii Waliigalaa", f"{df['kafaltii'].sum():,.2f} ETB")
            c3.metric("Ogeessota", len(df['ogeessa'].unique()))
            
            # Chart Galii
            st.subheader("📈 Akkaataa Galii Ji'aa")
            df['yeroo_dt'] = pd.to_datetime(df['yeroo'], dayfirst=True)
            chart_data = df.resample('M', on='yeroo_dt').sum().reset_index()
            fig = px.line(chart_data, x='yeroo_dt', y='kafaltii', markers=True)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Ragaan galmeeffame hin jiru.")

    elif menu == "📝 Galmee Haaraa":
        st.header("📝 Galmee Tajaajilaa Haaraa")
        GATII_DICT = {"Kartaa": 150.0, "Jijjirra Maqaa": 200.0, "Dhimma Dangaa": 100.0, "Mana Murtii": 0.0}
        with st.form("reg_form", clear_on_submit=True):
            c1, c2 = st.columns(2)
            maqaa = c1.text_input("Maqaa Abbaa Dhimmaa")
            araddaa = c2.text_input("Araddaa")
            qaxana = c1.text_input("Qaxana")
            gosa = c2.selectbox("Gosa Tajaajilaa", list(GATII_DICT.keys()))
            
            if st.form_submit_button("💾 Galmeessi"):
                if maqaa:
                    guyyaa = datetime.now().strftime('%d/%m/%Y')
                    gatii = GATII_DICT[gosa]
                    val = (guyyaa, maqaa, araddaa, qaxana, gosa, st.session_state.user, gatii)
                    
                    conn = sqlite3.connect("dadar_land.db")
                    conn.cursor().execute("INSERT INTO records (yeroo, maqaa, araddaa, qaxana, gosa, ogeessa, kafaltii) VALUES (?,?,?,?,?,?,?)", val)
                    conn.commit()
                    conn.close()
                    st.success(f"Galmeeffameera! Kafaltii: {gatii} ETB")
                    
                    # Nagahee Qopheessu
                    r_data = {'Guyyaa': guyyaa, 'Maqaa': maqaa, 'Gosa': gosa, 'Kafaltii': gatii, 'Ogeessa': st.session_state.user}
                    receipt_pdf = generate_receipt(r_data)
                    st.download_button("📄 Nagahee PDF Buufadhu", receipt_pdf, f"Nagahee_{maqaa}.pdf")
                else:
                    st.error("Maqaa guutuu qabda!")

    elif menu == "🔍 Barbaadi":
        st.header("🔍 Barbaadi fi Sirreessi")
        q = st.text_input("Maqaa Abbaa Dhimmaa barreessi...")
        if not df.empty:
            res = df[df['maqaa'].str.contains(q, case=False, na=False)]
            st.dataframe(res, use_container_width=True)
            
            if st.session_state.role == "Admin" and not res.empty:
                st.divider()
                st.subheader("🗑 Galmee Haquu (Admin Only)")
                idx_to_del = st.number_input("ID Galmee haquu barbaaddu galchi:", step=1, min_value=0)
                if st.button("Haquu Mirkaneessi"):
                    conn = sqlite3.connect("dadar_land.db")
                    conn.cursor().execute("DELETE FROM records WHERE id=?", (idx_to_del,))
                    conn.commit()
                    conn.close()
                    st.warning(f"Galmeen ID {idx_to_del} haqameera!")
                    st.rerun()

    elif menu == "⚙️ Bulchiinsa":
        if st.session_state.role == "Admin":
            st.header("⚙️ Bulchiinsa Fayyadamtootaa")
            with st.expander("Nama Haaraa Galmeessi"):
                new_u = st.text_input("Username Haaraa")
                new_p = st.text_input("Password Haaraa", type="password")
                new_r = st.selectbox("Gahee (Role)", ["Ogeessa", "Admin"])
                if st.button("Fayyadamaa Uumi"):
                    if new_u and new_p:
                        conn = sqlite3.connect("dadar_land.db")
                        try:
                            conn.cursor().execute("INSERT INTO users VALUES (?,?,?)", (new_u, hash_password(new_p), new_r))
                            conn.commit()
                            st.success(f"Fayyadamaa '{new_u}' uumameera!")
                        except:
                            st.error("Maqaan kun duraan jira!")
                        finally:
                            conn.close()
            
            st.subheader("Tarree Hojjettootaa")
            conn = sqlite3.connect("dadar_land.db")
            st.table(pd.read_sql_query("SELECT username, role FROM users", conn))
            conn.close()
        else:
            st.error("Kutaa kana arguuf mirga Admin qabaachuu qabda!")
