import streamlit as st
from utils.styles import load_css

st.set_page_config(
    page_title="Perencanaan Kinerja",
    page_icon="📘",
    layout="wide"
)

st.markdown(load_css(), unsafe_allow_html=True)

with st.sidebar:
    st.image("assets/icons/single/logo.png", width=180)
    st.divider()
    st.page_link("app.py", label="Dashboard", icon="🏠")
    st.page_link("pages/1_Perencanaan_Kinerja.py", label="Perencanaan Kinerja", icon="📘")

st.title("PERENCANAAN KINERJA")
st.caption("Detail Komponen SAKIP")

st.info("Halaman Perencanaan Kinerja sedang kita bangun.")