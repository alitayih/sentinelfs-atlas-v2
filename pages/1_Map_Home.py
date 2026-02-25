import streamlit as st
from streamlit_plotly_events import plotly_events
from sentinelfs.data_store import load_signals
from sentinelfs.map_choropleth import load_admin0_geojson, build_country_risk_df, render_country_choropleth

GEOJSON_PATH = "data/ne_110m_admin_0_countries.geojson"

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
geojson = load_admin0_geojson(GEOJSON_PATH)
risk_df = build_country_risk_df(signals, geojson, window_days=window, commodity=commodity)

left, right = st.columns([3, 1])
with left:
    fig = render_country_choropleth(risk_df, geojson, window_days=window, commodity=commodity)
    selected = plotly_events(fig, click_event=True, hover_event=False, select_event=False, override_height=580, key="country_choropleth")

    if selected:
        idx = selected[0].get("pointIndex")
        if idx is not None and 0 <= idx < len(risk_df):
            rec = risk_df.iloc[int(idx)]
            st.session_state["selected_country_iso3"] = rec["iso3"]
            st.session_state["selected_country_name"] = rec["country_name"]
            st.session_state["selected_country"] = rec["country_name"]
            st.success(f"Selected: {rec['country_name']}")
            try:
                st.switch_page("pages/2_Country_Focus.py")
            except Exception:
                if st.button("Open Country Focus", type="primary"):
                    st.switch_page("pages/2_Country_Focus.py")

with right:
    st.subheader("Quick Summary")
    st.info("Click a country to open Country Focus.")
    sel_name = st.session_state.get("selected_country_name") or st.session_state.get("selected_country")
    sel_iso3 = st.session_state.get("selected_country_iso3")
    if sel_iso3:
        row = risk_df[risk_df["iso3"] == sel_iso3]
    elif sel_name:
        row = risk_df[risk_df["country_name"] == sel_name]
    else:
        row = risk_df.iloc[0:0]

    if not row.empty:
        rec = row.iloc[0]
        st.metric("Country", rec["country_name"])
        st.metric("ISO3", rec["iso3"])
        st.metric("Risk", f"{rec['risk_level']} ({rec['risk_score']:.1f})")

st.caption(f"Filters applied — Date window: {window} days | Commodity: {commodity} | Mode: {'Advanced' if mode else 'Simple'}")
