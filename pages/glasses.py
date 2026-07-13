import streamlit as st

from utils import render_inspection_page


def render_glasses():
    render_inspection_page(
        "Glasses",
        "Glasses",
        ["Front Windshield", "Rear Windshield", "Left Glass", "Right Glass", "Sunroof"],
        inspection_id=st.session_state.get("inspection_id"),
    )
