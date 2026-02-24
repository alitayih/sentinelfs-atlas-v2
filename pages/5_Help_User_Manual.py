import streamlit as st

st.set_page_config(page_title="Help", layout="wide")
st.title("📘 Help / User Manual")

st.header("Quick Start")
st.markdown("1. Open **Map Home**.\n2. Click any country polygon.\n3. Review **Country Focus** for plain-language guidance.\n4. Run **Scenarios** to anticipate shocks.")

st.header("How to read the map")
st.write("Green = lower immediate risk, Yellow = moderate pressure, Red = elevated disruption risk.")

st.header("Metric definitions (plain language)")
st.markdown(
    """
- **Conflict intensity:** degree of geopolitical tension in/around a country.
- **Freight volatility:** instability in shipping/logistics costs.
- **Export restriction score:** likelihood of policy barriers affecting exports.
- **Escalation probability:** chance disruptions worsen in the near term.
"""
)

st.header("How scenario simulation works (Hormuz example)")
st.write("The model combines baseline risk + country exposure + scenario base impact + selected severity and time horizon to estimate likely disruption.")

st.header("Troubleshooting Streamlit Cloud")
st.markdown(
    """
- Confirm `requirements.txt` installs cleanly.
- Deploy from `main` branch with `app.py` as entrypoint.
- If app behaves oddly, use **Clear cache** and **Reboot app** in Streamlit Cloud.
"""
)

st.info("All data in this demo is synthetic and for illustration only.")
