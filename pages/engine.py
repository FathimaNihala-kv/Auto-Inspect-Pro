import streamlit as st

from utils import render_inspection_page


def render_engine():
    render_inspection_page(
        "Engine",
        "Engine",
        ["Oil Leakage", "Coolant Leakage", "Battery", "Radiator", "Belts", "Mounts", "Air Filter", "Smoke", "Noise", "Idle", "Performance"],
        inspection_id=st.session_state.get("inspection_id"),
    )
