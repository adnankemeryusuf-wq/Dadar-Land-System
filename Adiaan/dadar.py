import streamlit as st
import pandas as pd
import os

# 1. SETUP - Bakka koodiin itti jalqabu
DATA_FILE = "dadar_data.txt"

# 2. DATA FUNCTIONS - Logic koodii kee
def load_data():
    try:
        if os.path.exists(DATA_FILE):
            return pd.read_csv(DATA_FILE, sep="|")
        else:
            return pd.DataFrame(columns=["Guyyaa", "Maqaa", "Kaffaltii"])
    except Exception as e:
        st.error(f"Data dubbisuu irratti dogongorri uumame: {e}")
        return pd.DataFrame()

# 3. ACTION FUNCTIONS - Gochaalee akka Telegram erguu
def send_report(text):
    try:
        # Kodii Telegram kee asitti gala...
        # requests.post(...)
        st.success("Telegramitti ergameera!")
    except ConnectionError:
        st.error("Internet kee check godhadhu, Telegramitti hin ergamne.")
    except Exception as e:
        st.error(f"Dogongora biraa: {e}")

# 4. UI - Ijaarsa appilikeeshinii
st.title("Dadar Land Admin")
df = load_data()

# Barbaadi (Search) dabalata siif qopheessuu?
name_search = st.text_input("Maqaa barbaadi:")
if name_search:
    result = df[df['Maqaa'].str.contains(name_search, case=False)]
    st.write(result)
