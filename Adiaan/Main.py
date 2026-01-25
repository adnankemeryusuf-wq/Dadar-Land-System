elif menu == "📝 Galmee Haaraa":
        st.header("📝 Galmee Tajaajilaa Guutuu")
        
        # Tajaajiloota hunda iddoo tokkotti (Dropdown menu)
        TAJAAJILA_HUNDA = [
            "Gibira Baaxii Gooroo", "Gibira Lafa Qonnaa", "Gibira Manaa",
            "Kaffaltii Liizii Waggaa", "Kaffaltii Liizii Duraa", "Kaffaltii Kiiraa Manaa",
            "TOT (Turnover Tax)", "Jijjiirraa Maqaa (Gift/Sale)",
            "Kaartaa Haaraa (Liizii)", "Kaartaa Haaraa (Kiiraa)", "Kaartaa Bakka Bu'aa",
            "Kaartaa Kadastaaraa", "Sirreeffama Daangaa", "Kaartaa Lafa Qonnaa",
            "Pilaanii Magaalaa", "Itti Fayyadama Lafaa (Land Use)", "Humna Mahandisummaa",
            "Ugura Mana Murtii", "Ugura Kaasuu", "Waliigaltee Liqii Baankii",
            "Waliigaltee Hiikuu", "Dhimma Dhala (Inheritance)",
            "Waraqaa Ragaa (Clearance)", "Deebii Iyyannoo",
            "Adabbii Ijaarsa Seeraan Alaa", "Kaffaltii Seeressuu (Regularization)", 
            "Adabbii Faallaa Pilaanii"
        ]

        with st.form("galmee_guutuu", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                m_maqaa = st.text_input("👤 Maqaa Maamilaa")
                m_ara = st.text_input("📍 Araddaa")
            with col2:
                m_qaxana = st.text_input("🧭 Qaxana")
                m_ogeessa = st.text_input("👷 Maqaa Ogeessaa")

            st.markdown("---")
            # Tajaajila hunda bakka tokkotti filachuuf
            t_filatame = st.selectbox("🎯 Tajaajila Barbaadame Filadhu", TAJAAJILA_HUNDA)
            
            m_fee = st.number_input("💸 Kaffaltii Tajaajilaa (ETB)", min_value=0.0, step=10.0)
            
            submit = st.form_submit_button("💾 GALMEESSI")

            if submit:
                if m_maqaa and t_filatame:
                    curr_date = datetime.now().strftime('%d/%m/%Y')
                    
                    # Data galmeessuu
                    new_entry = [curr_date, m_maqaa, m_ara, m_qaxana, t_filatame, m_ogeessa, m_fee]
                    df = load_data(DATA_FILE, COL_NAMES)
                    df = pd.concat([df, pd.DataFrame([new_entry], columns=COL_NAMES)], ignore_index=True)
                    save_data(df, DATA_FILE)
                    
                    # Nagahee uumuu
                    receipt_meta = {"guyyaa": curr_date, "maqaa": m_maqaa, "total": m_fee, "ogeessa": m_ogeessa}
                    item_dict = {t_filatame: m_fee}
                    pdf_bytes = create_itemized_receipt(receipt_meta, item_dict)
                    
                    st.success(f"✅ Tajaajilli '{t_filatame}' maamila {m_maqaa}f galmaa'eera!")
                    st.download_button("📥 Nagahee Buufadhu", pdf_bytes, f"Nagahee_{m_maqaa}.pdf")
                else:
                    st.error("Maaloo, maqaa maamilaa galchi!")
