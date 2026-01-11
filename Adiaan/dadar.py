import streamlit as st

# --- SIDEBAR MENU ---
# Filannoo kana dura qopheessuu qabda
with st.sidebar:
    st.title("Wajjira Lafaa Dadar")
    menu = st.sidebar.selectbox(
        "Filannoo",
        ["🏠 Dashboard", "📝 Galmee Haaraa", "✅ Dhimma Xumurame", "📊 Gabaasa Excel"]
    )

# --- MENU SELECTION LOGIC ---
if menu == "🏠 Dashboard":
    st.subheader("🏠 Dashboard Waliigalaa")
    # Dashboard koodii kee as jala galchi...

elif menu == "📝 Galmee Haaraa":
    st.subheader("📝 Galmee Abbaa Dhimmaa")
    # Koodii galmee asitti dabali...
