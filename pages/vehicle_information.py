import streamlit as st

from modules.database_functions import create_inspection, create_vehicle, get_vehicle
from utils import ensure_session


def render_vehicle_information():
    st.title("🚗 Vehicle Information")
    st.caption("Capture the core vehicle and customer details required for the inspection report.")

    vehicle_id = st.session_state.get("vehicle_id")
    inspection_id = st.session_state.get("inspection_id")
    existing_vehicle = None
    if vehicle_id:
        existing_vehicle = get_vehicle(vehicle_id)

    with st.form("vehicle_info_form"):
        inspection_date = st.date_input("Inspection Date")
        inspector_name = st.text_input("Inspector Name", value=st.session_state.user.get("full_name", "") if st.session_state.get("user") else "")
        customer_name = st.text_input("Customer Name")
        customer_contact = st.text_input("Customer Contact")
        make = st.text_input("Vehicle Make")
        model = st.text_input("Vehicle Model")
        year = st.text_input("Year")
        vin = st.text_input("VIN")
        engine = st.text_input("Engine")
        odometer = st.text_input("Odometer Reading")
        transmission = st.text_input("Transmission Type")
        fuel_type = st.text_input("Fuel Type")
        color = st.text_input("Color")
        interior_type = st.text_input("Interior Type")
        accident_history = st.text_input("Accident History")
        registration_number = st.text_input("Registration Number")
        engine_number = st.text_input("Engine Number")
        origin_of_vehicle = st.text_input("Origin of Vehicle")
        vehicle_category = st.text_input("Vehicle Category")
        remarks = st.text_area("Remarks")
        submitted = st.form_submit_button("Save Vehicle Information")

    if submitted:
        required_fields = [make, model, year, vin, inspector_name, customer_name]
        if any(not field for field in required_fields):
            st.error("Please fill in the required fields before continuing.")
            return
        vehicle_data = {
            "make": make,
            "model": model,
            "year": year,
            "vin": vin,
            "engine": engine,
            "odometer": odometer,
            "transmission": transmission,
            "fuel_type": fuel_type,
            "color": color,
            "interior_type": interior_type,
            "accident_history": accident_history,
            "registration_number": registration_number,
            "engine_number": engine_number,
            "origin_of_vehicle": origin_of_vehicle,
            "vehicle_category": vehicle_category,
            "remarks": remarks,
            "inspection_date": inspection_date.strftime("%Y-%m-%d"),
            "inspector_name": inspector_name,
            "customer_name": customer_name,
            "customer_contact": customer_contact,
        }
        if existing_vehicle and vehicle_id:
            st.info("Vehicle already captured. Proceed to the next inspection page.")
        else:
            vehicle_id = create_vehicle(vehicle_data)
            st.session_state.vehicle_id = vehicle_id
            inspection_id = create_inspection(vehicle_id, inspector_name)
            st.session_state.inspection_id = inspection_id
            st.success("Vehicle information saved. You can now continue to the inspection sections.")
