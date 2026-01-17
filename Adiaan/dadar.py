import streamlit as st
import pandas as pd
import os
import io
import requests
import base64
from datetime import datetime
from fpdf import FPDF

# ================= 1. CONFIGURATION & STYLE =================
LOGO_PATH = "Adiaan/logo.png"
DATA_FILE = "dadar_final_report.txt"
BOT_TOKEN = "8357193631:AAHCuSnXzjZTQaglkmcS0gq-EvqnkIQLDBI"
CHAT_ID_MANAGER = "7329587700"

st.set_page_config(
    page_title="Dadar Land Customer Registration", 
    page_icon=LOGO_PATH if os.path.exists(LOGO_PATH) else "🏢", 
    layout="wide"
)

# Logo Base64 gochuuf (Header irratti mul'isuuf)
def get_base64_img(path):
    if os.path.exists(path):
        with open(path, "rb") as f:
            data = f.read()
        return base64.b64encode(data).decode()
    return ""

img_b64 = get_base64_img(LOGO_PATH)

# CSS - Logo bitaa qofaaf fi Style bareeduuf
st.markdown(f"""
    <style>
    .header-container {{
        display: flex;
        align-items: center;
        background-color: #ffffff;
        padding: 15px;
        border-radius: 12px;
        border-bottom: 5px solid #2e7d32;
        margin-bottom: 25px;
        box-shadow: 0px 4px 10px rgba(0,0,0,0.05);
    }}
    .logo-img {{ width: 90px; height: 90px; object-fit: contain; margin-right: 25px; }}
    .main-title {{ color: #1b5e20; font-family: 'Arial Black'; line-height: 1; }}
    .stApp {{ background-color: #f9fbf9; }}
    div.stForm {{ background: white; border-radius: 15px; border: 1px solid #ddd; padding: 20px; }}
    .card {{ background: white; padding: 20px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); text-align: center; border-top: 5px solid #2e7d32; }}
    </style>
    """, unsafe_allow_html=True)

# ================= 2. CORE FUNCTIONS =================
COL_NAMES = ['Guyyaa', 'Maqaa_Abbaa_Dhimmaa', 'Araddaa', 'Qaxana', 'Gosa_Tajajjilaa', 'Maqaa_Ogeessa', 'Kafaltii_Taj']
MONTH_ORDER = ["Fulbaana", "Onkololeessa", "Sadaasa", "Muddee", "Amajjii", "Guraandhala", "Bitootessa", "Eebila", "Caamsaa", "Waxabajjii", "Adooleessa", "Hagayya"]
MONTH_MAP = {9: "Fulbaana", 10: "Onkololeessa", 11: "Sadaasa", 12: "Muddee", 1: "Amajjii", 2: "Guraandhala", 3: "Bitootessa", 4: "Eebila", 5: "Caamsaa", 6: "Waxabajjii", 7: "Adooleessa", 8: "Hagayya"}

def load_data():
    if not os.path.exists(DATA_FILE) or os.stat(DATA_FILE).st_size == 0:
        return pd.DataFrame(columns=COL_NAMES)
    df = pd.read_csv(DATA_FILE, sep="|", names=COL_NAMES, header=None, encoding='utf-8')
    df['Date_Obj'] = pd.to_datetime(df['Guyyaa'], format='%d/%m/%Y', errors='coerce')
    df['Waggaa'] = df['Date_Obj'].dt.year
    df['Ji\'a'] = df['Date_Obj'].dt.month.map(MONTH_MAP)
    return df

def create_advanced_pdf(name, count, rank, cert_type="STAFF"):
    pdf = FPDF(orientation='L', unit='mm', format='A4')
    pdf.add_page()
    
    # Halluu Sadarkaa
    colors = {1: (255, 215, 0), 2: (192, 192, 192), 3: (205, 127, 50)}
    b_color = colors.get(rank, (27, 94, 32))
    
    # Borders
    pdf.set_draw_color(*b_color)
    pdf.set_line_width(3.0); pdf.rect(10, 10, 277, 190)
    pdf.set_line_width(1.0); pdf.rect(13, 13, 271, 184)
    
    # Logo Bitaa Qofa (PDF irratti)
    if os.path.exists(LOGO_PATH):
        pdf.image(LOGO_PATH, 15, 15, 30)
    
    pdf.set_y(50)
    pdf.set_font('Arial', 'B', 32); pdf.set_text_color(*b_color)
    title = "SARTIIFIKETA BEEKAMTII" if cert_type == "STAFF" else "WARAQAA RAGAA TAJAAJILAA"
    pdf.cell(0, 15, title, ln=True, align='C')
    
    pdf.set_font('Arial', '', 20); pdf.set_text_color(0, 0, 0); pdf.ln(20)
    if cert_type == "STAFF":
        msg = f"Obbo/Adde {str(name).upper()}\n\nTajaajilamtoota {count} saffisaan tajaajiluun sadarkaa {rank}ffaa\nwaggaa 2026 waan qabataniif beekamtiin kun kennameef."
    else:
        msg = f"Obbo/Adde {str(name).upper()}\n\nWaajjira Lafaa Bulchiinsa Magaalaa Dadar irraa tajaajila argachuu keessaniif ragaa kenname."
        
    pdf.multi_cell(0, 12, msg, align='C')
    pdf.set_y(170); pdf.line(110, 175, 187, 175)
    pdf.set_xy(110, 177); pdf.set_font('Arial', 'B', 12)
    pdf.cell(77, 8, "Itti Gaafatamaa Waajjiraa", align='C')
    return pdf.output(dest='S').encode('latin-1')

# ================= 3. MAIN APP =================
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    # Login Page (Maqaa waajjiraa fi Logo qofa)
    st.markdown("<br><br>", unsafe_allow_html=True)
    _, col_mid, _ = st.columns([1, 1.2, 1])
    with col_mid:
        if os.path.exists(LOGO_PATH): st.image(LOGO_PATH, width=120)
        st.markdown("<h2 style='text-align:center;'>Systemii Galmee Dadar</h2>", unsafe_allow_html=True)
        with st.form("login"):
            u = st.text_input("Username")
            p = st.text_input("Password", type="password")
            if st.form_submit_button("Seeni"):
                if u == "DAD" and p == "2026":
                    st.session_state.logged_in = True; st.rerun()
                else: st.error("Dogoggora!")
else:
    # --- HEADER (LOGO BITAA QOFA) ---
    logo_src = f"data:image/png;base64,{img_b64}" if img_b64 else ""
    st.markdown(f"""
        <div class="header-container">
            <img src="{logo_src}" class="logo-img"> 
            <div class="main-title">
                <h1 style='margin:0; font-size: 28px;'>BULCHIINSA MAGAALAA DADAR</h1>
                <h2 style='margin:0; font-size: 20px; color: #4caf50;'>WAAJJIRA LAFAA</h2>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    df = load_data()
    menu = st.sidebar.radio("FILANNOO", ["📊 Dashboard", "📝 Galmee Haaraa", "🏆 Badhaasa", "🔍 Barbaadi"])

   # 1. DASHBOARD
    if menu == "📊 Dashboard":
        st.header("📊 Dashboard")
        if not df.empty:
            c1, c2, c3 = st.columns(3)
            with c1: st.markdown(f"<div class='card'><p>💰 Galii</p><p class='metric-value'>{df['Kafaltii_Taj'].sum():,.2f}</p></div>", unsafe_allow_html=True)
            with c2: st.markdown(f"<div class='card'><p>👥 Maamiltoota</p><p class='metric-value'>{len(df)}</p></div>", unsafe_allow_html=True)
            with c3: st.markdown(f"<div class='card'><p>👷 Ogeeyyii</p><p class='metric-value'>{df['Maqaa_Ogeessa'].nunique()}</p></div>", unsafe_allow_html=True)
            st.area_chart(df.groupby('Ji\'a')['Kafaltii_Taj'].sum().reindex(MONTH_ORDER).fillna(0))
        else: st.info("Data'n hin jiru.")

    # 2. REGISTRATION
    elif menu == "📝 Galmee Haaraa":
        st.header("📝 Galmee Tajaajilaa")
        
        # Gosa tajaajilaa filachuuf
        GATII_DICT = {
            "Gibira": ["Gibira Baaxii Gooroo", "Gibira Lafa Qonnaa"],
            "Liizii": ["Liizii Waggaa", "Jijjiirraa Maqaa", "Kafaltii Liizii Duraa", "TOT"],
            "Ittii Fayyaddam": ["Hayyama Itti Fayyadama Lafaa", "Humna Mahandiisaa"],
            "Kaartaa": ["Kaartaa Lafa", "Kaartaa Kadastaara", "Kaartaa Lafa Qonnaa"],
            "Dhimma Mana Murtii": ["Ugura Mana Murtii", "Uguraa Mana Murtii Kaasuu"],
            "Liqii Bankii": ["Dorkka Liqii Bankii", "Dorkkaa Liqii Bankii Kaasuu"]
        }

        # 1. Filannoo Gosa Tajaajilaa (Dirqama akka filatamuuf)
        selected_main = st.multiselect("🟢 Gosa Tajaajilaa Filadhu (Dirqama)", list(GATII_DICT.keys()))
        
        details, d_fees = [], {}
        if selected_main:
            for g in selected_main:
                subs = st.multiselect(f"Tajaajila {g}:", GATII_DICT[g], key=f"m_{g}")
                for s in subs:
                    details.append(f"{g}({s})")
                    d_fees[f"{g}_{s}"] = st.number_input(f"Kafaltii {s} (ETB)", min_value=0.0, key=f"f_{g}_{s}")

        # 2. Form Galmee
        with st.form("entry_form", clear_on_submit=True):
            st.markdown("##### Odeeffannoo Maamilaa")
            c1, c2 = st.columns(2)
            
            # Form validation: placeholder fi label irratti "Required" dabalameera
            maqaa_f = c1.text_input("Maqaa Abbaa Dhimmaa *", placeholder="Maqaa guutuu barreessi")
            ara_f = c2.text_input("Araddaa *", placeholder="Araddaa  Dhimma")
            qax_f = c1.text_input("Qaxana *", placeholder="Qaxana Abbaa Dhimma")
            ogeessa = c2.text_input("Maqaa Ogeessaa *", placeholder="Maqaa Ogeessa")
            
            nagahee_file = st.file_uploader("Nagahee Scan (JPG/PNG)", type=['jpg','png','jpeg'])

            # Button submit
            submit = st.form_submit_button("💾 Galmeessi")

            if submit:
                # --- VALIDATION LOGIC ---
                # Check gochuu: Wantoonni ijoon guutamaniiru?
                if not maqaa_f or not ara_f or not qax_f or not ogeessa:
                    st.error("⚠️ Maaloo! Bakka mallattoo (*) qaban hunda guutuu kee mirkaneessi.")
                elif not details:
                    st.error("⚠️ Maaloo! Gosa tajaajilaa kamiyyuu hin filanne.")
                else:
                    # Yoo hundi guutame, data save godha
                    if nagahee_file:
                        f_name = f"{maqaa_f.replace(' ','_')}_{datetime.now().strftime('%H%M%S')}.jpg"
                        with open(os.path.join(NAGAHEE_DIR, f_name), "wb") as f:
                            f.write(nagahee_file.getbuffer())
                    
                    new_row = [
                        datetime.now().strftime('%d/%m/%Y'), 
                        maqaa_f, 
                        ara_f, 
                        qax_f, 
                        ", ".join(details), 
                        ogeessa, 
                        sum(d_fees.values())
                    ]
                    
                    # Data update gochuu
                    df = pd.concat([df, pd.DataFrame([new_row], columns=COL_NAMES)], ignore_index=True)
                    save_data(df)
                    
                    st.balloons() # Success animation
                    st.success(f"✅ Galmeen {maqaa_f} milkaa'inaan Galmeeffameera!")
                    
                    # Refresh gochuuf
                    # st.rerun()
        # 3. GABAASA
    elif menu == "📈 Gabaasa Bal'aa":
        st.header("📈 Gabaasa")
        st.dataframe(df[COL_NAMES])


# --- BADHAASA OGEEYYII ---
    elif menu == "🏆 Badhaasa Ogeeyyii":
        st.markdown("<h4 style='color: #1b5e20;'>🏆 Sadarkaa fi Badhaasa Ogeeyyii</h4>", unsafe_allow_html=True)
        
        # Logo filachuuf
        cl, cr = st.columns(2)
        l_l = cl.file_uploader("Logo Bitaa (PDF irratti)", type=['png', 'jpg'], key="logo_l")
        l_r = cr.file_uploader("Logo Mirgaa (PDF irratti)", type=['png', 'jpg'], key="logo_r")
        
        st.divider()

        if not df.empty:
            # Ogeeyyii baay'ina hojiitiin addaan baasuu
            top_3 = df['Maqaa_Ogeessa'].value_counts().head(3)
            cols = st.columns(3)
            
            # Halluuwwan sadarkaaf
            colors = ["#FFD700", "#C0C0C0", "#CD7F32"] # Gold, Silver, Bronze
            labels = ["1FFAA", "2FFAA", "3FFAA"]

            for i, (name, count) in enumerate(top_3.items()):
                with cols[i]:
                    # Card bareedaa halluu sadarkaatiin
                    st.markdown(f"""
                        <div class='card' style='border-top: 5px solid {colors[i]};'>
                            <h2 style='color: {colors[i]};'>{labels[i]}</h2>
                            <h3 style='margin: 5px 0;'>{name}</h3>
                            <p style='font-size: 14px; color: #555;'>Hojii Raawwatame: <b>{count}</b></p>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    # PDF Generate gochuu
                    try:
                        pdf_file = create_advanced_pdf(name, count, i+1, l_l, l_r)
                        st.download_button(
                            label=f"📥 Sartiifiketa {labels[i]}",
                            data=pdf_file,
                            file_name=f"Sadarkaa_{i+1}_{name}.pdf",
                            mime="application/pdf",
                            key=f"dl_{i}"
                        )
                    except Exception as e:
                        st.error("PDF uumuu irratti dogoggora!")
        else:
            st.info("Data'n hojii ogeeyyii agarsiisu hin jiru.")

    # --- SEARCH & EDIT ---
    elif menu == "🔍 Barbaadi/Edit":
        col_l, col_r = st.columns([1, 4])
        with col_l:
            if os.path.exists(LOGO_PATH):
                st.image(LOGO_PATH, width=80)
        with col_r:
            st.header("🔍 Barbaadi fi Sirreessi")
            st.info("Maqaa maamilaa barreessuun galmee isaa sirreessi ykn haqi.")

        q = st.text_input("🔍 Maqaa Abbaa Dhimmaa Barbaadi...", placeholder="Fkn: Alii Mohammed")
        
        if q and not df.empty:
            res = df[df['Maqaa_Abbaa_Dhimmaa'].str.contains(q, case=False, na=False)]
            if not res.empty:
                st.write(f"🔎 Bu'aa {len(res)} argaman:")
                for idx, row in res.iterrows():
                    with st.expander(f"📄 {row['Maqaa_Abbaa_Dhimmaa']} ({row['Guyyaa']})"):
                        c1, c2 = st.columns(2)
                        n_n = c1.text_input("Maqaa Sirreessi", row['Maqaa_Abbaa_Dhimmaa'], key=f"n_{idx}")
                        n_f = c2.number_input("Kafaltii (ETB)", float(row['Kafaltii_Taj']), key=f"f_{idx}")
                        ca1, ca2, _ = st.columns([1, 1, 2])
                        if ca1.button("💾 Update", key=f"u_{idx}"):
                            df.at[idx, 'Maqaa_Abbaa_Dhimmaa'] = n_n
                            df.at[idx, 'Kafaltii_Taj'] = n_f
                            save_data(df); st.success("✅ Sirreeffameera!"); st.rerun()
                        if ca2.button("🗑 Haqi", key=f"d_{idx}"):
                            df = df.drop(idx); save_data(df); st.rerun()
            else:
                st.error("Maqaan kun galmee keessa hin jiru!")

    elif menu == "Ba'i":
        st.session_state.logged_in = False
        st.rerun()
