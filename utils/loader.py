import pandas as pd
import streamlit as st

SHEET_ID = "1ivf0S-njLiD6VMnE8dYBDfW0_RNuw2sE3Z6q4H5fWpw"

GID = {
    "Dashboard_SAKIP": "615415318",
    "LKE": "1713682576",
    "Trend_Nilai": "747503926",
}

@st.cache_data(ttl=300)
def read_google_sheet(gid):
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={gid}"
    return pd.read_csv(url)

def load_dashboard_sakip():
    return read_google_sheet(GID["Dashboard_SAKIP"])

def load_lke():
    return read_google_sheet(GID["LKE"])

def load_trend_nilai():
    return read_google_sheet(GID["Trend_Nilai"])
    def load_terakhir_update():
    return "09 Juni 2026 17:30 WITA"
