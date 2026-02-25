import json
import streamlit as st
from sentinelfs.data_store import load_exposure, load_geojson, load_scenarios, load_signals
from sentinelfs.maps import render_impact_map_folium
from sentinelfs.risk_engine import compute_baseline_risk
from sentinelfs.scenario_engine import second_order_effects, simulate_scenario

st.set_page_config(page_title="Scenarios", layout="wide")
st.title("🔮 Scenario Simulation")

scenarios = load_scenarios()
scenario_name = st.selectbox("Scenario", list(scenarios.keys()))
severity = st.slider("Severity", 1, 5, 3)
horizon = st.radio("Time horizon", [7, 14, 30], horizontal=True)

if st.button("Simulate", type="primary"):
    latest = compute_baseline_risk(load_signals(), window_days=90)
    exposure = load_exposure()
    impacts, assumptions = simulate_scenario(
        latest,
        exposure,
        scenario_name,
        scenarios[scenario_name]["base_impact"],
        severity,
        horizon,
    )

    st.subheader("Impact Mode Map")
    render_impact_map_folium(load_geojson(), impacts, show_hormuz=(scenario_name == "Hormuz Closure"))

    if scenario_name == "Hormuz Closure":
        st.info("Chokepoint: Hormuz is strategically highlighted in this scenario.")

    view = impacts[["country", "impact_shipping", "impact_price", "supply_disruption_prob", "impact_severity", "confidence"]].copy()
    view.columns = ["Country", "Shipping Disruption", "Price Pressure Proxy", "Supply Disruption Probability", "Impact Severity", "Confidence"]
    st.subheader("Impact table")
    st.dataframe(view.sort_values("Impact Severity", ascending=False), use_container_width=True)

    st.subheader("Second-order effects")
    for item in second_order_effects(scenario_name):
        st.write(f"- {item}")

    st.subheader("Confidence + assumptions")
    st.code(json.dumps(assumptions, indent=2), language="json")
