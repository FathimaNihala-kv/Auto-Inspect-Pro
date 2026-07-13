import streamlit as st

from utils import render_inspection_page


def render_tyres_wheels():
    render_inspection_page(
        "Tyres & Wheels",
        "Tyres & Wheels",
        ["Front Left", "Front Right", "Rear Left", "Rear Right", "Spare Tyre"],
        inspection_id=st.session_state.get("inspection_id"),
    )
