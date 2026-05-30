import mysql.connector
import settings as st


def get_connection():
    return mysql.connector.connect(
        host=st.DB_HOST, user=st.DB_USER,
        password=st.DB_PASSWORD, database=st.DB_NAME
    )


def get_enrolled_students(section_id):
    """جلب بيانات الطلاب المسجلين في الشعبة"""
    conn   = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT s.student_id, s.full_name, s.email
        FROM enrollments e
        JOIN students s ON e.student_id = s.student_id
        WHERE e.section_id = %s
    """, (section_id,))
    students = cursor.fetchall()
    cursor.close()
    conn.close()
    return students


def get_course_name(section_id):
    """جلب اسم المادة المرتبطة بالشعبة"""
    conn   = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT c.course_name
        FROM sections s
        JOIN courses c ON s.course_id = c.course_id
        WHERE s.section_id = %s
    """, (section_id,))
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    return result["course_name"] if result else "غير معروف"


def get_section(section_id):
    """جلب بيانات الشعبة الحالية"""
    conn   = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM sections WHERE section_id = %s", (section_id,))
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    return result


def update_section(section_id, change_type, new_value):
    """تحديث بيانات الشعبة في قاعدة البيانات"""
    column_map = {
        "وقت":  "start_time",
        "قاعة": "room",
        "مدرس": "instructor_id",
        "يوم":  "days",
    }

    column = column_map.get(change_type)
    if not column:
        return False

    conn   = get_connection()
    cursor = conn.cursor()
    cursor.execute(f"""
        UPDATE sections SET {column} = %s
        WHERE section_id = %s
    """, (new_value, section_id))
    conn.commit()
    cursor.close()
    conn.close()
    return True


def save_notification(student_id, section_id, change_type, old_value, new_value, message):
    """حفظ سجل الإشعار في قاعدة البيانات"""
    conn   = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO private_notification
        (student_id, section_id, change_type, old_value, new_value, message)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (student_id, section_id, change_type, old_value, new_value, message))
    conn.commit()
    cursor.close()
    conn.close()
