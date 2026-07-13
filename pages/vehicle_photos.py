import streamlit as st

from modules.database_functions import get_photos, save_photo
from modules.image_handler import process_image_upload


def render_vehicle_photos():
    st.title("📸 Vehicle Photos")
    st.caption("Upload multiple photos for each category and keep the inspection evidence organized.")

    inspection_id = st.session_state.get("inspection_id")
    if not inspection_id:
        st.info("Start a new inspection first.")
        return

    categories = [
        "Exterior Photos",
        "Interior Photos",
        "Engine Room / Under Hood",
        "Undercarriage",
        "VIN Plate",
        "Odometer",
        "Damage Photos",
        "Other Photos",
    ]
    category = st.selectbox("Select photo category", categories)
    uploaded_files = st.file_uploader(
        f"Upload photos for {category}",
        type=["jpg", "jpeg", "png", "webp"],
        accept_multiple_files=True,
    )
    if st.button("Save Photos"):
        if uploaded_files:
            for uploaded_file in uploaded_files:
                saved_path = process_image_upload(uploaded_file, inspection_id, category, category)
                if saved_path:
                    save_photo(inspection_id, category, saved_path, caption=category)
            st.success("Photos saved successfully")
        else:
            st.error("Please choose at least one image")

    st.markdown("---")
    st.subheader("Stored Photos")
    for cat in categories:
        photos = get_photos(inspection_id, category=cat)
        if photos:
            st.write(f"### {cat}")
            for photo in photos:
                st.image(photo["file_path"], width=220)
