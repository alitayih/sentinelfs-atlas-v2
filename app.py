import streamlit as st

from sentinelfs.data_store import init_actions_table

st.set_page_config(page_title="SentinelFS Atlas", layout="wide")
print("BOOT_OK")
st.write("BOOT_OK")

init_actions_table()

st.title("SentinelFS Atlas")
st.markdown(
    """
Welcome to **SentinelFS Atlas** — a map-first anticipatory intelligence cockpit for food and logistics risk.

👉 Open **Map Home** from the left sidebar to begin by clicking a country.
"""
)
