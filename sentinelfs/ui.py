import streamlit as st


def render_risk_badge(level: str):
    colors = {"Green": "🟢", "Yellow": "🟡", "Red": "🔴"}
    st.subheader(f"{colors.get(level, '⚪')} {level} Risk")


def what_this_means(level: str) -> str:
    if level == "Red":
        return "High likelihood of disruption. Immediate mitigation planning is recommended."
    if level == "Yellow":
        return "Moderate pressure in the supply chain. Monitor closely and pre-plan alternatives."
    return "Conditions are stable for now. Maintain routine monitoring."


def what_to_do_now(level: str):
    if level == "Red":
        return ["Escalate to crisis cell", "Activate alternative suppliers", "Review inventory burn-rate daily"]
    if level == "Yellow":
        return ["Increase monitoring cadence", "Validate backup routes", "Pre-book logistics capacity"]
    return ["Continue watch", "Refresh contingency contacts", "Validate assumptions weekly"]
