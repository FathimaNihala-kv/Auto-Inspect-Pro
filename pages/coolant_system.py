import streamlit as st

from utils import render_inspection_page


def render_coolant_system():
    render_inspection_page(
        "Coolant System",
        "Coolant System",
        ["Coolant Level", "Radiator", "Water Pump", "Thermostat", "Hoses", "Leakage"],
        inspection_id=st.session_state.get("inspection_id"),
    )
