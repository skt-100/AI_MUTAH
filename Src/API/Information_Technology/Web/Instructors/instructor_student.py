from API import settings as st
from flask import Blueprint, request, jsonify
import mysql.connector

instructor_student_bp = Blueprint('instructor_student', __name__)


def get_connection():
    return mysql.connector.connect(**st.DB_CONFIG)


# جلب المساقات التي يُدرِّسها المحاضر
@instructor_student_bp.route('/api/instructor/courses', methods=['POST'])
def get_instructor_courses():
    data = request.get_json() or {}
    instructor_id = data.get('instructor_id')

    if not instructor_id:
        return jsonify({"success": False, "message": "instructor_id مطلوب"}), 400

    try:
        with get_connection() as conn:
            with conn.cursor(dictionary=True) as cursor:
                cursor.execute("""
                    SELECT DISTINCT c.course_id, c.course_name
                    FROM sections s
                    JOIN courses c ON s.course_id = c.course_id
                    WHERE s.instructor_id = %s
                    ORDER BY c.course_name
                """, (instructor_id,))
                courses = cursor.fetchall()

        return jsonify({"success": True, "courses": courses})

    except mysql.connector.Error as err:
        return jsonify({"success": False, "message": f"خطأ في قاعدة البيانات: {str(err)}"}), 500


# جلب الشعب التابعة للمحاضر في مادة معينة
@instructor_student_bp.route('/api/instructor/sections', methods=['POST'])
def get_instructor_sections():
    data = request.get_json() or {}
    instructor_id = data.get('instructor_id')
    course_id     = data.get('course_id')

    if not instructor_id or not course_id:
        return jsonify({"success": False, "message": "instructor_id و course_id مطلوبان"}), 400

    try:
        with get_connection() as conn:
            with conn.cursor(dictionary=True) as cursor:
                cursor.execute("""
                    SELECT section_id, section_number
                    FROM sections
                    WHERE instructor_id = %s AND course_id = %s
                    ORDER BY section_number
                """, (instructor_id, course_id))
                sections = cursor.fetchall()

        return jsonify({"success": True, "sections": sections})

    except mysql.connector.Error as err:
        return jsonify({"success": False, "message": f"خطأ في قاعدة البيانات: {str(err)}"}), 500


# جلب قائمة الطلاب في الشعبة مع غياباتهم وعلاماتهم
@instructor_student_bp.route('/api/instructor/students_list', methods=['POST'])
def get_students_list():
    data = request.get_json() or {}
    section_id = data.get('section_id')

    if not section_id:
        return jsonify({"success": False, "message": "section_id مطلوب"}), 400

    try:
        with get_connection() as conn:
            with conn.cursor(dictionary=True) as cursor:
                cursor.execute("""
                    SELECT
                        s.student_id,
                        s.full_name,
                        COALESCE(a.absences_count, 0)      AS absences_count,
                        COALESCE(g.participation_grade, 0) AS participation,
                        COALESCE(g.midterm_grade, 0)       AS midterm,
                        COALESCE(g.final_grade, 0)         AS final
                    FROM enrollments e
                    JOIN students s ON e.student_id = s.student_id
                    LEFT JOIN attendance a ON a.student_id = s.student_id AND a.section_id = e.section_id
                    LEFT JOIN grades g     ON g.student_id = s.student_id AND g.section_id = e.section_id
                    WHERE e.section_id = %s
                    ORDER BY s.full_name
                """, (section_id,))
                students = cursor.fetchall()

        return jsonify({"success": True, "students": students})

    except mysql.connector.Error as err:
        return jsonify({"success": False, "message": f"خطأ في قاعدة البيانات: {str(err)}"}), 500


# حفظ الغيابات أو العلامات
@instructor_student_bp.route('/api/instructor/save_records', methods=['POST'])
def save_records():
    data      = request.get_json() or {}
    section_id = data.get('section_id')
    mode       = data.get('mode')
    records    = data.get('records', [])

    if not section_id or not mode or not records:
        return jsonify({"success": False, "message": "البيانات المطلوبة ناقصة"}), 400

    try:
        with get_connection() as conn:
            with conn.cursor() as cursor:
                if mode == 'attendance':
                    for rec in records:
                        cursor.execute("""
                            INSERT INTO attendance (student_id, section_id, absences_count)
                            VALUES (%s, %s, %s)
                            ON DUPLICATE KEY UPDATE absences_count = VALUES(absences_count)
                        """, (rec['student_id'], section_id, rec['absences_count']))
                else:
                    for rec in records:
                        cursor.execute("""
                            INSERT INTO grades
                                (student_id, section_id, participation_grade, midterm_grade, final_grade)
                            VALUES (%s, %s, %s, %s, %s)
                            ON DUPLICATE KEY UPDATE
                                participation_grade = VALUES(participation_grade),
                                midterm_grade       = VALUES(midterm_grade),
                                final_grade         = VALUES(final_grade)
                        """, (rec['student_id'], section_id,
                              rec['participation'], rec['midterm'], rec['final']))
            conn.commit()

        return jsonify({"success": True})

    except mysql.connector.Error as err:
        return jsonify({"success": False, "message": f"خطأ في قاعدة البيانات: {str(err)}"}), 500
