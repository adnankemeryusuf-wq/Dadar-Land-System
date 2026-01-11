# --- GALMEE HAARAA ---
    elif menu == "📝 Galmee Haaraa":
        with st.form("RegForm", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                ad = st.text_input("Maqaa Abbaa Dhimmaa")
                bad = st.text_input("Bilbila AD (09...)")
                ar = st.text_input("Araddaa")
                wi = st.text_input("Wirtuu")
            with col2:
                gs = st.selectbox("Gosa Tajaajilaa", ["Kartaa", "Lizi", "Jijjiirraa Maqaa", "Safara", "Gibira"])
                og = st.text_input("Maqaa Ogeessaa")
                bog = st.text_input("Bilbila Ogeessaa")
                beellama = st.text_input("Guyyaa & Sa'aatii Beellamaa (Fkn: 2026-02-10 09:00)")

            st.write("💰 **Kafaltiiwwan**")
            k1, k2, k3 = st.columns(3)
            v_kartaa = k1.number_input("Kafaltii Kartaa", value=0.0)
            v_lizi = k2.number_input("Kafaltii Lizi", value=0.0)
            v_tot = k3.number_input("TOT/Gibira", value=0.0)

            # --- MALLATTOO SUBMIT (KUN DOGOGGORA SANA SIRREESSA) ---
            submitted = st.form_submit_button("✅ GALMEESSI FI SMS ERGI")

            if submitted:
                if ad and bad:
                    total = v_kartaa + v_lizi + v_tot
                    now_s = datetime.now().strftime("%Y-%m-%d %H:%M")
                    # Ragaa walitti qabnee galmeessina (Format File keetii eeguun)
                    new_line = f"{now_s}|{ad}|{ar}|{wi}|{bad}|{gs}|{og}|{bog}|{beellama}|{v_kartaa}|{v_lizi}|{v_tot}|{total}\n"
                    
                    with open(DATA_FILE, "a", encoding="utf-8") as f:
                        f.write(new_line)
                    
                    # SMS Erguu
                    msg_ad = f"Kabajamaa {ad}, tajaajila {gs}af galmeeffamtaniittu. Beellama: {beellama}. Dadar Land."
                    send_sms(bad, msg_ad)
                    
                    if bog: # Ogeessaafis SMS yoo jiraate
                        msg_og = f"Ogeessa {og}, mamiila {ad} safaruuf beellama qabdu."
                        send_sms(bog, msg_og)

                    st.success(f"Galmeen {ad} milkiin xumurameera! SMS ergameera.")
                    st.balloons()
                else:
                    st.error("Maaloo maqaa fi bilbila abbaa dhimmaa galchi!")

