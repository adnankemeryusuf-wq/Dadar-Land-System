elif choice == "📝 Galmee Haaraa":
        st.subheader("📝 Galmee Abbaa Dhimmaa")
        with st.form("galmee_form"):
            c1, c2 = st.columns(2)
            maqaa = c1.text_input("Maqaa Abbaa Dhimmaa")
            bilbila = c1.text_input("Lakk. Bilbilaa")
            tajaajila = c2.selectbox("Gosa Tajaajilaa", ["Kartaa", "Jijjiirraa Maqaa", "Lizio", "Gibira"])
            ogeessa = c2.text_input("Maqaa Ogeessaa")
            
            if st.form_submit_button("Galmeessi"):
                if maqaa and bilbila:
                    # --- RAGAA FILII KEESSATTI KUUSUU ---
                    now_str = datetime.now().strftime("%Y-%m-%d %H:%M")
                    eth_date = to_ethiopian(datetime.now())
                    line = f"{now_str}|{eth_date}|{maqaa}|{bilbila}|{tajaajila}|{ogeessa}\n"
                    
                    with open(DATA_FILE, "a", encoding="utf-8") as f:
                        f.write(line)
                    
                    st.success(f"{maqaa} galmeeffameera! (File irratti ol-ka'eera)")
                    st.balloons()
                else: 
                    st.warning("Maaloo, odeeffannoo guutuu galchi!")
