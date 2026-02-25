import streamlit as st
import plotly.express as px
from sentinelfs.data_store import list_actions, load_exposure, load_signals
from sentinelfs.risk_engine import compute_baseline_risk, detect_trend
from sentinelfs.ui import render_risk_badge, what_this_means, what_to_do_now

st.set_page_config(page_title="Country Focus", layout="wide")
st.title("🎯 Country Focus")

country = st.session_state.get("selected_country") or st.session_state.get("selected_country_name")
iso3 = st.session_state.get("selected_country_iso3")
if not country:
    st.warning("No country selected yet. Please click a country on Map Home first.")
    st.page_link("pages/1_Map_Home.py", label="Go to Map Home")
    st.stop()

signals = load_signals()
exposure = load_exposure()
latest = compute_baseline_risk(signals, window_days=90)
row = latest[latest["country"] == country]
has_signal = not row.empty

if has_signal:
    rec = row.iloc[0]
    trend = detect_trend(signals, country)

st.caption(f"Selected country: **{country}**" + (f" | ISO3: `{iso3}`" if iso3 else ""))

t1, t2, t3, t4 = st.tabs(["Overview", "Drivers", "Exposure", "Actions"])

with t1:
    if has_signal:
        render_risk_badge(rec["risk_level"])
        st.write(
            f"**Plain-language summary:** Risk is **{rec['risk_level']}** with score **{rec['risk_score']:.2f}**. Trend over 14 days is **{trend}**."
        )
        st.markdown("### What this means")
        st.write(what_this_means(rec["risk_level"]))
        st.markdown("### What to do now")
        for item in what_to_do_now(rec["risk_level"]):
            st.write(f"- {item}")
    else:
        st.info("No demo signal history exists for this country yet. You can still review exposure and actions.")

with t2:
    cdf = signals[signals["country"] == country].sort_values("date").tail(90)
    if cdf.empty:
        st.info("Driver trends are unavailable because this country is missing from demo_signals.csv.")
    else:
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
