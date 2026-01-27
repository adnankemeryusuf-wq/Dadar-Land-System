import streamlit as st
import pandas as pd
import os, io, requests, base64
from datetime import datetime
from fpdf import FPDF

# ================= 1. CONFIGURATION & STYLE =================
LOGO_PATH = "Adiaan/logo.png"
DATA_FILE = "dadar_final_report.txt"
NAGAHEE_DIR = "Adiaan/nagahee"
BOT_TOKEN = "8357193631:AAHCuSnXzjZTQaglkmcS0gq-EvqnkIQLDBI"
CHAT_ID_MANAGER = "7329587700"

if not os.path.exists(NAGAHEE_DIR): os.makedirs(NAGAHEE_DIR, exist_ok=True)

# --- CORE FUNCTIONS ---
COL_NAMES = ['Guyyaa', 'Maqaa_Abbaa_Dhimmaa', 'Araddaa', 'Qaxana', 'Gosa_Tajajjilaa', 'Maqaa_Ogeessa', 'Kafaltii_Taj']
MONTH_ORDER = ["Fulbaana", "Onkololeessa", "Sadaasa", "Muddee", "Amajjii", "Guraandhala", "Bitootessa", "Eebila", "Caamsaa", "Waxabajjii", "Adooleessa", "Hagayya"]
MONTH_MAP = {9: "Fulbaana", 10: "Onkololeessa", 11: "Sadaasa", 12: "Muddee", 1: "Amajjii", 2: "Guraandhala", 3: "Bitootessa", 4: "Eebila", 5: "Caamsaa", 6: "Waxabajjii", 7: "Adooleessa", 8: "Hagayya"}

def save_data(df_to_save):
    df_to_save[COL_NAMES].to_csv(DATA_FILE, sep="|", index=False, header=False, encoding="utf-8")
    return True

def load_data():
    if not os.path.exists(DATA_FILE) or os.stat(DATA_FILE).st_size == 0:
        return pd.DataFrame(columns=COL_NAMES)
    df = pd.read_csv(DATA_FILE, sep="|", names=COL_NAMES, header=None, encoding='utf-8')
    df['Date_Obj'] = pd.to_datetime(df['Guyyaa'], format='%d/%m/%Y')
    df['Ji\'a'] = df['Date_Obj'].dt.month.map(MONTH_MAP)
    return df

# --- EXCEL TELEGRAM FORMATTED ---
def send_excel_to_telegram(df_to_send):
    try:
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df_to_send[COL_NAMES].to_excel(writer, index=False, sheet_name='Gabaasa')
            workbook, worksheet = writer.book, writer.sheets['Gabaasa']
            header_f = workbook.add_format({'bold':True,'bg_color':'#2E7D32','font_color':'white','border':1})
            for col_num, value in enumerate(df_to_send[COL_NAMES].columns.values):
                worksheet.write(0, col_num, value, header_f)
                worksheet.set_column(col_num, col_num, 20)
        output.seek(0)
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendDocument"
        files = {'document': ('Gabaasa_Dadar_Formatted.xlsx', output)}
        cap = f"📊 **Gabaasa Dadar**\n💰 Galii: {df_to_send['Kafaltii_Taj'].sum():,.2f}\n👥 Maamila: {len(df_to_send)}"
        requests.post(url, data={'chat_id': CHAT_ID_MANAGER, 'caption': cap, 'parse_mode':'Markdown'}, files=files)
        return True
    except: return False

def create_advanced_pdf(name, count, rank, logo_l=None, logo_r=None):
    pdf = FPDF(orientation='L', unit='mm', format='A4')
    pdf.add_page()
    colors = {1: (255, 215, 0), 2: (192, 192, 192), 3: (205, 127, 50)}
    pdf.set_draw_color(*colors.get(rank, (0,0,0))); pdf.set_line_width(3); pdf.rect(10, 10, 277, 190)
    if logo_l: pdf.image(logo_l, 15, 15, 30)
    if logo_r: pdf.image(logo_r, 252, 15, 30)
    pdf.set_y(60); pdf.set_font('Arial','B',30); pdf.cell(0,15,"SARTIIFIKETA BEEKAMTII",0,1,'C')
    pdf.set_font('Arial','',20); pdf.ln(10)
    pdf.multi_cell(0,12,f"Obbo/Adde {name.upper()}\n\nTajaajilamtoota {count} tajaajiluun sadarkaa {rank}ffaa\nwaggaa 2026 qabachuun keessaniif ragaa kenname.",0,'C')
    return pdf.output(dest='S').encode('latin-1')

# ================= 3. MAIN UI =================
st.set_page_config(page_title="Dadar Land", layout="wide")
df = load_data()
menu = st.sidebar.radio("FILANNOO", ["📊 Dashboard", "📝 Galmee Haaraa", "📈 Gabaasa Bal'aa", "🏆 Badhaasa", "🔍 Barbaadi"])

if menu == "📊 Dashboard":
    st.title("📊 Dashboard")
    if not df.empty:
        c1, c2, c3 = st.columns(3)
        c1.metric("💰 Galii Hunda", f"{df['Kafaltii_Taj'].sum():,.2f} ETB")
        c2.metric("👥 Maamiltoota", len(df))
        c3.metric("👷 Ogeeyyii", df['Maqaa_Ogeessa'].nunique())
        st.area_chart(df.groupby('Ji\'a')['Kafaltii_Taj'].sum().reindex(MONTH_ORDER))

elif menu == "📝 Galmee Haaraa":
    st.header("📝 Galmee Tajaajilaa")
    GATII_DICT = {
        "Gibira": ["Gibira Baaxii Gooroo", "Gibira Lafa Qonnaa", "Gibira Manaa"],
        "Liizii": ["Liizii Waggaa", "Jijjiirraa Maqaa", "Kafaltii Liizii Duraa"],
        "Kaartaa": ["Kaartaa Lafa", "Kaartaa Kadastaara", "Kaartaa Lafa Qonnaa"]
    }
    selected_main = st.multiselect("🟢 Gosa Tajaajilaa", list(GATII_DICT.keys()))
    details, d_fees = [], {}
    if selected_main:
        for g in selected_main:
            subs = st.multiselect(f"Tajaajila {g}:", GATII_DICT[g])
            for s in subs:
                details.append(f"{g}({s})")
                d_fees[f"{g}_{s}"] = st.number_input(f"Kafaltii {s}", min_value=0.0)

    with st.form("entry"):
        c1, c2 = st.columns(2)
        maqaa = c1.text_input("Maqaa Abbaa Dhimmaa *")
        ara = c2.text_input("Araddaa *")
        qax = c1.text_input("Qaxana *")
        ogeessa = c2.text_input("Maqaa Ogeessaa *")
        if st.form_submit_button("💾 Galmeessi"):
            new_row = [datetime.now().strftime('%d/%m/%Y'), maqaa, ara, qax, ", ".join(details), ogeessa, sum(d_fees.values())]
            df = pd.concat([df, pd.DataFrame([new_row], columns=COL_NAMES)])
            save_data(df); st.success("Galmeeffameera!")

elif menu == "📈 Gabaasa Bal'aa":
    st.header("📈 Gabaasa Kurmaanaa fi Torbee")
    if not df.empty:
        df['Kurmaana'] = df['Date_Obj'].dt.month.apply(lambda x: f"Kurmaana {(x-1)//3 + 1}ffaa")
        st.write("### Gabaasa Kurmaanaan")
        st.bar_chart(df.groupby('Kurmaana')['Kafaltii_Taj'].sum())
        
        if st.button("🚀 Excel Gara Telegram-itti Ergi"):
            if send_excel_to_telegram(df): st.success("Gara Telegram-itti ergameera!")
        st.dataframe(df[COL_NAMES])

elif menu == "🏆 Badhaasa":
    st.header("🏆 Badhaasa Ogeeyyii")
    l_l = st.file_uploader("Logo Bitaa")
    l_r = st.file_uploader("Logo Mirgaa")
    if not df.empty:
        top_3 = df['Maqaa_Ogeessa'].value_counts().head(3)
        cols = st.columns(3)
        for i, (name, count) in enumerate(top_3.items()):
            with cols[i]:
                st.subheader(f"#{i+1} {name}")
                pdf = create_advanced_pdf(name, count, i+1, l_l, l_r)
                st.download_button(f"Sartifiikeeta {i+1}", pdf, f"{name}.pdf")
