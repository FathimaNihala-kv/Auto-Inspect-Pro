import streamlit as st

from utils import render_inspection_page


def render_exterior():
    render_inspection_page(
        "Exterior",
        "Exterior",
        ["Front Bumper", "Rear Bumper", "Headlights", "Tail Lights", "Fog Lamps", "Mirrors", "Door Handles", "Windshield Wipers"],
        inspection_id=st.session_state.get("inspection_id"),
    )
