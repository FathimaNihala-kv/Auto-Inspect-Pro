from datetime import datetime
from pathlib import Path
import sqlite3
import time

from database import get_connection
from config import DATABASE_PATH


def create_vehicle(vehicle_data: dict):
    query = """
        INSERT INTO vehicles (
            make, model, year, vin, engine, odometer, transmission, fuel_type, color,
            interior_type, accident_history, registration_number, engine_number,
            origin_of_vehicle, vehicle_category, remarks, inspection_date,
            inspector_name, customer_name, customer_contact
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
    params = (
        vehicle_data.get("make"),
        vehicle_data.get("model"),
        vehicle_data.get("year"),
        vehicle_data.get("vin"),
        vehicle_data.get("engine"),
        vehicle_data.get("odometer"),
        vehicle_data.get("transmission"),
        vehicle_data.get("fuel_type"),
        vehicle_data.get("color"),
        vehicle_data.get("interior_type"),
        vehicle_data.get("accident_history"),
        vehicle_data.get("registration_number"),
        vehicle_data.get("engine_number"),
        vehicle_data.get("origin_of_vehicle"),
        vehicle_data.get("vehicle_category"),
        vehicle_data.get("remarks"),
        vehicle_data.get("inspection_date"),
        vehicle_data.get("inspector_name"),
        vehicle_data.get("customer_name"),
        vehicle_data.get("customer_contact"),
    )
    for attempt in range(3):
        try:
            with get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, params)
                vehicle_id = cursor.lastrowid
            return vehicle_id
        except sqlite3.OperationalError:
            if attempt < 2:
                time.sleep(0.1 * (attempt + 1))
                continue
            raise


def get_vehicle(vehicle_id: int):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM vehicles WHERE vehicle_id = ?", (vehicle_id,))
        vehicle = cursor.fetchone()
    return dict(vehicle) if vehicle else None


def create_inspection(vehicle_id: int, inspector_name: str):
    query = "INSERT INTO inspections (vehicle_id, inspector_name, overall_status, completion_percentage) VALUES (?, ?, ?, ?)"
    params = (vehicle_id, inspector_name, "Pending", 0.0)
    for attempt in range(3):
        try:
            with get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, params)
                inspection_id = cursor.lastrowid
            return inspection_id
        except sqlite3.OperationalError:
            if attempt < 2:
                time.sleep(0.1 * (attempt + 1))
                continue
            raise


def get_inspection(inspection_id: int):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM inspections WHERE inspection_id = ?", (inspection_id,))
        inspection = cursor.fetchone()
    return dict(inspection) if inspection else None


def save_inspection_item(inspection_id, category, part_name, condition, severity, remarks):
    query = """
        INSERT INTO inspection_items (inspection_id, category, part_name, condition, severity, remarks)
        VALUES (?, ?, ?, ?, ?, ?)
        """
    params = (inspection_id, category, part_name, condition, severity, remarks)
    for attempt in range(3):
        try:
            with get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, params)
            return
        except sqlite3.OperationalError:
            if attempt < 2:
                time.sleep(0.1 * (attempt + 1))
                continue
            raise


def get_inspection_items(inspection_id, category=None):
    with get_connection() as conn:
        cursor = conn.cursor()
        if category:
            cursor.execute("SELECT * FROM inspection_items WHERE inspection_id = ? AND category = ?", (inspection_id, category))
        else:
            cursor.execute("SELECT * FROM inspection_items WHERE inspection_id = ?", (inspection_id,))
        items = cursor.fetchall()
    return [dict(item) for item in items]


def save_photo(inspection_id, category, file_path, caption=None):
    query = "INSERT INTO photos (inspection_id, category, file_path, caption) VALUES (?, ?, ?, ?)"
    params = (inspection_id, category, str(file_path), caption)
    for attempt in range(3):
        try:
            with get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, params)
            return
        except sqlite3.OperationalError:
            if attempt < 2:
                time.sleep(0.1 * (attempt + 1))
                continue
            raise


def get_photos(inspection_id, category=None):
    with get_connection() as conn:
        cursor = conn.cursor()
        if category:
            cursor.execute("SELECT * FROM photos WHERE inspection_id = ? AND category = ?", (inspection_id, category))
        else:
            cursor.execute("SELECT * FROM photos WHERE inspection_id = ?", (inspection_id,))
        photos = cursor.fetchall()
    return [dict(photo) for photo in photos]


def save_report(inspection_id, report_name, pdf_path, report_notes=None):
    query1 = "INSERT INTO reports (inspection_id, report_name, pdf_path, report_notes) VALUES (?, ?, ?, ?)"
    query2 = "INSERT INTO report_history (inspection_id, action) VALUES (?, ?)"
    params1 = (inspection_id, report_name, str(pdf_path), report_notes)
    params2 = (inspection_id, 'Generated report')
    for attempt in range(3):
        try:
            with get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query1, params1)
                cursor.execute(query2, params2)
            return
        except sqlite3.OperationalError:
            if attempt < 2:
                time.sleep(0.1 * (attempt + 1))
                continue
            raise


def update_report(report_id, report_name, pdf_path, report_notes=None):
    query1 = "UPDATE reports SET report_name = ?, pdf_path = ?, report_notes = ?, created_at = CURRENT_TIMESTAMP WHERE report_id = ?"
    query2 = "INSERT INTO report_history (inspection_id, action) VALUES ((SELECT inspection_id FROM reports WHERE report_id = ?), ?)"
    params1 = (report_name, str(pdf_path), report_notes, report_id)
    params2 = (report_id, 'Updated report')
    for attempt in range(3):
        try:
            with get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query1, params1)
                cursor.execute(query2, params2)
            return
        except sqlite3.OperationalError:
            if attempt < 2:
                time.sleep(0.1 * (attempt + 1))
                continue
            raise


def get_report(report_id):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM reports WHERE report_id = ?", (report_id,))
        report = cursor.fetchone()
    return dict(report) if report else None


def get_report_by_inspection(inspection_id):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM reports WHERE inspection_id = ? ORDER BY created_at DESC", (inspection_id,))
        reports = cursor.fetchall()
    return [dict(report) for report in reports]


def get_reports(inspection_id=None):
    with get_connection() as conn:
        cursor = conn.cursor()
        if inspection_id is None:
            cursor.execute("SELECT * FROM reports ORDER BY created_at DESC")
        else:
            cursor.execute("SELECT * FROM reports WHERE inspection_id = ? ORDER BY created_at DESC", (inspection_id,))
        reports = cursor.fetchall()
    return [dict(report) for report in reports]


def get_inspection_summary_counts():
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) AS total FROM inspections")
        total = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) AS today FROM inspections WHERE date(created_at) = date('now')")
        today = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) AS pending FROM inspections WHERE overall_status = 'Pending'")
        pending = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) AS completed FROM inspections WHERE overall_status = 'Completed'")
        completed = cursor.fetchone()[0]
    return {"total": total, "today": today, "pending": pending, "completed": completed}


def search_inspections(query: str):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
        SELECT i.inspection_id, v.vin, v.registration_number, v.customer_name, v.inspection_date, i.overall_status
        FROM inspections i
        JOIN vehicles v ON v.vehicle_id = i.vehicle_id
        WHERE CAST(i.inspection_id AS TEXT) LIKE ?
        OR v.vin LIKE ?
        OR v.registration_number LIKE ?
        OR v.customer_name LIKE ?
        OR v.inspection_date LIKE ?
        """,
            (f"%{query}%", f"%{query}%", f"%{query}%", f"%{query}%", f"%{query}%"),
        )
        results = cursor.fetchall()
    return [dict(item) for item in results]


def update_inspection_summary(inspection_id: int, score: float, status: str, completion: float, remarks: str):
    query = "UPDATE inspections SET overall_score = ?, overall_status = ?, completion_percentage = ?, remarks = ?, updated_at = ? WHERE inspection_id = ?"
    params = (score, status, completion, remarks, datetime.utcnow().isoformat(), inspection_id)
    for attempt in range(3):
        try:
            with get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, params)
            return
        except sqlite3.OperationalError:
            if attempt < 2:
                time.sleep(0.1 * (attempt + 1))
                continue
            raise
