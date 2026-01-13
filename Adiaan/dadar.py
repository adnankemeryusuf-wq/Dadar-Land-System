# --- 3. GABAASA BAL'AA ( Kutaa Calalii Fooyya'aa ) ---
    elif menu == "📈 Gabaasa Bal'aa":
        st.markdown("<h2 style='color: #1b5e20;'>📈 Gabaasa fi Calalii</h2>", unsafe_allow_html=True)
        
        if not df.empty:
            # Bakka Calalii (Filter Section)
            st.markdown("### 🔍 Calaltuu Filadhu")
            
            # 1. Gosa Gabaasaa
            f_type = st.selectbox("Gosa Gabaasaa:", ["Waliigala", "Waggaa", "Kurmaana", "Ji'a", "Torbee", "Guyyaa Addaa"])
            
            filtered_df = df.copy()
            
            # 2. Waggaa (Hundafuu ni barbaachisa)
            if f_type != "Waliigala" and f_type != "Guyyaa Addaa":
                sel_y = st.selectbox("Waggaa Filadhu:", sorted(df['Waggaa'].unique(), reverse=True))
                filtered_df = filtered_df[filtered_df['Waggaa'] == sel_y]

            # 3. Filannoo Kurmaanaa (Bifa Barawaan/Horizontal)
            if f_type == "Kurmaana":
                st.write("---")
                st.markdown("**Kurmaana (Q) Filadhu:**")
                # Filannoo Q1-Q4 bifa barawaan (Horizontal)
                q_labels = {1: "Kurmaana 1ffaa (Ful-Mud)", 2: "Kurmaana 2ffaa (Amj-Bit)", 
                            3: "Kurmaana 3ffaa (Eeb-Wax)", 4: "Kurmaana 4ffaa (Ado-Hag)"}
                
                sel_q = st.radio(
                    "Kurmaana:", 
                    options=[1, 2, 3, 4], 
                    format_func=lambda x: q_labels[x],
                    horizontal=True
                )
                filtered_df = filtered_df[filtered_df['Kurmaana'] == sel_q]

            # 4. Filannoo Ji'aa
            elif f_type == "Ji'a":
                sel_m = st.selectbox("Ji'a Filadhu:", MONTH_ORDER)
                filtered_df = filtered_df[filtered_df['Ji\'a'] == sel_m]

            # 5. Filannoo Torbee
            elif f_type == "Torbee":
                sel_m = st.selectbox("Ji'a Filadhu:", MONTH_ORDER)
                sel_w = st.select_slider("Torbee Filadhu:", options=[1, 2, 3, 4])
                filtered_df = filtered_df[(filtered_df['Ji\'a'] == sel_m) & (filtered_df['Torbee'] == sel_w)]

            # 6. Guyyaa Addaa
            elif f_type == "Guyyaa Addaa":
                sel_d = st.date_input("Guyyaa Filadhu:")
                filtered_df = filtered_df[filtered_df['Guyyaa'] == sel_d.strftime('%d/%m/%Y')]

            # --- AGARSIISA BU'AA ---
            st.divider()
            st.markdown(f"**Gabaasa {f_type}**")
            st.dataframe(filtered_df[COL_NAMES], use_container_width=True)
            
            t_f = filtered_df['Kafaltii_Taj'].sum()
            c_f = len(filtered_df)
            
            col_res1, col_res2 = st.columns(2)
            col_res1.metric("💰 Waliigala Galii", f"{t_f:,.2f} ETB")
            col_res2.metric("👥 Baay'ina Tajaajilamtootaa", f"{c_f}")

            # Download Button
            buf = io.BytesIO()
            with pd.ExcelWriter(buf, engine='xlsxwriter') as wr:
                filtered_df[COL_NAMES].to_excel(wr, index=False)
            st.download_button("📥 Excel-iin Download godhu", buf.getvalue(), f"Gabaasa_{f_type}.xlsx")
            
        else:
            st.warning("Data'n galmeeffame hin jiru.")
