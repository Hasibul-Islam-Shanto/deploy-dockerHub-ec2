from app.database import get_db_connection


def get_all_students():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT s.id, s.name, s.created_at,
               (SELECT status FROM attendance a
                WHERE a.student_id = s.id AND a.date = CURDATE()
                LIMIT 1) AS today_status
        FROM students s
        ORDER BY s.name ASC
    """)
    students = cursor.fetchall()
    cursor.close()
    conn.close()
    return students


def get_student(student_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id, name, created_at FROM students WHERE id = %s", (student_id,))
    student = cursor.fetchone()
    cursor.close()
    conn.close()
    return student


def add_student(name):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO students (name) VALUES (%s)", (name,))
    student_id = cursor.lastrowid
    conn.commit()
    cursor.close()
    conn.close()
    return student_id


def update_student(student_id, name):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE students SET name = %s WHERE id = %s", (name, student_id))
    updated = cursor.rowcount > 0
    conn.commit()
    cursor.close()
    conn.close()
    return updated


def delete_student(student_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM students WHERE id = %s", (student_id,))
    deleted = cursor.rowcount > 0
    conn.commit()
    cursor.close()
    conn.close()
    return deleted


def mark_attendance(student_id, date, status="Present"):
    """Create or update attendance for one student on one date."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO attendance (student_id, date, status)
        VALUES (%s, %s, %s)
        ON DUPLICATE KEY UPDATE status = VALUES(status)
    """, (student_id, date, status))
    conn.commit()
    cursor.close()
    conn.close()


def delete_attendance(attendance_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM attendance WHERE id = %s", (attendance_id,))
    deleted = cursor.rowcount > 0
    conn.commit()
    cursor.close()
    conn.close()
    return deleted


def get_attendance(search=None, date_filter=None):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    query = """
        SELECT a.id AS attendance_id, s.id AS student_id, s.name, a.date, a.status
        FROM attendance a
        JOIN students s ON a.student_id = s.id
        WHERE 1=1
    """
    params = []

    if search:
        query += " AND s.name LIKE %s"
        params.append(f"%{search}%")

    if date_filter:
        query += " AND a.date = %s"
        params.append(date_filter)

    query += " ORDER BY a.date DESC, s.name ASC"

    cursor.execute(query, params)
    records = cursor.fetchall()
    cursor.close()
    conn.close()
    return records


def get_attendance_stats(start_date, end_date):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT status, COUNT(*) as count
        FROM attendance
        WHERE date BETWEEN %s AND %s
        GROUP BY status
    """, (start_date, end_date))
    data = {row["status"]: row["count"] for row in cursor.fetchall()}
    cursor.close()
    conn.close()
    return {"Present": data.get("Present", 0), "Absent": data.get("Absent", 0)}


def get_student_attendance(name, start_date, end_date):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT a.status, COUNT(*) as count
        FROM attendance a
        JOIN students s ON a.student_id = s.id
        WHERE s.name = %s AND a.date BETWEEN %s AND %s
        GROUP BY a.status
    """, (name, start_date, end_date))
    data = {row["status"]: row["count"] for row in cursor.fetchall()}
    cursor.close()
    conn.close()
    return {"Student": name, "Present": data.get("Present", 0), "Absent": data.get("Absent", 0)}


def get_dashboard_stats():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT COUNT(*) AS total FROM students")
    total_students = cursor.fetchone()["total"]

    cursor.execute("""
        SELECT status, COUNT(*) AS count
        FROM attendance
        WHERE date = CURDATE()
        GROUP BY status
    """)
    today = {row["status"]: row["count"] for row in cursor.fetchall()}

    cursor.close()
    conn.close()
    return {
        "total_students": total_students,
        "present_today": today.get("Present", 0),
        "absent_today": today.get("Absent", 0),
    }
