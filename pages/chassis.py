import streamlit as st

from utils import render_inspection_page


def render_chassis():
    render_inspection_page(
        "Chassis",
        "Chassis",
        ["Frame", "Rust", "Cracks", "Accident Repair", "Alignment"],
        inspection_id=st.session_state.get("inspection_id"),
    )
