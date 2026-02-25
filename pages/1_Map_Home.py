import streamlit as st
from sentinelfs.data_store import load_signals, load_geojson
from sentinelfs.risk_engine import compute_baseline_risk
from sentinelfs.maps import render_baseline_risk_map_folium

st.set_page_config(page_title="Map Home", layout="wide")
st.title("🗺️ SentinelFS Atlas — Map Home")

c1, c2, c3, c4 = st.columns([1, 1, 1, 1])
with c1:
    window = st.radio("Date window", [30, 90], horizontal=True, index=1)
with c2:
    commodity = st.selectbox("Commodity", ["All", "Wheat", "Rice", "Frozen Protein"], index=0)
with c3:
    mode = st.toggle("Advanced Mode", value=False)
with c4:
    if st.button("Reset map cache"):
        st.cache_data.clear()
        st.rerun()

signals = load_signals()
geojson = load_geojson()
latest_risk = compute_baseline_risk(signals, window_days=window)

left, right = st.columns([3, 1])
with left:
    clicked = render_baseline_risk_map_folium(geojson, latest_risk)
    if clicked and clicked.get("country_name"):
        st.session_state["selected_country"] = clicked["country_name"]
        if clicked.get("iso_a3"):
            st.session_state["selected_country_iso3"] = clicked["iso_a3"]
        st.success(f"Selected: {clicked['country_name']}")
        st.switch_page("pages/2_Country_Focus.py")

with right:
    st.subheader("Quick Summary")
    selected = st.session_state.get("selected_country")
    if selected:
        row = latest_risk[latest_risk["country"] == selected]
        if not row.empty:
            rec = row.iloc[0]
            st.metric("Country", selected)
            st.metric("Baseline Risk", rec["risk_level"])
            st.metric("Risk Score", f"{rec['risk_score']:.2f}")
        else:
            st.info("Click a country on the map to view details.")
    else:
        st.info("Click a country on the map to drill into Country Focus.")

st.caption(f"Filters applied — Date window: {window} days | Commodity: {commodity} | Mode: {'Advanced' if mode else 'Simple'}")
