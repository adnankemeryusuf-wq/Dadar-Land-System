# --- CSS Styling ---
st.markdown("""
    <style>
    /* Main app background */
    .stApp {
        background: linear-gradient(135deg, #f1f8e9 0%, #ffffff 100%);
    }

    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background-color: #33691e !important;
    }
    [data-testid="stSidebar"] * {
        color: #ffffff !important;
    }

    /* Form container */
    div.stForm {
        background: white;
        border-radius: 15px;
        padding: 25px;
        border: 2px solid #2e7d32;
        box-shadow: 0px 4px 15px rgba(0, 0, 0, 0.1);
    }

    /* Cards */
    .card {
        background: white;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        text-align: center;
        border-top: 5px solid #2e7d32;
        margin-bottom: 10px;
    }

    /* Metric values */
    .metric-value {
        font-size: 24px;
        font-weight: bold;
        color: #1b5e20;
    }
    </style>
""", unsafe_allow_html=True)
