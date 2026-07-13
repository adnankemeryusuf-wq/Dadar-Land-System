# ==========================================================
# DADAR LAND ADMIN PREMIUM SYSTEM
# FIXED VERSION 1.0
# PART 1/5
# ==========================================================

import streamlit as st
import pandas as pd
import os
import io
import requests
import tempfile

from datetime import datetime
from fpdf import FPDF
from ethiopian_date import EthiopianDateConverter


# ==========================================================
# 1. CONFIGURATION
# ==========================================================

BOT_TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"
CHAT_ID_MANAGER = "YOUR_CHAT_ID"

LOGO_PATH = "Adiaan/logo.png"
DATA_FILE = "dadar_final_report.txt"


st.set_page_config(
    page_title="Dadar Land Admin Premium",
    layout="wide",
    page_icon="🏢"
)


# ==========================================================
# 2. PREMIUM CSS STYLE
# ==========================================================

st.markdown("""
<style>

.stApp {
    background: linear-gradient(
        135deg,
        #f0fdf4 0%,
        #ffffff 100%
    );
}


/* Main Title */

.main-title {

    font-family: Segoe UI;

    font-size: 2.5rem;

    font-weight: 800;

    color:#064e3b;

    text-align:center;

}


/* Dashboard Card */

.card {

    background:white;

    padding:25px;

    border-radius:20px;

    box-shadow:
    0 8px 32px rgba(0,0,0,0.10);

    text-align:center;

}


/* Number */

.metric-value {

    font-size:2.2rem;

    font-weight:800;

    color:#059669;

}



</style>

""",
unsafe_allow_html=True)



# ==========================================================
# 3. DATABASE STRUCTURE
# ==========================================================

COL_NAMES = [

    "Guyyaa",

    "Maqaa_Abbaa_Dhimmaa",

    "Araddaa",

    "Qaxana",

    "Gosa_Tajajjilaa",

    "Maqaa_Ogeessa",

    "Kafaltii_Taj"

]



# ==========================================================
# 4. LOAD DATA
# ==========================================================

def load_data():

    if not os.path.exists(DATA_FILE):

        return pd.DataFrame(
            columns=COL_NAMES
        )


    if os.path.getsize(DATA_FILE)==0:

        return pd.DataFrame(
            columns=COL_NAMES
        )


    df = pd.read_csv(

        DATA_FILE,

        sep="|",

        names=COL_NAMES,

        header=None,

        encoding="utf-8"

    )


    df["Kafaltii_Taj"] = pd.to_numeric(

        df["Kafaltii_Taj"],

        errors="coerce"

    ).fillna(0)


    return df



# ==========================================================
# 5. SAVE DATA
# ==========================================================

def save_data(df):

    df.to_csv(

        DATA_FILE,

        sep="|",

        index=False,

        header=False,

        encoding="utf-8"

    )



# ==========================================================
# 6. ETHIOPIAN DATE
# ==========================================================

def get_ethiopian_date():

    now = datetime.now()


    ethiopian = EthiopianDateConverter.to_ethiopian(

        now.year,

        now.month,

        now.day

    )


    return (
        f"{ethiopian.day:02d}/"
        f"{ethiopian.month:02d}/"
        f"{ethiopian.year}"
    )



# ==========================================================
# 7. SESSION DATA
# ==========================================================

if "df" not in st.session_state:

    st.session_state.df = load_data()


df = st.session_state.df
# ==========================================================
# PART 2/5
# PDF GENERATOR FUNCTIONS
# ==========================================================


# ==========================================================
# 1. RECEIPT PDF
# ==========================================================

def create_receipt_pdf(row):

    pdf = FPDF()

    pdf.add_page()


    pdf.set_font(
        "Arial",
        "B",
        16
    )


    pdf.cell(
        0,
        10,
        "WAAJJIRA LAFAA MAGAALAA DADAR",
        ln=True,
        align="C"
    )


    pdf.set_font(
        "Arial",
        "B",
        14
    )


    pdf.cell(
        0,
        10,
        "NAGAHEE KAFFALTII",
        ln=True,
        align="C"
    )


    pdf.ln(10)


    pdf.set_font(
        "Arial",
        "",
        12
    )


    data = [

        f"Guyyaa: {row['Guyyaa']}",

        f"Maqaa: {row['Maqaa_Abbaa_Dhimmaa']}",

        f"Araddaa: {row['Araddaa']}",

        f"Qaxana: {row['Qaxana']}",

        f"Tajaajila: {row['Gosa_Tajajjilaa']}",

        f"Ogeessa: {row['Maqaa_Ogeessa']}"

    ]


    for item in data:

        pdf.cell(
            0,
            8,
            item,
            ln=True
        )


    pdf.ln(5)


    pdf.set_font(
        "Arial",
        "B",
        14
    )


    pdf.cell(

        0,

        10,

        f"Kaffaltii: {row['Kafaltii_Taj']:,.2f} ETB",

        ln=True

    )


    return pdf.output(
        dest="S"
    ).encode("latin-1")





# ==========================================================
# 2. CLEARANCE PDF
# ==========================================================


def create_clearance_pdf(data):

    pdf = FPDF(
        "P",
        "mm",
        "A4"
    )


    pdf.add_page()



    # Border

    pdf.rect(
        10,
        10,
        190,
        277
    )



    pdf.set_y(25)


    pdf.set_font(
        "Arial",
        "B",
        16
    )


    pdf.cell(

        0,

        10,

        "MOOTUMMAA NAANNOO OROMIYAA",

        ln=True,

        align="C"

    )


    pdf.cell(

        0,

        10,

        "BULCHIINSA MAGAALAA DADAR",

        ln=True,

        align="C"

    )


    pdf.ln(10)



    pdf.set_font(
        "Arial",
        "B",
        15
    )


    pdf.cell(

        0,

        10,

        "WARAQAA RAGAA QULQULLINAA",

        ln=True,

        align="C"

    )


    pdf.ln(15)



    pdf.set_font(
        "Arial",
        "",
        12
    )


    lines=[


    f"Maqaa: {data['maqaa']}",

    f"Araddaa: {data['araddaa']}",

    f"Qaxana: {data['qaxana']}",

    f"Lakk. Kaartaa: {data['kaartaa']}",

    f"Gosa Qabiyyee: {data['gosa_qabiyyee']}",

    f"Bara Gibiraa: {data['bara_gibiraa']}",

    f"Dhimma: {data['dhimma']}"

    ]



    for line in lines:

        pdf.cell(

            0,

            10,

            line,

            ln=True

        )



    pdf.ln(10)



    pdf.multi_cell(

        0,

        8,

        "Ragaan kun bu'uura seera bulchiinsa lafaatiin "
        "kennamee dhimma barbaadameef akka tajaajilu "
        "ni mirkaneessina."

    )



    pdf.ln(20)


    pdf.cell(

        0,

        10,

        f"Itti Gaafatamaa: {data['head_name']}",

        ln=True

    )



    return pdf.output(

        dest="S"

    ).encode("latin-1")





# ==========================================================
# 3. CERTIFICATE PDF
# ==========================================================


def create_certificate_pdf(

    name,

    count,

    rank,

    head_name

):


    pdf = FPDF(

        "L",

        "mm",

        "A4"

    )


    pdf.add_page()



    pdf.set_line_width(2)


    pdf.rect(

        10,

        10,

        277,

        190

    )



    pdf.set_y(45)



    pdf.set_font(

        "Arial",

        "B",

        28

    )


    pdf.cell(

        0,

        15,

        "SARTIIFIIKEETA BADHAASAA",

        ln=True,

        align="C"

    )



    pdf.ln(15)



    pdf.set_font(

        "Arial",

        "B",

        24

    )


    pdf.cell(

        0,

        15,

        name.upper(),

        ln=True,

        align="C"

    )



    pdf.set_font(

        "Arial",

        "",

        15

    )


    pdf.cell(

        0,

        15,

        f"Dhimma {count} milkiin xumurtaniif",

        ln=True,

        align="C"

    )



    pdf.ln(20)


    pdf.cell(

        0,

        10,

        f"Itti Gaafatamaa: {head_name}",

        ln=True,

        align="C"

    )



    return pdf.output(

        dest="S"

    ).encode("latin-1")
# ==========================================================
# PART 3/5
# LOGIN + DASHBOARD + MENU
# ==========================================================


# ==========================================================
# SESSION LOGIN
# ==========================================================

if "logged_in" not in st.session_state:

    st.session_state.logged_in = False



# ==========================================================
# LOGIN PAGE
# ==========================================================

if not st.session_state.logged_in:


    c1,c2,c3 = st.columns(
        [1,2,1]
    )


    with c2:


        if os.path.exists(LOGO_PATH):

            st.image(
                LOGO_PATH,
                width=180
            )


        st.markdown(

            "<h1 class='main-title'>"
            "Dadar Land Admin Premium"
            "</h1>",

            unsafe_allow_html=True

        )



        with st.form(
            "login_form"
        ):


            username = st.text_input(
                "Username"
            )


            password = st.text_input(

                "Password",

                type="password"

            )



            login = st.form_submit_button(

                "🔐 SEENI"

            )



            if login:


                if username=="admin" and password=="123":


                    st.session_state.logged_in=True

                    st.rerun()



                else:


                    st.error(

                        "Username ykn Password dogoggora!"

                    )





# ==========================================================
# MAIN APPLICATION
# ==========================================================

else:



    # ==========================
    # SIDEBAR
    # ==========================

    with st.sidebar:


        if os.path.exists(LOGO_PATH):

            st.image(

                LOGO_PATH,

                use_container_width=True

            )


        st.markdown(

            "## 🏢 Magaalaa Dadar"

        )


        st.divider()



        menu = st.radio(

            "Filannoo",

            [

                "📊 Dashboard",

                "📝 Galmee Tajaajilaa",

                "📜 Clearance",

                "📈 Gabaasa Galii",

                "🏆 Badhaasa",

                "🚪 Logout"

            ]

        )




    # ======================================================
    # DASHBOARD
    # ======================================================


    if menu=="📊 Dashboard":


        st.title(

            "📊 Dashboard Premium"

        )


        total_customer = len(df)



        total_income = (

            df["Kafaltii_Taj"]

            .sum()

        )



        if not df.empty:


            top_staff = (

                df["Maqaa_Ogeessa"]

                .mode()[0]

            )


        else:


            top_staff="-"



        col1,col2,col3 = st.columns(3)



        with col1:


            st.markdown(

            f"""

            <div class="card">

            👥 Maamiltoota

            <div class="metric-value">

            {total_customer}

            </div>

            </div>

            """,

            unsafe_allow_html=True

            )




        with col2:


            st.markdown(

            f"""

            <div class="card">

            💰 Galii Waliigalaa

            <div class="metric-value">

            {total_income:,.2f}

            </div>

            </div>

            """,

            unsafe_allow_html=True

            )




        with col3:


            st.markdown(

            f"""

            <div class="card">

            🏆 Ogeessa Cimaa

            <div class="metric-value"
            style="font-size:18px">

            {top_staff}

            </div>

            </div>

            """,

            unsafe_allow_html=True

            )



        st.divider()



        st.subheader(

            "📋 Galmee Haaraa"

        )



        if not df.empty:


            st.dataframe(

                df.tail(10),

                use_container_width=True

            )


        else:


            st.info(

                "Galmeen hin jiru."

            )
# ==========================================================
# PART 4/5
# REGISTRATION + CLEARANCE + REPORT
# ==========================================================


# ==========================================================
# GALMEE TAJAAJILAA
# ==========================================================

    elif menu == "📝 Galmee Tajaajilaa":


        st.title(
            "📝 Galmee Tajaajilaa Haaraa"
        )


        services=[

            "Kaartaa Haaraa",
            "Kaartaa Bakka Bu'aa",
            "Kaartaa Kadastaraa",
            "Jijjiirraa Maqaa",
            "Sirreeffama Daangaa",
            "Clearance",
            "Hayyama Ijaarsaa",
            "Pilaanii Magaalaa",
            "Gibira Lafa Qonnaa",
            "Kaffaltii Liizii"

        ]



        with st.form(
            "service_form"
        ):


            c1,c2 = st.columns(2)


            with c1:

                maqaa = st.text_input(
                    "Maqaa Maamilaa"
                )

                araddaa = st.text_input(
                    "Araddaa"
                )

                qaxana = st.text_input(
                    "Lakk. Qaxanaa"
                )


            with c2:


                ogeessa = st.text_input(
                    "Maqaa Ogeessaa"
                )


                service = st.selectbox(

                    "Gosa Tajaajilaa",

                    services

                )


                kaffaltii = st.number_input(

                    "Kaffaltii (ETB)",

                    min_value=0.0

                )



            save = st.form_submit_button(

                "💾 GALMEESSI"

            )




        if save:


            if maqaa=="" or ogeessa=="":


                st.warning(

                    "Maqaa fi Ogeessa guuti."

                )


            elif not qaxana.isdigit():


                st.error(

                    "Qaxana keessatti lakkoofsa qofa galchi."

                )


            else:


                new_row = {


                "Guyyaa":
                datetime.now()
                .strftime(
                    "%d/%m/%Y %H:%M"
                ),


                "Maqaa_Abbaa_Dhimmaa":
                maqaa,


                "Araddaa":
                araddaa,


                "Qaxana":
                qaxana,


                "Gosa_Tajajjilaa":
                service,


                "Maqaa_Ogeessa":
                ogeessa,


                "Kafaltii_Taj":
                kaffaltii

                }



                st.session_state.df = pd.concat(

                    [

                    st.session_state.df,

                    pd.DataFrame([new_row])

                    ],

                    ignore_index=True

                )



                save_data(

                    st.session_state.df

                )


                st.success(

                    "✅ Galmeen milkiin kuufame."

                )


                st.download_button(

                    "📄 Nagahee Buufadhu",

                    create_receipt_pdf(

                        new_row

                    ),

                    "Nagahee.pdf"

                )





# ==========================================================
# CLEARANCE
# ==========================================================

    elif menu == "📜 Clearance":


        st.title(

            "📜 Waraqaa Ragaa Qulqullinaa"

        )



        with st.form(

            "clearance_form"

        ):


            c1,c2=st.columns(2)


            data={


            "maqaa":
            c1.text_input(
                "Maqaa Abbaa Qabiyyee"
            ),


            "araddaa":
            c2.text_input(
                "Araddaa"
            ),


            "qaxana":
            c1.text_input(
                "Qaxana"
            ),


            "kaartaa":
            c2.text_input(
                "Lakk. Kaartaa"
            ),


            "gosa_qabiyyee":
            c1.selectbox(
                "Gosa Qabiyyee",
                [
                "Liizii",
                "Permit"
                ]
            ),


            "bara_gibiraa":
            c2.text_input(
                "Bara Gibiraa"
            ),


            "dhimma":
            c1.selectbox(
                "Dhimma",
                [
                "Gurgurtaa",
                "Liqii",
                "Kennaa"
                ]
            ),


            "head_name":
            st.text_input(
                "Itti Gaafatamaa"
            )


            }



            create = st.form_submit_button(

                "📄 PDF UUMI"

            )



        if create:


            if data["maqaa"]:


                pdf = create_clearance_pdf(

                    data

                )


                st.download_button(

                    "📥 PDF Buufadhu",

                    pdf,

                    "Clearance.pdf"

                )





# ==========================================================
# GABAASA GALII
# ==========================================================

    elif menu=="📈 Gabaasa Galii":


        st.title(

            "📈 Gabaasa Galii"

        )


        search = st.text_input(

            "🔍 Barbaadi"

        )


        result=df.copy()



        if search:


            result=result[

                result.astype(str)

                .apply(

                lambda x:

                x.str.contains(

                    search,

                    case=False

                )

                )

                .any(axis=1)

            ]



        st.dataframe(

            result,

            use_container_width=True

        )



        excel=io.BytesIO()



        with pd.ExcelWriter(

            excel,

            engine="openpyxl"

        ) as writer:


            result.to_excel(

                writer,

                index=False

            )



        st.download_button(

            "📥 Excel Buufadhu",

            excel.getvalue(),

            "Dadar_Report.xlsx"

        )



        if st.button(

            "✈️ Telegram Ergi"

        ):


            requests.post(

            f"https://api.telegram.org/bot{BOT_TOKEN}/sendDocument",

            data={

            "chat_id":

            CHAT_ID_MANAGER

            },

            files={

            "document":

            (

            "Dadar_Report.xlsx",

            excel.getvalue()

            )

            }

            )


            st.success(

                "Gabaasni ergameera."

            )
# ==========================================================
# PART 5/5
# BADHAASA + LOGOUT + FINAL
# ==========================================================


# ==========================================================
# BADHAASA OGEEYYII
# ==========================================================

    elif menu == "🏆 Badhaasa":


        st.title(
            "🏆 Badhaasa Ogeeyyii"
        )


        head_name = st.text_input(
            "Maqaa Itti Gaafatamaa"
        )


        if not df.empty:


            ranking = (

                df["Maqaa_Ogeessa"]

                .value_counts()

                .head(3)

            )



            for rank,(name,count) in enumerate(

                ranking.items(),

                start=1

            ):


                st.divider()


                st.write(

                    f"🥇 Sadarkaa {rank}: {name} "
                    f"({count} Dhimma)"

                )



                if head_name:


                    certificate = create_certificate_pdf(

                        name,

                        count,

                        rank,

                        head_name

                    )



                    st.download_button(

                        label=
                        f"📥 Certificate {name}",

                        data=certificate,

                        file_name=
                        f"Certificate_{name}.pdf"

                    )



        else:


            st.info(

                "Odeeffannoo Ogeessaa hin jiru."

            )





# ==========================================================
# LOGOUT
# ==========================================================

    elif menu == "🚪 Logout":


        st.session_state.logged_in=False


        st.success(

            "Sirnaan baateetta."

        )


        st.rerun()
