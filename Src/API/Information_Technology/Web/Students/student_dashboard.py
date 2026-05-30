from API import settings as st
from flask import Blueprint, request, jsonify
import mysql.connector

student_dashboard_bp = Blueprint('student_dashboard', __name__)


def get_connection():
    return mysql.connector.connect(**st.DB_CONFIG)


# جلب إحصائيات الطالب للبطاقات
@student_dashboard_bp.route('/api/student_dashboard_info', methods=['POST'])
def student_dashboard_info():
    data = request.get_json() or {}
    student_id = data.get('student_id')

    if not student_id:
        return jsonify({"success": False, "message": "الرقم الجامعي مطلوب"}), 400

    try:
        with get_connection() as conn:
            with conn.cursor(dictionary=True) as cursor:
                
                # جلب بيانات الطالب الأساسية
                cursor.execute("""
                    SELECT gpa, completed_hours, academic_year 
                    FROM students 
                    WHERE student_id = %s
                """, (student_id,))
                student = cursor.fetchone()

                if not student:
                    return jsonify({"success": False, "message": "الطالب غير موجود"}), 404

                # جلب جميع العدادات باستعلام واحد
                cursor.execute("""
                    SELECT 
                        (SELECT COUNT(*) FROM registration_requests WHERE student_id = %s AND status = 'معلق') AS pending_count,
                        (SELECT COUNT(*) FROM enrollments WHERE student_id = %s) AS enrolled_count,
                        (SELECT COALESCE(SUM(c.credit_hours), 0) FROM enrollments e 
                         JOIN sections s ON e.section_id = s.section_id 
                         JOIN courses c ON s.course_id = c.course_id 
                         WHERE e.student_id = %s) AS enrolled_hours,
                        (SELECT COUNT(*) FROM student_records WHERE student_id = %s AND final_grade >= 50) AS passed_courses
                """, (student_id, student_id, student_id, student_id))
                
                stats = cursor.fetchone()

        return jsonify({
            "success": True,
            "data": {
                "gpa":             float(student['gpa']),
                "completed_hours": int(student['completed_hours']),
                "academic_year":   int(student['academic_year']),
                "pending_count":   int(stats['pending_count']),
                "enrolled_count":  int(stats['enrolled_count']),
                "enrolled_hours":  int(stats['enrolled_hours']),
                "passed_courses":  int(stats['passed_courses']),
            }
        })

    except mysql.connector.Error as err:
        return jsonify({"success": False, "message": f"خطأ في قاعدة البيانات: {str(err)}"}), 500


# جلب المواد المسجلة للفصل الحالي
@student_dashboard_bp.route('/api/student_dashboard_courses', methods=['POST'])
def student_dashboard_courses():
    data = request.get_json() or {}
    student_id = data.get('student_id')

    if not student_id:
        return jsonify({"success": False, "message": "الرقم الجامعي مطلوب"}), 400

    try:
        with get_connection() as conn:
            with conn.cursor(dictionary=True) as cursor:
                # استعلام جلب تفاصيل المواد والمدرسين
                cursor.execute("""
                    SELECT
                        c.course_id,
                        c.course_name,
                        c.credit_hours,
                        i.full_name  AS instructor_name,
                        s.days,
                        s.start_time,
                        s.end_time,
                        s.room
                    FROM enrollments e
                    JOIN sections    s ON e.section_id    = s.section_id
                    JOIN courses     c ON s.course_id     = c.course_id
                    JOIN instructors i ON s.instructor_id = i.instructors_id
                    WHERE e.student_id = %s
                """, (student_id,))
                rows = cursor.fetchall()

        courses = []
        for row in rows:
            # تنسيق وقت البداية والنهاية
            start = str(row['start_time'])[:5] if row['start_time'] else '—'
            end   = str(row['end_time'])[:5]   if row['end_time']   else '—'
            
            courses.append({
                "course_id":        row['course_id'],
                "course_name":      row['course_name'],
                "credit_hours":     int(row['credit_hours']),
                "instructor_name":  row['instructor_name'],
                "days":             row['days'],
                "time":             f"{start} - {end}",
                "room":             row['room'],
            })

        return jsonify({"success": True, "courses": courses})

    except mysql.connector.Error as err:
        return jsonify({"success": False, "message": f"خطأ في قاعدة البيانات: {str(err)}"}), 500


# جلب الإشعارات الخاصة بالطالب
@student_dashboard_bp.route('/api/student_dashboard_notifications', methods=['POST'])
def student_dashboard_notifications():
    data = request.get_json() or {}
    student_id = data.get('student_id')

    if not student_id:
        return jsonify({"success": False, "message": "الرقم الجامعي مطلوب"}), 400

    try:
        with get_connection() as conn:
            with conn.cursor(dictionary=True) as cursor:
                cursor.execute("""
                    SELECT
                        pn.notification_id,
                        pn.change_type,
                        pn.old_value,
                        pn.new_value,
                        pn.message,
                        pn.sent_at,
                        c.course_name
                    FROM private_notification pn
                    JOIN sections s ON pn.section_id = s.section_id
                    JOIN courses  c ON s.course_id   = c.course_id
                    WHERE pn.student_id = %s
                    ORDER BY pn.sent_at DESC
                    LIMIT 20
                """, (student_id,))
                rows = cursor.fetchall()

        for row in rows:
            if row['sent_at']:
                row['sent_at'] = row['sent_at'].strftime('%Y-%m-%d %H:%M')

        return jsonify({
            "success": True,
            "private": rows,
            "public":  []
        })

    except mysql.connector.Error as err:
        return jsonify({"success": False, "message": f"خطأ في قاعدة البيانات: {str(err)}"}), 500
