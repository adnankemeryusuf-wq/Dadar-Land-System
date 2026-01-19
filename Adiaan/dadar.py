elif menu == "📝 Galmee Haaraa":
    st.header("📝 Galmee Tajaajilaa Haaraa")
    
    # 1. Session State qopheessu (Akka Download Button hin badneef)
    if 'show_download' not in st.session_state:
        st.session_state.show_download = False
    if 'pdf_data' not in st.session_state:
        st.session_state.pdf_data = None
    if 'pdf_filename' not in st.session_state:
        st.session_state.pdf_filename = ""

    GATII_DICT = {
        "🏷️ Gibira & Kaffaltii": ["Gibira Baaxii Gooroo", "Gibira Lafa Qonnaa", "Kaffaltii Liizii Waggaa", "Kaffaltii Liizii Duraa", "TOT (Turnover Tax)"],
        "📜 Kaartaa & Qabiyyee": ["Kaartaa Haaraa", "Kaartaa Bakka Bu'aa", "Kaartaa Kadastaaraa", "Jijjiirraa Maqaa (Gift/Sale)", "Sirreeffama Daangaa", "Ganda Irraa gara Magaalaatti"],
        "🏗️ Pilaanii & Ijaarsa": ["Pilaanii Magaalaa", "Itti Fayyadama Lafaa (Land Use)", "Humna Mahandisummaa"],
        "⚖️ Dhimma Seeraa": ["Ugura Mana Murtii", "Ugura Kaasuu", "Waliigaltee Liqii Baankii", "Waliigaltee Hiikuu", "Dhimma Dhala (Inheritance)"],
        "📂 Tajaajila Biroo": ["Waraqaa Ragaa (Clearance)", "Deebii Iyyannoo"]
    }
    
    selected_cats = st.multiselect("🟢 Gosa Tajaajilaa Filadhu", list(GATII_DICT.keys()))
    details, d_fees = [], {}
    
    for cat in selected_cats:
        with st.expander(f"Kaffaltii {cat}", expanded=True):
            subs = st.multiselect(f"Tajaajiloota {cat}:", GATII_DICT[cat], key=cat)
            for s in subs:
                details.append(f"{s}")
                d_fees[f"{cat}_{s}"] = st.number_input(f"Kaffaltii {s}", min_value=0.0, key=f"f_{s}")

    st.divider()

    with st.form("main_form", clear_on_submit=True):
        st.subheader("Odeeffannoo Maamilaa")
        c1, c2 = st.columns(2)
        m_maqaa = c1.text_input("Maqaa Maamilaa *")
        m_araddaa = c2.text_input("Araddaa *")
        m_qaxana = c1.text_input("Qaxana")
        m_nagahee_lakk = c2.text_input("Lakk. Nagahee (Receipt No.) *")
        m_ogeessa = c1.text_input("Ogeessa Raawwate *")
        nagahee_file = st.file_uploader("Nagahee Scan", type=['jpg','png','jpeg'])
        
        submit = st.form_submit_button("💾 Galmeessi fi Kuusi")
        
        if submit:
            if m_maqaa and m_araddaa and m_nagahee_lakk and details:
                kafallti_hunda = sum(d_fees.values())
                new_row = [datetime.now().strftime('%d/%m/%Y'), m_maqaa, m_araddaa, m_qaxana, ", ".join(details), m_ogeessa, kafallti_hunda]
                df = pd.concat([df, pd.DataFrame([new_row], columns=COL_NAMES)], ignore_index=True)
                save_data(df)
                st.success(f"✅ Galmeen {m_maqaa} milkaa'eera!")
                
                # Clearance yoo jiraate Session State irratti save godhi
                if "Waraqaa Ragaa (Clearance)" in details:
                    st.session_state.pdf_data = create_clearance_pdf(m_maqaa, m_araddaa, m_qaxana, ", ".join(details), m_nagahee_lakk)
                    st.session_state.pdf_filename = f"Clearance_{m_maqaa.replace(' ', '_')}.pdf"
                    st.session_state.show_download = True
                else:
                    st.session_state.show_download = False
            else:
                st.error("⚠️ Maaloo hunda guuti!")
                st.session_state.show_download = False

    # 2. Form-ii alatti Download Button fiduu (Refresh yoo ta'ellee akka hin badneef)
    if st.session_state.show_download:
        st.info("📄 Waraqaan Ragaa (Clearance) Maamila kanaaf qophaa'eera.")
        st.download_button(
            label="📥 Waraqaa Ragaa (Clearance) Download Godhuuf As Cuqaasi",
            data=st.session_state.pdf_data,
            file_name=st.session_state.pdf_filename,
            mime="application/pdf",
            key="final_dl_btn"
        )
        # Erga download godhamee booda akka badu yoo barbaadde:
        # st.session_state.show_download = False
