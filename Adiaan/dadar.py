import streamlit as st
import pandas as pd
import os, io, requests
from datetime import datetime
from fpdf import FPDF

# ================= CONFIG =================
DATA_FILE = "dadar_data.csv"
LOGO_PATH = "Adiaan/logo.png"

COLS = [
    "Guyyaa", "Maqaa_Abbaa_Dhimmaa", "Araddaa", "Qaxana",
    "Gosa_Tajaajilaa", "Maqaa_Ogeessa", "Kafaltii_Taj"
]

MONTH_MAP = {
    1:"Amajjii",2:"Guraandhala",3:"Bitootessa",4:"Eebila",
    5:"Caamsaa",6:"Waxabajjii",7:"Adooleessa",8:"Hagayya",
    9:"Fulbaana",10:"Onkololeessa",11:"Sadaasa",12:"Muddee"
}

# ================= PAGE =================
st.set_page_config(
    page_title="Dadar Land Office",
    page_icon="🏢",
    layout="wide"
)

# ================= UTILITIES =================
def load_data():
    if not os.path.exists(DATA_FILE):
        return pd.DataFrame(columns=COLS)
    df = pd.read_csv(DATA_FILE)
    df["Date"] = pd.to_datetime(df["Guyyaa"], format="%d/%m/%Y")
    df["Ji'a"] = df["Date"].dt.month.map(MONTH_MAP)
    df["Waggaa"] = df["Date"].dt.year
    return df

def save_data(df):
    df[COLS].to_csv(DATA_FILE, index=False)

def send_telegram(file_data, file_name, caption):
    url = f"https://api.telegram.org/bot{st.secrets['BOT_TOKEN']}/sendDocument"
    files = {"document": (file_name, file_data)}
    data = {"chat_id": st.secrets["CHAT_ID"], "caption": caption}
    requests.post(url, files=files, data=data)

# ================= LOGIN =================
if "login" not in st.session_state:
    st.session_state.login = False

if not st.session_state.login:
    st.title("🔐 Login")
    u = st.text_input("Username")
    p = st.text_input("Password", type="password")
    if st.button("Seeni"):
        if u == st.secrets["USERNAME"] and p == st.secrets["PASSWORD"]:
            st.session_state.login = True
            st.rerun()
        else:
            st.error("Dogoggora!")

# ================= MAIN APP =================
else:
    df = load_data()

    with st.sidebar:
        if os.path.exists(LOGO_PATH):
            st.image(LOGO_PATH, width=100)
        menu = st.radio("MENU", [
            "📊 Dashboard",
            "📝 Galmee Haaraa",
            "📈 Gabaasa",
            "🔍 Barbaadi/Edit",
            "🚪 Ba'i"
        ])

    # ========== DASHBOARD ==========
    if menu == "📊 Dashboard":
        st.header("📊 Dashboard")
        if df.empty:
            st.info("Data hin jiru")
        else:
            c1, c2, c3 = st.columns(3)
            c1.metric("💰 Galii", f"{df['Kafaltii_Taj'].sum():,.2f} ETB")
            c2.metric("👥 Maamiltoota", len(df))
            c3.metric("🏆 Ogeessa", df["Maqaa_Ogeessa"].mode()[0])

            st.area_chart(
                df.groupby("Ji'a")["Kafaltii_Taj"]
                .sum()
                .reindex(MONTH_MAP.values())
                .fillna(0)
            )

    # ========== REGISTRATION ==========
    elif menu == "📝 Galmee Haaraa":
        st.header("📝 Galmee Haaraa")
        with st.form("reg"):
            maqaa = st.text_input("Maqaa Abbaa Dhimmaa")
            ara = st.text_input("Araddaa")
            qax = st.text_input("Qaxana")
            gosa = st.text_input("Gosa Tajaajilaa")
            oge = st.text_input("Maqaa Ogeessa")
            fee = st.number_input("Kafaltii (ETB)", min_value=0.0)

            if st.form_submit_button("💾 Galmeessi"):
                new = pd.DataFrame([[
                    datetime.now().strftime("%d/%m/%Y"),
                    maqaa, ara, qax, gosa, oge, fee
                ]], columns=COLS)
                df = pd.concat([df, new], ignore_index=True)
                save_data(df)
                st.success("Galmeeffameera!")
                st.rerun()

    # ========== REPORT ==========
    elif menu == "📈 Gabaasa":
        st.header("📈 Gabaasa")
        st.dataframe(df[COLS])

        buf = io.BytesIO()
        df[COLS].to_excel(buf, index=False)

        c1, c2 = st.columns(2)
        c1.download_button("📥 Excel", buf.getvalue(), "gabaasa.xlsx")
        if c2.button("✈️ Telegramitti Ergi"):
            send_telegram(buf.getvalue(), "gabaasa.xlsx", "📊 Gabaasa Dadar")
            st.success("Ergameera!")

    # ========== SEARCH ==========
    elif menu == "🔍 Barbaadi/Edit":
        q = st.text_input("Maqaa Barbaadi")
        res = df[df["Maqaa_Abbaa_Dhimmaa"].str.contains(q, case=False, na=False)]
        for i, r in res.iterrows():
            with st.expander(r["Maqaa_Abbaa_Dhimmaa"]):
                new_fee = st.number_input("Kafaltii", value=r["Kafaltii_Taj"], key=i)
                if st.button("💾 Update", key=f"u{i}"):
                    df.at[i, "Kafaltii_Taj"] = new_fee
                    save_data(df)
                    st.success("Sirreeffameera")
                    st.rerun()

    # ========== LOGOUT ==========
    elif menu == "🚪 Ba'i":
        st.session_state.login = False
        st.rerun()
