import os
import json
import uuid
from datetime import datetime
from pathlib import Path

import streamlit as st

from config import CONDITION_OPTIONS, SEVERITY_OPTIONS
from modules.database_functions import (
    save_inspection_item,
    get_inspection_items,
    save_photo,
    get_photos,
)
from modules.image_handler import process_image_upload


def load_css():
    from config import STYLES_PATH

    if STYLES_PATH.exists():
        with open(STYLES_PATH, "r", encoding="utf-8") as fh:
            st.markdown(f"<style>{fh.read()}</style>", unsafe_allow_html=True)


def ensure_session():
    defaults = {
        "inspection_id": None,
        "vehicle_id": None,
        "sidebar_nav": "Dashboard",
        "redirect_page": None,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def reset_inspection_session():
    st.session_state.inspection_id = None
    st.session_state.vehicle_id = None


def render_sidebar(navigation_items):
    from pathlib import Path

    logo_path = Path("assets/logo.png")
    if logo_path.exists():
        st.sidebar.image(str(logo_path), use_container_width=True)
    else:
        st.sidebar.markdown("### 🚗 AutoInspect Pro")
    st.sidebar.title("AutoInspect Pro")
    st.sidebar.caption("Premium Vehicle Inspection Platform")
    selected = st.sidebar.radio("Navigation", navigation_items, key="sidebar_nav")
    st.sidebar.markdown("---")
    st.sidebar.button("New Inspection", on_click=reset_inspection_session)
    return selected


def render_inspection_page(page_title, category, parts, inspection_id=None, include_photo_uploader=True):
    if not inspection_id:
        st.info("Start a new inspection from the Vehicle Information page first.")
        return

    st.header(page_title)
    st.caption("Capture the current condition, severity, remarks, and supporting images for each item.")

    for part in parts:
        with st.expander(part, expanded=False):
            col1, col2 = st.columns([1, 1])
            condition = col1.selectbox("Condition", CONDITION_OPTIONS, key=f"{category}_{part}_condition")
            severity = col2.selectbox("Severity", SEVERITY_OPTIONS, key=f"{category}_{part}_severity")
            remarks = st.text_area("Remarks", key=f"{category}_{part}_remarks")
            uploaded_files = st.file_uploader(
                f"Upload photos for {part}",
                type=["jpg", "jpeg", "png", "webp"],
                accept_multiple_files=True,
                key=f"{category}_{part}_upload",
            )
            if st.button(f"Save {part}", key=f"save_{category}_{part}"):
                if uploaded_files:
                    for uploaded_file in uploaded_files:
                        saved_path = process_image_upload(uploaded_file, inspection_id, category, part)
                        if saved_path:
                            save_photo(inspection_id, category, saved_path, caption=part)
                save_inspection_item(
                    inspection_id=inspection_id,
                    category=category,
                    part_name=part,
                    condition=condition,
                    severity=severity,
                    remarks=remarks,
                )
                st.success(f"{part} saved successfully.")

    if include_photo_uploader:
        uploaded_files = st.file_uploader(
            "Upload supporting photos for this section",
            type=["jpg", "jpeg", "png", "webp"],
            accept_multiple_files=True,
            key=f"{category}_section_upload",
        )
        if st.button(f"Save section photos for {category}", key=f"{category}_section_photos"):
            if uploaded_files:
                for uploaded_file in uploaded_files:
                    saved_path = process_image_upload(uploaded_file, inspection_id, category, category)
                    if saved_path:
                        save_photo(inspection_id, category, saved_path, caption=category)
                st.success("Section photos saved successfully.")

    st.markdown("---")
    st.subheader("Saved findings")
    items = get_inspection_items(inspection_id, category=category)
    if items:
        for item in items:
            st.write(f"- {item['part_name']} | Condition: {item['condition']} | Severity: {item['severity']}")
    else:
        st.info("No findings saved for this section yet.")


def get_dashboard_metrics():
    from modules.database_functions import get_inspection_summary_counts

    return get_inspection_summary_counts()
