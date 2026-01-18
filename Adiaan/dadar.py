import streamlit as st

# Sidebar Filannoo
with st.sidebar:
    st.header("⚙️ Qindaa'ina")
    # Uploaders asitti ta'u
    menu = st.radio("FILANNOO", ["📝 Galmee & Clearance", "📊 Dashboard", "📈 Gabaasa"])

# 1. Kutaa Galmee
if menu == "📝 Galmee & Clearance":
    st.subheader("Galmee Tajaajilaa")
    # Form-ii kee asitti barreeffama...

# 2. Kutaa Dashboard
elif menu == "📊 Dashboard":
    st.subheader("Statistiksii Waajjiraa")
    # Metric-oota asitti agarsiisama...

# 3. Kutaa Gabaasa
elif menu == "📈 Gabaasa":
    st.subheader("Gabatee Gabaasaa")
    # Dataframe asitti agarsiisama...
