import streamlit as st
import pandas as pd
import os
from datetime import datetime

# ================= CONFIG =================
st.set_page_config("Dadar Land Admin Pro", page_icon="🏢", layout="wide")

DATA_FILE = "dadar_data.txt"
COLS = ["Guyyaa", "Maqaa_Abbaa_Dhimmaa", "Araddaa", "Qaxana", "Gosa_Tajaajilaa", "Ogeessa", "Kafaltii"]

# ================= FUNCTIONS =================
def load_data():
    if not os.path.exists(DATA_FILE):
        return pd.DataFrame(columns=COLS)
    return pd.read_csv(DATA_FILE, sep="|", names=COLS)

def save_data(df):
    df.to_csv(DATA_FILE, sep="|", index=False, header=False)

# ================= LOGIN =================
if "login" not in st.session_state:
    st.session_state.login = False

if not st.session_state.login:
    st.title("🔐 Admin Login")
    u = st.text_input("Username")
    p = st.text_input("Password", type="password")

    if st.button("Seeni"):
        if u == "admin" and p == "123":
            st.session_state.login = True
            st.rerun()
        else:
            st.error("❌ Username ykn Password dogoggora")

    st.stop()

# ================= MAIN APP =================
df = load_data()

with st.sidebar:
    st.title("🏢 Dadar Admin")
    menu = st.radio("MENU", ["📊 Dashboard", "📝 Galmee Haaraa", "📈 Gabaasa", "🚪 Ba'i"])

# ================= DASHBOARD =================
if menu == "📊 Dashboard":
    st.header("📊 Dashboard")

    if df.empty:
        st.info("Galmeen hin jiru.")
    else:
        c1, c2, c3 = st.columns(3)
        c1.metric("💰 Galii Waliigalaa", f"{df['Kafaltii'].sum():,.2f} ETB")
        c2.metric("👥 Maamiltoota", len(df))
        c3.metric("👷 Ogeeyyii", df['Ogeessa'].nunique())

        df["Date"] = pd.to_datetime(df["Guyyaa"], format="%d/%m/%Y")
        daily = df.groupby("Date")["Kafaltii"].sum()

        st.subheader("📈 Galii Guyyaa")
        st.line_chart(daily)

# ================= REGISTRATION =================
elif menu == "📝 Galmee Haaraa":
    st.header("📝 Galmee Tajaajilaa")

    with st.form("reg"):
        c1, c2 = st.columns(2)
        name = c1.text_input("Maqaa Abbaa Dhimmaa")
        ara = c2.text_input("Araddaa")
        qax = c1.text_input("Qaxana")
        service = c2.text_input("Gosa Tajaajilaa")
        ogeessa = c1.text_input("Maqaa Ogeessaa")
        fee = c2.number_input("Kafaltii (ETB)", min_value=0.0)

        if st.form_submit_button("💾 Galmeessi"):
            if name and service and ogeessa:
                new_row = [
                    datetime.now().strftime("%d/%m/%Y"),
                    name, ara, qax, service, ogeessa, fee
                ]
                df = pd.concat([df, pd.DataFrame([new_row], columns=COLS)], ignore_index=True)
                save_data(df)
                st.success("✅ Galmeeffameera!")
            else:
                st.error("⚠ Odeeffannoo guutuu galchi!")

# ================= REPORT =================
elif menu == "📈 Gabaasa":
    st.header("📈 Gabaasa Guutuu")

    if df.empty:
        st.warning("Data hin jiru.")
    else:
        st.dataframe(df, use_container_width=True)

        total = df["Kafaltii"].sum()
        st.metric("💰 Galii Waliigalaa", f"{total:,.2f} ETB")

        excel = df.to_csv(index=False).encode("utf-8")
        st.download_button(
            "📥 Excel Buusi",
            excel,
            "Dadar_Gabaasa.csv",
            "text/csv"
        )

# ================= LOGOUT =================
elif menu == "🚪 Ba'i":
    st.session_state.login = False
    st.rerun()
