import streamlit as st
from datetime import datetime
from fpdf import FPDF
import os
from PIL import Image
from ethiopian_date import EthiopianDateConverter

# ================= 1. CORE FUNCTIONS =================

def get_ethiopian_date_str():
    """Guyyaa har'aa G.C. irraa gara E.C. tti jijjiira"""
    now = datetime.now()
    converter = EthiopianDateConverter()
    # EthiopianDate Object deebisa
    e_date = converter.to_ethiopian(now.year, now.month, now.day)
    # Object irraa .day, .month, .year fayyadamna
    return f"{e_date.day:02d}/{e_date.month:02d}/{e_date.year}"

def create_clearance_pdf(data):
    # 'Times' jechuun Times New Roman jechuudha
    pdf = FPDF(orientation='P', unit='mm', format='A4')
    pdf.add_page()
    
    # 1. BORDER (Sarara Qarqaraa Double)
    pdf.set_line_width(0.8); pdf.rect(10, 10, 190, 277)
    pdf.set_line_width(0.2); pdf.rect(12, 12, 186, 273)

    # 2. LOGOS
    if os.path.exists("logo_bitta.jpg"): 
        pdf.image("logo_bitta.jpg", 15, 15, 25)
    if os.path.exists("logo_mirga.jpg"): 
        pdf.image("logo_mirga.jpg", 170, 15, 25)

    # 3. HEADER
    pdf.set_y(22)
    pdf.set_font('Times', 'B', 15)
    pdf.cell(0, 8, "MOOTUMMAA NAANNOO OROMIYAA", ln=True, align='C')
    pdf.set_font('Times', 'B', 14)
    pdf.cell(0, 8, "BULCHIINSA MAGAALAA DADAR", ln=True, align='C')
    pdf.cell(0, 8, "WAAJJIRA LAFAA", ln=True, align='C')
    
    pdf.ln(2); pdf.set_line_width(0.5); pdf.line(20, 48, 190, 48)

    # 4. LAKK FI GUYYAA (Kalaandara Itoophiyaa)
    pdf.ln(8); pdf.set_font('Times', '', 12)
    converter = EthiopianDateConverter()
    now_ec = converter.to_ethiopian(datetime.now().year, datetime.now().month, datetime.now().day)
    
    guyyaa_ec = get_ethiopian_date_str()
    now_ec_year = now_ec.year 

    pdf.set_x(20)
    pdf.cell(90, 5, f"Lakk. Galmee: DAD/WL/{now_ec_year}/____", ln=False, align='L')
    pdf.cell(80, 5, f"Guyyaa: {guyyaa_ec}", ln=True, align='R')

    # 5. SUBJECT
    pdf.ln(10); pdf.set_font('Times', 'BU', 14)
    pdf.cell(0, 10, "DHIMMA: WARAQAA RAGAA QULQULLINAA (CLEARANCE)", ln=True, align='C')

    # 6. BODY TEXT
    pdf.set_y(90); pdf.set_font('Times', '', 12)
    
    kaffaltii_ibsa = ("2. Kaffaltii Liizii waggaa/duraa kan kaffalamuu qabu hunda kaffalanii kan xumuran ta'uu isaanii ni mirkaneessina." 
                      if data.get('gosa_qabiyyee') == "Liizii" else 
                      "2. Kaffaltii tajaajilaa fi kaffaltiiwwan adda addaa qabiyyee durii kanaan wal qabatan hunda raawwatanii kan xumuran ta'uu isaanii ni mirkaneessina.")

    pdf.set_x(20)
    text_content = (
        f"Waraqaan ragaa kun Obbo/Adde/Dhaabbata {data['maqaa'].upper()} Araddaa {data['araddaa']} "
        f"Qaxana {data['qaxana']} keessatti mana/lafa Lakk. Kaartaa {data['kaartaa']} qabaniif kan kennameedha.\n\n"
        f"Maamilli kun hanga guyyaa har'aatti tajaajiloota waajjira keenya irraa argachaa turaniif:\n\n"
        f"1. Kaffaltii Gibira waggaa hanga bara {data['bara_gibiraa']} guutummaatti kaffalaniiru.\n"
        f"{kaffaltii_ibsa}\n"
        f"3. Lafni/Manni kun DHORKAA MANA MURTII ykn dhimma seeraa biroo kamirrayyuu bilisa ta'uu isaa qulqulleessinee mirkaneessineera.\n\n"
        f"Kanaafuu, maamilli kun dhimma {data['dhimma']} raawwachuuf ragaa qulqullinaa kana akka dhiyeeffatan beekamee, "
        f"waajjirri keenyas dhimma kana irratti mormii kan hin qabne ta'uu ni mirkaneessina."
    )
    pdf.multi_cell(170, 9, text_content, align='L')

    # 7. SIGNATURE SECTION (Maqaa Ogeessaa haqameera)
    pdf.set_y(230); pdf.set_font('Times', 'B', 12); pdf.set_x(120)
    pdf.cell(0, 8, "Maqaa Itti Gaafatamaa: ________________", ln=True)
    pdf.set_x(120); pdf.cell(0, 8, "Mallattoo: _________________", ln=True)
    pdf.set_x(120); pdf.cell(0, 8, f"Guyyaa (E.C): {guyyaa_ec}", ln=True)
    pdf.set_x(120); pdf.cell(0, 8, "(Chaappaa Waajjiraa)", ln=True)

    return pdf.output(dest='S').encode('latin-1')
