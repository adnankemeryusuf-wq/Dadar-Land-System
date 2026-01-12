import streamlit as st
import pandas as pd
import os
import hashlib
from datetime import datetime
from fpdf import FPDF
from PIL import Image, ImageDraw, ImageOps

# ================= CONFIG =================
st.set_page_config(page_title="Dadar Land Admin Pro", layout="wide", page_icon="🏢")

DATA_FILE = "dadar_final_report.txt"
USERS_FILE = "users.csv"
# Logoo barbaaduu
LOGO_PATH = next((p for p in ["logo.png", "Adiaan/logo.png"] if os.path.exists(p)), None)

COL_NAMES = ['Yeroo', 'Maqaa', 'Araddaa', 'Qaxana', 'Gosa', 'Ogeessa', 'Kafaltii_Taj', 'Kafaltii_Wal', 'C1', 'C2', 'C3']

# ================= SECURITY =================
def hash_password(pwd):
    return hashlib.sha256(pwd.encode()).hexdigest()

# ================= USERS =================
def load_users():
    if not os.path.exists(USERS_FILE):
        df = pd.DataFrame([["admin", hash_password("admin123"), "admin"]], columns=["username", "password", "role"])
        df.to_csv(USERS_FILE, index=False)
    return pd.read_csv(USERS_FILE)

def save_users(df):
    df.to_csv(USERS_FILE, index=False)

# ================= DATA =================
def load_data():
    if not os.path.exists(DATA_FILE) or os.stat(DATA_FILE).st_size == 0:
        return pd.DataFrame(columns=COL_NAMES)
    try:
        return pd.read_csv(DATA_FILE, sep="|", names=COL_NAMES, header=None, on_bad_lines='skip', encoding='utf-8')
    except:
        return pd.DataFrame(columns=COL_NAMES)

def save_data(df):
    df.to_csv(DATA_FILE, sep="|", index=False, header=False, encoding="utf-8")

# ================= HELPER: CIRCULAR LOGO =================
def get_circular_logo(path):
    if path and os.path.exists(path):
        img = Image.open(path).convert("RGBA")
        size = (400, 400)
        img = img.resize(size, Image.LANCZOS)
        mask = Image.new('L', size, 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((0, 0) + size, fill=255)
        img.putalpha(mask)
        # Background adii gochuu PDF-f
        output = Image.new("RGB", size, (255, 255, 255))
        output.paste(img, mask=img.split()[3])
        return output
    return None

# ================= SARTIIFIKETA (Centered & Circular) =================
def generate_certificate(expert_name):
    pdf = FPDF(orientation='L', unit='mm', format='A4')
    pdf.add_page()
    
    # Border Navy & Gold
    pdf.set_line_width(2); pdf.set_draw_color(184, 134, 11)
    pdf.rect(5, 5, 287, 200) 
    
    # --- LOGO CHAACHOO JIDDUUTTI ---
    circular_img = get_circular_logo(LOGO_PATH)
    if circular_img:
        pdf.image(circular_img, x=131, y=10, w=35)

    pdf.ln(35)
    pdf.set_font('Times', 'B', 40); pdf.set_text_color(30, 58, 138)
    pdf.cell(0, 20, "SARTIIFIKETA BEEKAMTII", ln=True, align='C')
    
    pdf.ln(5); pdf.set_font('Arial', 'I', 16); pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 10, "Waajjira Lafaa Bulchiinsa Magaalaa Dadar", ln=True, align='C')
    
    pdf.ln(10); pdf.set_font('Arial', '', 20)
    pdf.cell(0, 10, "Gootummaa Hojii Waggaa kan kennameef:", ln=True, align='C')
    
    pdf.ln(5); pdf.set_font('Times', 'B', 32); pdf.set_text_color(21, 128, 61)
    pdf.cell(0, 15, f"Obbo/Adde: {expert_name.upper()}", ln=True, align='C')
    
    pdf.ln(10); pdf.set_font('Arial', '', 14); pdf.set_text_color(60, 60, 60)
    # Lakkoofsi haqameera
    msg = ("Waggaa kanatti tajaajila saffisaa, iftoomina qabuu fi amannamaa ta'een "
            "hojii gaarii hojjettanii waan argamtaniif beekamtii kanaan badhaafamaniiru.")
    pdf.multi_cell(0, 10, msg, align='C')
    
    pdf.set_y(172)
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(100, 8, "__________________________", ln=0, align='C')
    pdf.cell(87, 8, "", ln=0)
    pdf.cell(100, 8, "__________________________", ln=1, align='C')
    pdf.cell(100, 5, "Aqiil Abdujaaliil", ln=0, align='C')
    pdf.cell(87, 5, "", ln=0)
    pdf.cell(100, 5, datetime.now().strftime("%d/%m/%Y"), ln=1, align='C')
    
    return pdf.output(dest='S').encode('latin-1')

# ================= LOGIN =================
def login_page():
    _, col_mid, _ = st.columns([1, 1.2, 1])
    with col_mid:
        if LOGO_PATH: st.image(LOGO_PATH, width=150)
        st.title("🏢 Seensa Sirna")
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")

        if st.button("Seeni", use_container_width=True):
            users = load_users()
            h = hash_password(p)
            user = users[(users.username == u) & (users.password == h)]

            if not user.empty:
                st.session_state.logged_in = True
                st.session_state.user = u
                st.session_state.role = user.iloc[0]['role']
                st.rerun()
            else:
                st.error("Username ykn Password dogoggora")

# ================= MAIN APP =================
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    login_page()
else:
    # Sidebar
    with st.sidebar:
        if LOGO_PATH: st.image(LOGO_PATH, width=120)
        st.success(f"👤 {st.session_state.user} ({st.session_state.role})")
        menu = st.radio("Menu", ["📝 Galmee", "🔍 Barbaaduu & Sirreessu", "📊 Odeeffannoo", "🏆 Sartiifiketa", "🧑‍💼 Users", "🚪 Ba'i"])

    df = load_data()

    if menu == "📝 Galmee":
        st.header("📝 Galmee Tajaajilaa Haaraa")
        with st.form("entry"):
            col1, col2 = st.columns(2)
            maqaa = col1.text_input("Maqaa Abbaa Dhimmaa")
            araddaa = col2.text_input("Araddaa")
            gosa = col1.selectbox("Gosa Tajaajilaa", ["Ittii Fayyaddam", "Kartaa", "Jijjirra Maqaa", "Dangaa", "Mana Murttii", "Liqii Bankii"])
            ogeessa = col2.text_input("Maqaa Ogeessaa")
            k_taj = col1.number_input("Kafaltii Tajaajilaa", min_value=0.0)
            k_wal = col2.number_input("Kafaltii Waliigalaa", min_value=0.0)
            if st.form_submit_button("💾 Galmeessi"):
                new_row = [datetime.now().strftime('%d/%m/%Y'), maqaa, araddaa, '', gosa, ogeessa, k_taj, k_wal, '', '', '']
                df.loc[len(df)] = new_row
                save_data(df)
                st.success("Milkaa'inaan galmeeffame!")
                st.rerun()

    elif menu == "🔍 Barbaaduu & Sirreessu":
        st.header("🔍 Barbaadi fi Sirreessi")
        q = st.text_input("Maqaa barbaadi...")
        if not df.empty:
            results = df[df['Maqaa'].str.contains(q, case=False, na=False)]
            if not results.empty:
                st.dataframe(results, use_container_width=True)
                selected_name = st.selectbox("Nama sirreessuuf filadhu:", results['Maqaa'].tolist())
                idx = df[df['Maqaa'] == selected_name].index[0]
                
                with st.form("edit_form"):
                    st.subheader(f"Sirreessu: {selected_name}")
                    e_maqaa = st.text_input("Maqaa", value=df.at[idx, 'Maqaa'])
                    e_araddaa = st.text_input("Araddaa", value=df.at[idx, 'Araddaa'])
                    e_ogeessa = st.text_input("Ogeessa", value=df.at[idx, 'Ogeessa'])
                    e_k_wal = st.number_input("Kafaltii", value=float(df.at[idx, 'Kafaltii_Wal']))
                    
                    c1, c2 = st.columns(2)
                    if c1.form_submit_button("💾 SAVE CHANGES"):
                        df.at[idx, 'Maqaa'] = e_maqaa
                        df.at[idx, 'Araddaa'] = e_araddaa
                        df.at[idx, 'Ogeessa'] = e_ogeessa
                        df.at[idx, 'Kafaltii_Wal'] = e_k_wal
                        save_data(df)
                        st.success("Fooyya'eera!")
                        st.rerun()
                    if c2.form_submit_button("🗑️ DELETE", type="primary"):
                        df = df.drop(idx)
                        save_data(df)
                        st.warning("Haqameera!")
                        st.rerun()

    elif menu == "📊 Odeeffannoo":
        st.header("📊 Gabaasa Waliigalaa")
        st.dataframe(df, use_container_width=True)
        # PDF Buufachuu
        from fpdf import FPDF
        def simple_pdf(data):
            pdf = FPDF(); pdf.add_page(); pdf.set_font("Arial", size=12)
            pdf.cell(200, 10, txt="Gabaasa Dadar Land Admin", ln=1, align='C')
            for i, r in data.iterrows():
                pdf.cell(0, 10, txt=f"{r['Maqaa']} - {r['Gosa']} - {r['Kafaltii_Wal']}", ln=1)
            return pdf.output(dest='S').encode('latin-1')
        
        st.download_button("📥 Gabaasa PDF Buusi", simple_pdf(df), "Gabaasa.pdf")

    elif menu == "🏆 Sartiifiketa":
        st.header("🏆 Beekamtii Ogeessaa")
        if not df.empty:
            og_counts = df['Ogeessa'].value_counts()
            if not og_counts.empty:
                best_og = og_counts.idxmax()
                st.success(f"Ogeessa Hojii Gaarii Hojjete: **{best_og}**")
                if st.button("📜 SARTIIFIKETA QOPHEESSI"):
                    cert_pdf = generate_certificate(best_og)
                    st.download_button("📥 PDF Buufadhu", cert_pdf, f"Sartiifiketa_{best_og}.pdf")

    elif menu == "🧑‍💼 Users" and st.session_state.role == "admin":
        st.header("🧑‍💼 Bulchiinsa Users")
        users = load_users()
        st.table(users[["username", "role"]])
        with st.form("add_user"):
            new_u = st.text_input("Username")
            new_p = st.text_input("Password", type="password")
            new_r = st.selectbox("Role", ["admin", "user"])
            if st.form_submit_button("➕ User Dabali"):
                users.loc[len(users)] = [new_u, hash_password(new_p), new_r]
                save_users(users)
                st.success("User dabalameera!")
                st.rerun()

    elif menu == "🚪 Ba'i":
        st.session_state.clear()
        st.rerun()
