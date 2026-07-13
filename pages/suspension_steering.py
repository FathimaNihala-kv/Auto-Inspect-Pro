import streamlit as st

from utils import render_inspection_page


def render_suspension_steering():
    render_inspection_page(
        "Suspension & Steering",
        "Suspension & Steering",
        ["Shock Absorbers", "Control Arms", "Steering Rack", "Bushes", "Wheel Alignment"],
        inspection_id=st.session_state.get("inspection_id"),
    )
