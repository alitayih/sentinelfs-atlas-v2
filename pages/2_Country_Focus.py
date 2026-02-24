import streamlit as st
import plotly.express as px
from sentinelfs.data_store import list_actions, load_exposure, load_signals
from sentinelfs.risk_engine import compute_baseline_risk, detect_trend
from sentinelfs.ui import render_risk_badge, what_this_means, what_to_do_now

st.set_page_config(page_title="Country Focus", layout="wide")
st.title("🎯 Country Focus")

country = st.session_state.get("selected_country")
if not country:
    st.warning("No country selected yet. Please click a country on Map Home first.")
    st.page_link("pages/1_Map_Home.py", label="Go to Map Home")
    st.stop()

signals = load_signals()
exposure = load_exposure()
latest = compute_baseline_risk(signals, window_days=90)
row = latest[latest["country"] == country]
if row.empty:
    st.error("Selected country was not found in demo data.")
    st.stop()

rec = row.iloc[0]
trend = detect_trend(signals, country)
st.caption(f"Selected country: **{country}**")

t1, t2, t3, t4 = st.tabs(["Overview", "Drivers", "Exposure", "Actions"])

with t1:
    render_risk_badge(rec["risk_level"])
    st.write(f"**Plain-language summary:** Risk is **{rec['risk_level']}** with score **{rec['risk_score']:.2f}**. Trend over 14 days is **{trend}**.")
    st.markdown("### What this means")
    st.write(what_this_means(rec["risk_level"]))
    st.markdown("### What to do now")
    for item in what_to_do_now(rec["risk_level"]):
        st.write(f"- {item}")

with t2:
    cdf = signals[signals["country"] == country].sort_values("date").tail(90)
    for metric in ["conflict_intensity", "freight_volatility", "export_restriction_score", "escalation_probability"]:
        fig = px.line(cdf, x="date", y=metric, title=metric.replace("_", " ").title())
        st.plotly_chart(fig, use_container_width=True)

with t3:
    xrow = exposure[exposure["country"] == country]
    if not xrow.empty:
        st.dataframe(xrow, use_container_width=True)
    else:
        st.info("No exposure profile found for this country.")

with t4:
    adf = list_actions(country=country)
    st.dataframe(adf, use_container_width=True)
