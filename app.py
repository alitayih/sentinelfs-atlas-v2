import streamlit as st

try:
    import folium
    from streamlit_folium import st_folium
except Exception as e:
    st.error("Dependency import failed. Check requirements.txt and Streamlit Cloud logs.")
    st.exception(e)
    st.stop()

from sentinelfs.data_store import init_actions_table

st.set_page_config(page_title="SentinelFS Atlas", layout="wide")
init_actions_table()

st.title("SentinelFS Atlas")
st.markdown(
    """
Welcome to **SentinelFS Atlas** — a map-first anticipatory intelligence cockpit for food and logistics risk.

👉 Open **Map Home** from the left sidebar to begin by clicking a country.
"""
)
