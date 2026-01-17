# ================= 3. MAIN APP =================
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    _, col_mid, _ = st.columns([1, 1.2, 1])
    with col_mid:
        st.markdown("<h2 style='text-align:center;'>🏢 Deder Land Login</h2>", unsafe_allow_html=True)
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")
        if st.button("Seeni"):
            if u == "DAD" and p == "2026":
                st.session_state.logged_in = True
                st.rerun()
            else: st.error("Maqaa ykn Password dogoggora!")
else:
    df = load_data()
    menu = st.sidebar.radio("FILANNOO", ["📊 Dashboard", "📝 Galmee Haaraa", "📈 Gabaasa Bal'aa", "🔍 Barbaadi/Edit"])

    if menu == "📊 Dashboard":
        st.header("📊 Dashboard Waliigalaa")
        if not df.empty:
            c1, c2, c3 = st.columns(3)
            c1.markdown(f"<div class='card'><p>💰 Galii Waliigalaa</p><p class='metric-value'>{df['Kafaltii_Taj'].sum():,.2f} ETB</p></div>", unsafe_allow_html=True)
            c2.markdown(f"<div class='card'><p>👥 Maamiltoota</p><p class='metric-value'>{len(df)}</p></div>", unsafe_allow_html=True)
            top_og = df['Maqaa_Ogeessa'].mode()[0] if not df.empty else "-"
            c3.markdown(f"<div class='card'><p>🏆 Ogeessa Cimaa</p><p class='metric-value'>{top_og}</p></div>", unsafe_allow_html=True)
            st.area_chart(df.groupby('Ji\'a')['Kafaltii_Taj'].sum().reindex(MONTH_ORDER).fillna(0))

    elif menu == "📝 Galmee Haaraa":
        st.header("📝 Galmee Tajaajilaa")
        GATII_DICT = {"Gibira": ["Gibira Lafa Qonnaa", "Gibira Manaa"], "Liizii": ["Liizii Waggaa", "Jijjiirraa Maqaa", "TOT"]}
        
        with st.form("entry_form"):
            maqaa = st.text_input("Maqaa Abbaa Dhimmaa")
            ara = st.text_input("Araddaa")
            qax = st.text_input("Qaxana")
            ogeessa = st.text_input("Maqaa Ogeessaa")
            gosa = st.multiselect("Gosa Tajaajilaa", sum(GATII_DICT.values(), []))
            kaffaltii = st.number_input("Kaffaltii (ETB)", min_value=0.0)
            
            if st.form_submit_button("💾 Galmeessi"):
                if maqaa and ogeessa:
                    new_row = [datetime.now().strftime('%d/%m/%Y'), maqaa, ara, qax, ", ".join(gosa), ogeessa, kaffaltii]
                    df = pd.concat([df, pd.DataFrame([new_row], columns=COL_NAMES)], ignore_index=True)
                    save_data(df)
                    st.success("Galmeeffameera!")

    elif menu == "📈 Gabaasa Bal'aa":
        st.header("📈 Gabaasa Bal'aa")
        if not df.empty:
            f_type = st.selectbox("Calali:", ["Waliigala", "Waggaa", "Ji'a"])
            filtered = df.copy() # Calala dabalataa asitti galchuun ni danda'ama
            
            # Export Buttons
            st.subheader("📥 Gabaasa Buufadhu")
            ex1, ex2, ex3 = st.columns(3)
            
            # Excel
            buf_ex = io.BytesIO()
            with pd.ExcelWriter(buf_ex, engine='xlsxwriter') as writer:
                filtered[COL_NAMES].to_excel(writer, index=False)
            ex1.download_button("📊 Excel Buusi", buf_ex.getvalue(), "Gabaasa.xlsx")
            
            # PPT
            ppt_file = create_ppt_report(filtered, f_type)
            ex2.download_button("🖥️ PPT Buusi", ppt_file, "Gabaasa.pptx")
            
            st.dataframe(filtered[COL_NAMES], use_container_width=True)

    if st.sidebar.button("Log Out"):
        st.session_state.logged_in = False
        st.rerun()
