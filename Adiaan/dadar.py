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
    c.execute('''CREATE TABLE IF NOT EXISTS records 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, yeroo TEXT, maqaa TEXT, 
                  araddaa TEXT, qaxana TEXT, gosa TEXT, ogeessa TEXT, kafaltii REAL)''')
    c.execute('''CREATE TABLE IF NOT EXISTS users 
                 (username TEXT PRIMARY KEY, password TEXT, role TEXT)''')
    # Default Admin
    admin_pwd = hash_password("admin123")
    c.execute("INSERT OR IGNORE INTO users VALUES (?, ?, ?)", ("admin", admin_pwd, "Admin"))
    conn.commit()
    conn.close()

init_db()

def load_data_sql(role, user):
    conn = sqlite3.connect("dadar_land.db")
    if role == "Admin":
        df = pd.read_sql_query("SELECT * FROM records", conn)
    else:
        df = pd.read_sql_query("SELECT * FROM records WHERE ogeessa = ?", conn, params=(user,))
    conn.close()
    return df

# ================= 3. PDF GENERATORS =================
def generate_receipt(data):
    pdf = FPDF(orientation='P', unit='mm', format=(100, 150))
    pdf.add_page()
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 8, "BULCHIINSA LAFAA DADAR", ln=True, align='C')
    pdf.set_font('Arial', '', 10)
    pdf.cell(0, 5, "NAGAHEE KAFALTII", ln=True, align='C')
    pdf.line(10, 25, 90, 25)
    pdf.ln(10)
    for k, v in data.items():
        pdf.cell(0, 7, f"{k.capitalize()}: {v}", ln=True)
    return pdf.output(dest='S').encode('latin-1', 'replace')

# ================= 4. LOGIN SYSTEM =================
if 'logged_in' not in st.session_state:
    st.session_state.update({'logged_in': False, 'user': None, 'role': None})

if not st.session_state.logged_in:
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
                if res:
                    st.session_state.update({'logged_in': True, 'user': u, 'role': res[0]})
                    st.rerun()
                else: st.error("Username ykn Password dogoggora!")
else:
    # --- SIDEBAR ---
    with st.sidebar:
        st.markdown(f"### 👤 {st.session_state.user} ({st.session_state.role})")
        menu = st.radio("MENU", ["📊 Dashboard", "📝 Galmee Haaraa", "🔍 Barbaadi", "⚙️ Bulchiinsa", "Ba'i"])
        
        # Excel Backup (Option A)
        st.divider()
        if st.button("📥 Excel Backup Buufadhu"):
            df_full = load_data_sql("Admin", "")
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                df_full.to_excel(writer, index=False)
            st.download_button("Download Excel", output.getvalue(), "Backup_Dadar.xlsx")

    df = load_data_sql(st.session_state.role, st.session_state.user)

    # ================= 5. APP MODULES =================
    if menu == "📊 Dashboard":
        st.header("📊 Gabaasa Gabaabaa")
        if not df.empty:
            c1, c2, c3 = st.columns(3)
            c1.metric("Baay'ina Tajaajilaa", len(df))
            c2.metric("Kafaltii Waliigalaa", f"{df['kafaltii'].sum():,.2f} ETB")
            c3.metric("Ogeessota", len(df['ogeessa'].unique()))
            
            # Chart
            df['yeroo'] = pd.to_datetime(df['yeroo'], dayfirst=True)
            fig = px.bar(df.resample('M', on='yeroo').sum().reset_index(), x='yeroo', y='kafaltii', title="Galii Ji'aan")
            st.plotly_chart(fig, use_container_width=True)
        else: st.info("Ragaan hin jiru.")

    elif menu == "📝 Galmee Haaraa":
        st.header("📝 Galmee Tajaajilaa Haaraa")
        GATII_DICT = {"Kartaa": 150.0, "Jijjirra Maqaa": 200.0, "Dhimma Dangaa": 100.0}
        with st.form("reg_form"):
            c1, c2 = st.columns(2)
            maqaa = c1.text_input("Maqaa Abbaa Dhimmaa")
            araddaa = c2.text_input("Araddaa")
            gosa = c1.selectbox("Gosa Tajaajilaa", list(GATII_DICT.keys()))
            if st.form_submit_button("💾 Galmeessi"):
                val = [datetime.now().strftime('%d/%m/%Y'), maqaa, araddaa, "N/A", gosa, st.session_state.user, GATII_DICT[gosa]]
                conn = sqlite3.connect("dadar_land.db")
                conn.cursor().execute("INSERT INTO records (yeroo, maqaa, araddaa, qaxana, gosa, ogeessa, kafaltii) VALUES (?,?,?,?,?,?,?)", val)
                conn.commit()
                st.success("Galmeeffameera!")
                
                receipt = generate_receipt({'maqaa': maqaa, 'gosa': gosa, 'kafaltii': GATII_DICT[gosa]})
                st.download_button("📄 Nagahee Buufadhu", receipt, f"Nagahee_{maqaa}.pdf")

    elif menu == "🔍 Barbaadi":
        q = st.text_input("Maqaa Barbaadi...")
        res = df[df['maqaa'].str.contains(q, case=False, na=False)]
        st.dataframe(res, use_container_width=True)
        if st.session_state.role == "Admin" and not res.empty:
            idx = st.number_input("ID Galmee Haquu Barbaaddu Galchi", step=1)
            if st.button("🗑 Haqi"):
                conn = sqlite3.connect("dadar_land.db")
                conn.cursor().execute("DELETE FROM records WHERE id=?", (idx,))
                conn.commit()
                st.rerun()

    elif menu == "⚙️ Bulchiinsa":
        if st.session_state.role == "Admin":
            st.subheader("Nama Haaraa Galmeessi")
            new_u = st.text_input("Username Haaraa")
            new_p = st.text_input("Password Haaraa", type="password")
            role = st.selectbox("Gahee", ["Ogeessa", "Admin"])
            if st.button("Mirkaneessi"):
                conn = sqlite3.connect("dadar_land.db")
                conn.cursor().execute("INSERT INTO users VALUES (?,?,?)", (new_u, hash_password(new_p), role))
                conn.commit()
                st.success("Fayyadamaan haaraa uumameera!")
        else: st.error("Mirga Admin hin qabdu!")

    elif menu == "Ba'i":
        st.session_state.logged_in = False
        st.rerun()
