import streamlit as st
import os
import requests
import pandas as pd
from datetime import datetime
import plotly.express as px

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="Dadar Land System V9", layout="wide", page_icon="🏢")

USER_NAME, PASS_WORD = "admin", "1234"
DB_FILE = "galmee_abbaa_dhimmaa.txt"
LOGO_PATH = "logo.png"

# --- 2. DATA HANDLERS ---
def load_data():
    if not os.path.exists(DB_FILE): return pd.DataFrame()
    data_list = []
    try:
        with open(DB_FILE, "r", encoding="utf-8") as f:
            for line in f:
                if "|" in line:
                    parts = [x.split(":")[1].strip() for x in line.split("|")]
                    data_list.append(parts)
        cols = ["ID", "Guyyaa", "Maqaa", "Bilbila", "Araddaa", "Wirtuu", "Dhimma", "Kartaa", "Lizi", "Beellama", "Ogeessa", "Status"]
        return pd.DataFrame(data_list, columns=cols)
    except: return pd.DataFrame()

def save_all_data(df):
    """Dataframe gara text file-tti deebisee barreessa"""
    lines = []
    for _, row in df.iterrows():
        line = (f"ID:{row['ID']} | Guyyaa:{row['Guyyaa']} | Maqaa:{row['Maqaa']} | Bilbila:{row['Bilbila']} | "
                f"Araddaa:{row['Araddaa']} | Wirtuu:{row['Wirtuu']} | Dhimma:{row['Dhimma']} | Kartaa:{row['Kartaa']} | "
                f"Lizi:{row['Lizi']} | Beellama:{row['Beellama']} | Ogeessa:{row['Ogeessa']} | Status:{row['Status']}\n")
        lines.append(line)
    with open(DB_FILE, "w", encoding="utf-8") as f:
        f.writelines(lines)

# --- 3. UI STYLE ---
st.markdown("""
    <style>
    .stApp { background-color: #f8f9fa; }
    .header-box { background: #1f4e78; color: white; padding: 20px; border-radius: 10px; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

# --- 4. APP LOGIC ---
if 'logged_in' not in st.session_state: st.session_state.logged_in = False

if not st.session_state.logged_in:
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        st.subheader("Seensa Systemii")
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")
        if st.button("Seeni"):
            if u == USER_NAME and p == PASS_WORD:
                st.session_state.logged_in = True
                st.rerun()
            else: st.error("Dogooggora!")
else:
    with st.sidebar:
        st.title("Main Menu")
        menu = st.radio("FILADHU", ["🏠 Dashboard", "📝 Galmee Haaraa", "⚙️ Sirreessi (Edit/Delete)", "🚪 Logout"], key="sidebar_menu")

    df = load_data()

    if menu == "🏠 Dashboard":
        st.markdown('<div class="header-box"><h1>Waajjira Lafaa Magaalaa Dadar</h1></div>', unsafe_allow_html=True)
        st.write("")
        
        # Search Feature
        search = st.text_input("🔍 Barbaadi (Maqaa/Bilbila):", key="dash_search")
        if not df.empty:
            filtered = df[df['Maqaa'].str.contains(search, case=False) | df['Bilbila'].str.contains(search)]
            
            c1, c2 = st.columns(2)
            c1.metric("Waliigala", len(df))
            c2.metric("Argaman", len(filtered))
            
            st.subheader("Ragaalee Galmee")
            st.dataframe(filtered, use_container_width=True)
            
            fig = px.pie(filtered, names='Status', title="Haala Dhimmootaa")
            st.plotly_chart(fig)

    elif menu == "📝 Galmee Haaraa":
        st.subheader("📝 Galmee Haaraa")
        with st.form("new_entry_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                name = st.text_input("Maqaa")
                phone = st.text_input("Bilbila")
                araddaa = st.text_input("Araddaa")
            with col2:
                dhimma = st.selectbox("Dhimma", ["Kartaa", "Lizi", "Safara", "Jijjiirraa"])
                pay = st.number_input("Kafaltii", min_value=0.0)
                beellama = st.date_input("Beellama")
            
            if st.form_submit_button("Galmeessi"):
                id_sys = datetime.now().strftime("%f")[:4]
                guyyaa = datetime.now().strftime("%Y-%m-%d")
                new_line = f"ID:{id_sys} | Guyyaa:{guyyaa} | Maqaa:{name} | Bilbila:{phone} | Araddaa:{araddaa} | Wirtuu:- | Dhimma:{dhimma} | Kartaa:{pay} | Lizi:0 | Beellama:{beellama} | Ogeessa:- | Status:Pending\n"
                with open(DB_FILE, "a", encoding="utf-8") as f: f.write(new_line)
                st.success("Galmeeffameera!")

    elif menu == "⚙️ Sirreessi (Edit/Delete)":
        st.subheader("⚙️ Ragaa Sirreessi ykn Haqi")
        if not df.empty:
            target_id = st.selectbox("ID Abbaa dhimmaa filadhu:", df['ID'].tolist())
            row = df[df['ID'] == target_id].iloc[0]

            with st.form("edit_form"):
                st.write(f"ID: {target_id} qulqulleessi")
                new_status = st.selectbox("Status Jijjiiri", ["Pending", "Finished", "Cancelled"], index=["Pending", "Finished", "Cancelled"].index(row['Status']))
                new_name = st.text_input("Maqaa Sirreessi", value=row['Maqaa'])
                new_pay = st.text_input("Kafaltii", value=row['Kartaa'])
                
                col_e1, col_e2 = st.columns(2)
                if col_e1.form_submit_button("💾 UPDATE"):
                    df.loc[df['ID'] == target_id, ['Status', 'Maqaa', 'Kartaa']] = [new_status, new_name, new_pay]
                    save_all_data(df)
                    st.success("Ragaan sirreeffameera!")
                    st.rerun()
                
                if col_e2.form_submit_button("🗑️ HAQI (DELETE)"):
                    df = df[df['ID'] != target_id]
                    save_all_data(df)
                    st.warning("Ragaan haqameera!")
                    st.rerun()
        else:
