import streamlit as st
from sentinelfs.data_store import add_action, list_actions, update_action_close

st.set_page_config(page_title="Action Tracking", layout="wide")
st.title("✅ Action Tracking")

with st.form("add_action_form"):
    c1, c2 = st.columns(2)
    with c1:
        title = st.text_input("Title")
        owner = st.text_input("Owner")
        due_date = st.date_input("Due date")
        status = st.selectbox("Status", ["Open", "In Progress", "Closed"], index=0)
        country = st.text_input("Country")
    with c2:
        commodity = st.selectbox("Commodity", ["All", "Wheat", "Rice", "Frozen Protein"])
        expected_risk_impact = st.slider("Expected risk impact", 0.0, 1.0, 0.3)
        notes = st.text_area("Notes")
        outcome_notes = st.text_area("Outcome notes")
        observed_impact = st.slider("Observed impact", 0.0, 1.0, 0.0)
    submitted = st.form_submit_button("Add action")
    if submitted and title:
        add_action(
            {
                "title": title,
                "owner": owner,
                "due_date": str(due_date),
                "status": status,
                "country": country,
                "commodity": commodity,
                "expected_risk_impact": expected_risk_impact,
                "notes": notes,
                "outcome_notes": outcome_notes,
                "observed_impact": observed_impact,
            }
        )
        st.success("Action saved.")

st.subheader("Filter")
filter_country = st.text_input("Country filter", value=st.session_state.get("selected_country", ""))
df = list_actions(country=filter_country if filter_country else None)
st.dataframe(df, use_container_width=True)

st.subheader("Close action")
if not df.empty:
    action_id = st.selectbox("Action ID", df["id"].tolist())
    close_notes = st.text_input("Outcome summary")
    close_impact = st.slider("Observed impact (close)", 0.0, 1.0, 0.2)
    if st.button("Close selected action"):
        update_action_close(int(action_id), close_notes, close_impact)
        st.success("Action closed.")
else:
    st.info("No actions to close.")
