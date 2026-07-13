import streamlit as st

from modules.database_functions import get_inspection_items, get_photos, update_inspection_summary
from modules.scoring import build_summary


def render_inspection_summary():
    st.title("🧾 Inspection Summary")
    st.caption("Review the final score, critical issues, and recommendations before generating the report.")
    inspection_id = st.session_state.get("inspection_id")
    if not inspection_id:
        st.info("Start a new inspection first.")
        return

    items = get_inspection_items(inspection_id)
    summary = build_summary(items)

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Overall Score", f"{summary['overall_score']:.2f}")
    col2.metric("Vehicle Health %", f"{summary['vehicle_health']:.2f}%")
    col3.metric("Condition Rating", summary['condition_rating'])
    col4.metric("Critical Issues", summary['components_requiring_repair'])

    st.markdown("---")
    st.subheader("Professional Summary")
    summary_text = (
        f"This inspection assessed the vehicle's overall mechanical and cosmetic condition with an overall score of {summary['overall_score']:.2f}. "
        f"The vehicle health percentage is {summary['vehicle_health']:.2f}% and the current condition rating is {summary['condition_rating']}."
    )
    st.write(summary_text)

    st.subheader("Recommendations")
    recommendations = []
    if summary['components_requiring_repair'] > 0:
        recommendations.append("Immediate repair is recommended for critical inspection items.")
    if summary['overall_score'] < 70:
        recommendations.append("A full mechanical review is recommended before re-sale or fleet deployment.")
    else:
        recommendations.append("Routine maintenance is recommended to preserve the current condition.")
    for recommendation in recommendations:
        st.write(f"- {recommendation}")

    if st.button("Save Summary"):
        update_inspection_summary(
            inspection_id,
            summary['overall_score'],
            summary['condition_rating'],
            summary['vehicle_health'],
            summary_text,
        )
        st.success("Summary saved")

    st.markdown("---")
    st.subheader("Inspection Photos")
    photos = get_photos(inspection_id)
    if photos:
        for photo in photos:
            st.image(photo['file_path'], width=220)
