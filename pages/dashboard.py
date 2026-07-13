import streamlit as st
import pandas as pd

from modules.database_functions import get_inspection_summary_counts, search_inspections
from utils import get_dashboard_metrics


def render_dashboard():
    st.title("📊 Dashboard")
    st.caption("Monitor inspections, track pending reports, and manage the workflow in one place.")

    metrics = get_dashboard_metrics()
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Inspections", metrics.get("total", 0))
    col2.metric("Today's Inspections", metrics.get("today", 0))
    col3.metric("Pending Reports", metrics.get("pending", 0))
    col4.metric("Completed Reports", metrics.get("completed", 0))

    st.markdown("---")
    st.subheader("Quick Actions")
    action_col1, action_col2, action_col3 = st.columns(3)

    def redirect_to(page_name):
        st.session_state.redirect_page = page_name
        st.rerun()

    with action_col1:
        if st.button("Create New Inspection"):
            redirect_to("Vehicle Information")
    with action_col2:
        if st.button("View Report History"):
            redirect_to("Report History")
    with action_col3:
        if st.button("Generate Report"):
            redirect_to("Generate Report")

    st.markdown("---")
    query = st.text_input("Search by VIN, Registration, Customer Name, or Inspection ID")
    if query:
        results = search_inspections(query)
        if results:
            st.dataframe(pd.DataFrame(results))
        else:
            st.info("No matching inspections found")

    st.markdown("---")
    st.subheader("Recent Activity")
    st.info("Inspection workflow is ready. Start a new inspection from the sidebar to begin capturing data.")
