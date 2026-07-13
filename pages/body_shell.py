import streamlit as st

from utils import render_inspection_page


def render_body_shell():
    render_inspection_page(
        "Body Shell",
        "Body Shell",
        ["Roof", "Bonnet", "Boot", "Doors", "Pillars", "Quarter Panels", "Aprons", "Frame"],
        inspection_id=st.session_state.get("inspection_id"),
    )
