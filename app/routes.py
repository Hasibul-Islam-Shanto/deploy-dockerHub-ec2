from datetime import date, datetime

from flask import jsonify, render_template, request

from app import app
from app.models import (
    add_student,
    delete_attendance,
    delete_student,
    get_all_students,
    get_attendance,
    get_attendance_stats,
    get_dashboard_stats,
    get_student,
    get_student_attendance,
    mark_attendance,
    update_student,
)


@app.route("/")
def home():
    stats = get_dashboard_stats()
    return render_template("index.html", stats=stats)


@app.route("/students", methods=["GET"])
def list_students():
    search = request.args.get("search", "").strip()
    students = get_all_students()
    if search:
        students = [s for s in students if search.lower() in s["name"].lower()]
    return render_template("students.html", students=students)


@app.route("/register_student", methods=["POST"])
def register_student():
    data = request.get_json()
    name = (data.get("name") or "").strip()

    if not name:
        return jsonify({"error": "Name is required"}), 400

    student_id = add_student(name)
    mark_attendance(student_id, str(date.today()), "Present")

    return jsonify({"message": f"{name} registered and marked present for today."})


@app.route("/students/<int:student_id>", methods=["PUT"])
def edit_student(student_id):
    data = request.get_json()
    name = (data.get("name") or "").strip()

    if not name:
        return jsonify({"error": "Name is required"}), 400

    if not get_student(student_id):
        return jsonify({"error": "Student not found"}), 404

    update_student(student_id, name)
    return jsonify({"message": f"Student updated to {name}."})


@app.route("/students/<int:student_id>", methods=["DELETE"])
def remove_student(student_id):
    if not delete_student(student_id):
        return jsonify({"error": "Student not found"}), 404
    return jsonify({"message": "Student deleted successfully."})


@app.route("/mark_attendance", methods=["POST"])
def update_attendance_status():
    data = request.get_json()
    student_id = data.get("student_id")
    status = data.get("status")

    if not student_id:
        return jsonify({"error": "Student ID is required"}), 400

    if status not in ("Present", "Absent"):
        return jsonify({"error": "Status must be Present or Absent"}), 400

    if not get_student(student_id):
        return jsonify({"error": "Student not found"}), 404

    mark_attendance(student_id, str(date.today()), status)
    return jsonify({"message": f"Marked as {status} for today."})


@app.route("/attendance/<int:attendance_id>", methods=["DELETE"])
def remove_attendance(attendance_id):
    if not delete_attendance(attendance_id):
        return jsonify({"error": "Attendance record not found"}), 404
    return jsonify({"message": "Attendance record deleted."})


@app.route("/get_attendance", methods=["GET"])
def fetch_attendance():
    search = request.args.get("search", "").strip()
    date_filter = request.args.get("date", "").strip() or None
    records = get_attendance(search=search or None, date_filter=date_filter)
    return render_template("attendance.html", records=records)


@app.route("/analytics")
def analytics_page():
    students = get_all_students()
    return render_template("analytics.html", students=students)


@app.route("/attendance_stats", methods=["GET"])
def attendance_stats():
    start_date = request.args.get("start_date", "2023-01-01")
    end_date = request.args.get("end_date", datetime.today().strftime("%Y-%m-%d"))
    student_name = request.args.get("student_name") or None

    if student_name:
        stats = get_student_attendance(student_name, start_date, end_date)
    else:
        stats = get_attendance_stats(start_date, end_date)

    return jsonify(stats)
