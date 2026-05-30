from API import settings as st
from flask import Blueprint, request, jsonify
import mysql.connector

instructor_pages_bp = Blueprint('instructor_pages', __name__)


def get_connection():
    return mysql.connector.connect(**st.DB_CONFIG)


@instructor_pages_bp.route('/api/instructor/dashboard_stats', methods=['POST'])
def get_instructor_dashboard_stats():
    data = request.get_json() or {}
    instructor_id = data.get('instructor_id')

    if not instructor_id:
        return jsonify({"success": False, "message": "instructor_id مطلوب"}), 400

    try:
        with get_connection() as conn:
            with conn.cursor(dictionary=True) as cursor:

                # 1. عدد المواد المختلفة التي يدرّسها المحاضر
                cursor.execute("""
                    SELECT COUNT(DISTINCT course_id) AS courses_count
                    FROM sections
                    WHERE instructor_id = %s
                """, (instructor_id,))
                courses_count = cursor.fetchone()['courses_count']

                # 2. عدد الشعب المخصصة للمحاضر
                cursor.execute("""
                    SELECT COUNT(*) AS sections_count
                    FROM sections
                    WHERE instructor_id = %s
                """, (instructor_id,))
                sections_count = cursor.fetchone()['sections_count']

                # 3. إجمالي الطلاب في جميع شعب المحاضر
                cursor.execute("""
                    SELECT COUNT(e.enrollment_id) AS total_students
                    FROM enrollments e
                    JOIN sections s ON e.section_id = s.section_id
                    WHERE s.instructor_id = %s
                """, (instructor_id,))
                total_students = cursor.fetchone()['total_students']

                # 4. طلبات توسعة الشعبة المعلقة الخاصة بشعب المحاضر
                cursor.execute("""
                    SELECT COUNT(*) AS pending_requests
                    FROM registration_requests rr
                    JOIN sections s ON rr.section_id = s.section_id
                    WHERE s.instructor_id = %s AND rr.status = 'معلق'
                """, (instructor_id,))
                pending_requests = cursor.fetchone()['pending_requests']

                # 5. تفاصيل كل شعبة مع عدد الطلاب والطاقة الاستيعابية
                cursor.execute("""
                    SELECT
                        s.section_id,
                        s.section_number,
                        s.capacity,
                        c.course_id,
                        c.course_name,
                        COUNT(e.enrollment_id) AS enrolled_count
                    FROM sections s
                    JOIN courses c ON s.course_id = c.course_id
                    LEFT JOIN enrollments e ON e.section_id = s.section_id
                    WHERE s.instructor_id = %s
                    GROUP BY s.section_id, s.section_number, s.capacity,
                             c.course_id, c.course_name
                    ORDER BY c.course_name, s.section_number
                """, (instructor_id,))
                sections = cursor.fetchall()

        return jsonify({
            "success": True,
            "stats": {
                "courses_count":   courses_count,
                "sections_count":  sections_count,
                "total_students":  total_students,
                "pending_requests": pending_requests
            },
            "sections": sections
        })

    except mysql.connector.Error as err:
        return jsonify({"success": False, "message": f"خطأ في قاعدة البيانات: {str(err)}"}), 500
