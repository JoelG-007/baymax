import streamlit as st

from ui.router import render_page
from ui.login import render_login
from database.db_init import init_db

st.set_page_config(
    page_title="Baymax",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Professional medical styling
st.markdown("""
<style>
body {
    font-family: 'Segoe UI', sans-serif;
}

h1, h2, h3 {
    color: #1f4e79;
}

.stMetric {
    background-color: #f4f8fb;
    padding: 15px;
    border-radius: 10px;
}

.block-container {
    padding-top: 2rem;
}

div[data-testid="stExpander"] {
    border-radius: 10px;
}
</style>
""", unsafe_allow_html=True)

init_db()

if "user" not in st.session_state:
    st.session_state.user = None

if st.session_state.user:
    render_page()
else:
    render_login()