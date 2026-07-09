import mysql.connector
import os

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", "rootpassword"),
    "database": os.getenv("DB_NAME", "attendance_db"),
}


def get_db_connection():
    conn = mysql.connector.connect(**DB_CONFIG)
    return conn


def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("CREATE DATABASE IF NOT EXISTS attendance_db")
    cursor.execute("USE attendance_db")

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS students (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(100) NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    cursor.execute("""
        SELECT COUNT(*) FROM information_schema.columns
        WHERE table_schema = DATABASE()
          AND table_name = 'students'
          AND column_name = 'created_at'
    """)
    if cursor.fetchone()[0] == 0:
        cursor.execute("""
            ALTER TABLE students
            ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS attendance (
        id INT AUTO_INCREMENT PRIMARY KEY,
        student_id INT NOT NULL,
        date DATE NOT NULL,
        status ENUM('Present', 'Absent') DEFAULT 'Present',
        FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE
    )
    """)

    # Remove duplicate attendance rows before adding unique constraint
    cursor.execute("""
        DELETE a1 FROM attendance a1
        INNER JOIN attendance a2
        ON a1.student_id = a2.student_id
           AND a1.date = a2.date
           AND a1.id < a2.id
    """)

    cursor.execute("""
        SELECT COUNT(*) FROM information_schema.statistics
        WHERE table_schema = DATABASE()
          AND table_name = 'attendance'
          AND index_name = 'unique_student_date'
    """)
    if cursor.fetchone()[0] == 0:
        cursor.execute("""
            ALTER TABLE attendance
            ADD UNIQUE KEY unique_student_date (student_id, date)
        """)

    conn.commit()
    cursor.close()
    conn.close()
