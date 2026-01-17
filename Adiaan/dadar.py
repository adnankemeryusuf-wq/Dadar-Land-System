import streamlit as st
import pandas as pd
import os
import io
import requests
from datetime import datetime
from fpdf import FPDF
import plotly.express as px
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN

# ... (Kutaa Functions kaan akkuma jirutti dhiisi) ...

# ================= 2. CORE FUNCTIONS (ADD PPT) =================
def create_ppt_report(df_filtered, report_type):
    prs = Presentation()
    
    # --- Slide 1: Title Slide ---
    title_slide_layout = prs.slide_layouts[0]
    slide = prs.slides.add_slide(title_slide_layout)
    title = slide.shapes.title
    subtitle = slide.placeholders[1]
    title.text = "Gabaasa Sochii Hojii Lafa Magaalaa"
    subtitle.text = f"Deder City Land Office\nGabaasa: {report_type}\nGuyyaa: {datetime.now().strftime('%d/%m/%Y')}"

    # --- Slide 2: Waliigala (Executive Summary) ---
    slide = prs.slides.add_slide(prs.slide_layouts[1])
    slide.shapes.title.text = "Waliigala Gabaasaa"
    tf = slide.placeholders[1].text_frame
    tf.text = f"• Waliigala Galii: {df_filtered['Kafaltii_Taj'].sum():,.2f} ETB"
    tf.add_paragraph().text = f"• Baay'ina Maamiltootaa: {len(df_filtered)}"
    tf.add_paragraph().text = f"• Ogeessa Hojii Baay'ee: {df_filtered['Maqaa_Ogeessa'].mode()[0] if not df_filtered.empty else '-'}"

    # --- Slide 3: Gabaasa Araddaalee ---
    slide = prs.slides.add_slide(prs.slide_layouts[1])
    slide.shapes.title.text = "Galii Araddaalee"
    ar_data = df_filtered.groupby('Araddaa')['Kafaltii_Taj'].sum().reset_index()
    tf = slide.placeholders[1].text_frame
    for _, row in ar_data.iterrows():
        p = tf.add_paragraph()
        p.text = f"• {row['Araddaa']}: {row['Kafaltii_Taj']:,.2f} ETB"

    # Save to buffer
    ppt_io = io.BytesIO()
    prs.save(ppt_io)
    return ppt_io.getvalue()

# ... (Kutaa Dashboard fi Registration akkuma jirutti dhiisi) ...

# ================= 3. MAIN APP (MODIFIED REPORT SECTION) =================
# Menu "📈 Gabaasa Bal'aa" jala kanaan gadii bakka buusi:

    elif menu == "📈 Gabaasa Bal'aa":
        st.markdown("<h4 style='color: #1b5e20;'>📈 Gabaasa fi Xiinxala Galii</h4>", unsafe_allow_html=True)
        
        if not df.empty:
            # --- 1. Filter Section ---
            with st.expander("🔍 Calali ykn Barbaadi", expanded=True):
                c1, c2, _ = st.columns(3)
                f_type = c1.selectbox("Gosa Gabaasaa:", ["Waliigala", "Waggaa", "Kurmaana", "Ji'a", "Guyyaa"])
                
                filtered = df.copy()
                if f_type == "Waggaa":
                    sel_y = c2.selectbox("Waggaa:", sorted(df['Waggaa'].unique(), reverse=True))
                    filtered = filtered[filtered['Waggaa'] == sel_y]
                elif f_type == "Kurmaana":
                    sel_k = c2.selectbox("Kurmaana:", [1, 2, 3, 4])
                    filtered = filtered[filtered['Kurmaana'] == sel_k]
                elif f_type == "Ji'a":
                    sel_m = c2.selectbox("Ji'a:", MONTH_ORDER)
                    filtered = filtered[filtered['Ji\'a'] == sel_m]
                elif f_type == "Guyyaa":
                    sel_d = c2.date_input("Guyyaa Filadhu:", datetime.now())
                    filtered = filtered[filtered['Guyyaa'] == sel_d.strftime('%d/%m/%Y')]

            # --- 2. Metric Cards ---
            st.markdown("---")
            m1, m2, m3 = st.columns(3)
            m1.markdown(f"<div class='card'><h4>💰 Kaffaltii</h4><h2>{filtered['Kafaltii_Taj'].sum():,.2f}</h2><p>ETB</p></div>", unsafe_allow_html=True)
            m2.markdown(f"<div class='card'><h4>👥 Baay'ina</h4><h2>{len(filtered)}</h2><p>Abbaa Dhimmaa</p></div>", unsafe_allow_html=True)
            top_st = filtered['Maqaa_Ogeessa'].mode()[0] if not filtered.empty else "-"
            m3.markdown(f"<div class='card'><h4>🏆 Ogeessa</h4><h2>{top_st}</h2><p>Hojii Baay'ee</p></div>", unsafe_allow_html=True)

            # --- 3. EXPORT BUTTONS (PDF, EXCEL, PPT) ---
            st.subheader("📥 Gabaasaalee Buufadhu")
            ex_c1, ex_c2, ex_c3 = st.columns(3)

            # Excel
            buf_ex = io.BytesIO()
            with pd.ExcelWriter(buf_ex, engine='xlsxwriter') as writer:
                filtered[COL_NAMES].to_excel(writer, index=False)
            ex_c1.download_button("📊 Excel Buufadhu", buf_ex.getvalue(), "Gabaasa_Dadar.xlsx")

            # PPT (NEW)
            ppt_file = create_ppt_report(filtered, f_type)
            ex_c2.download_button(
                label="🖥️ PowerPoint (PPT) Buusi",
                data=ppt_file,
                file_name=f"Gabaasa_Dadar_{f_type}.pptx",
                mime="application/vnd.openxmlformats-officedocument.presentationml.presentation"
            )

            # Telegram erguuf
            if ex_c3.button("✈️ Telegramitti Ergi"):
                st.info("Gabaasni gara Telegramitti ergameera!")
            
            st.divider()
            st.subheader("📋 Tarreeffama Gabaasaa")
            st.dataframe(filtered[COL_NAMES], use_container_width=True)

        else:
            st.warning("Data'n galmeeffame hin jiru.")
