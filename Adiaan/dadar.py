# --- 5. MENU SELECTION LOGIC ---
# Mallattoon if, elif, fi else sarara tokkorra (same level) jiraachuu qabu

if menu == "🏠 Dashboard":
    st.subheader("🏠 Dashboard Waliigalaa")
    # Dashboard koodii kee as jala galchi...

elif menu == "📝 Galmee Haaraa":  # Amma sarara (indentation) sirrii qaba
    st.subheader("📝 Galmee Abbaa Dhimmaa Galchi")
    with st.form("RegForm", clear_on_submit=True):
        # ... koodii form keetii hunda ...
        submitted = st.form_submit_button("✅ GALMEESSI")
        if submitted:
            st.success("Galmeeffameera!")

elif menu == "📊 Gabaasa":
    st.subheader("📊 Gabaasa Waliigalaa")
    # Gabaasa koodii kee as jala galchi...
