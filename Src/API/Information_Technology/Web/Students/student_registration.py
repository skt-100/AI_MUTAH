from flask import Blueprint, request, jsonify
import mysql.connector
from API import settings as st

student_registration_bp = Blueprint('student_registration', __name__)

def get_connection():
    return mysql.connector.connect(**st.DB_CONFIG)


# ── معادلة الأولوية (مطابقة لـ Registrations/priority.py) ──────────────────
_W_YEAR, _W_HOURS, _W_FAIL, _W_GPA = 0.30, 0.25, 0.25, 0.20
_TOTAL_HOURS = 132
_THRESHOLD_AUTO, _THRESHOLD_HIGH, _THRESHOLD_NORMAL = 0.75, 0.50, 0.25

def _calc_priority(academic_year, completed_hours, fail_count, gpa):
    year_map    = {4: 1.0, 3: 0.75, 2: 0.50, 1: 0.25}
    year_score  = year_map.get(int(academic_year), 0.25)
    hours_score = round(min(int(completed_hours), _TOTAL_HOURS) / _TOTAL_HOURS, 2)
    fail_score  = 0.0 if fail_count == 0 else (0.5 if fail_count == 1 else 1.0)
    gpa_score   = round(min(float(gpa), 100) / 100, 2)
    return round(year_score * _W_YEAR + hours_score * _W_HOURS +
                 fail_score * _W_FAIL + gpa_score * _W_GPA, 4)

def _priority_label(score):
    if score >= _THRESHOLD_AUTO:   return "تسجيل فوري"
    if score >= _THRESHOLD_HIGH:   return "انتظار أولوية عالية"
    if score >= _THRESHOLD_NORMAL: return "انتظار عادية"
    return "آخر القائمة"


# 1. جلب طلبات الانتظار
@student_registration_bp.route('/api/get_pending_requests', methods=['POST'])
def get_pending_requests():
    try:
        data = request.get_json()
        student_id = data.get('student_id')

        if not student_id:
            return jsonify({"success": False, "message": "الرقم الجامعي مطلوب"}), 400

        with get_connection() as conn:
            with conn.cursor(dictionary=True) as cursor:
                query = """
                    SELECT r.request_id,
                           c.course_id, c.course_name, c.credit_hours,
                           s.section_number, s.days, s.room,
                           CONCAT(s.start_time, ' - ', s.end_time) AS time,
                           r.priority_score
                    FROM registration_requests r
                    JOIN sections s ON r.section_id = s.section_id
                    JOIN courses  c ON s.course_id  = c.course_id
                    WHERE r.student_id = %s AND r.status = 'معلق'
                    ORDER BY r.priority_score DESC
                """
                cursor.execute(query, (student_id,))
                requests_list = cursor.fetchall()

        return jsonify({"success": True, "requests": requests_list}), 200

    except mysql.connector.Error as err:
        return jsonify({"success": False, "message": f"خطأ في قاعدة البيانات: {str(err)}"}), 500


# 2. جلب المواد المسجلة والمثبتة
@student_registration_bp.route('/api/get_registered_enrollments', methods=['POST'])
def get_registered_enrollments():
    try:
        data = request.get_json()
        student_id = data.get('student_id')

        if not student_id:
            return jsonify({"success": False, "message": "الرقم الجامعي مطلوب"}), 400

        with get_connection() as conn:
            with conn.cursor(dictionary=True) as cursor:
                query = """
                    SELECT c.course_id, c.course_name, c.credit_hours,
                           s.section_number, s.days, s.room,
                           CONCAT(s.start_time, ' - ', s.end_time) AS time,
                           'مثبت' AS status
                    FROM enrollments e
                    JOIN sections s ON e.section_id = s.section_id
                    JOIN courses  c ON s.course_id  = c.course_id
                    WHERE e.student_id = %s
                """
                cursor.execute(query, (student_id,))
                enrollments_list = cursor.fetchall()

        return jsonify({"success": True, "enrollments": enrollments_list}), 200

    except mysql.connector.Error as err:
        return jsonify({"success": False, "message": f"خطأ في قاعدة البيانات: {str(err)}"}), 500


# 3. إضافة طلب تسجيل مع حساب الأولوية
@student_registration_bp.route('/api/add_registration_request', methods=['POST'])
def add_registration_request():
    try:
        data           = request.get_json()
        student_id     = data.get('student_id')
        course_id      = data.get('course_id')
        section_number = int(data.get('section_number', 0))

        if not all([student_id, course_id, section_number]):
            return jsonify({"success": False, "message": "جميع الحقول مطلوبة"}), 400

        force_specialization = data.get('force_specialization', False)

        with get_connection() as conn:
            with conn.cursor() as cursor:

                # أ. جلب section_id
                cursor.execute(
                    "SELECT section_id FROM sections WHERE course_id = %s AND section_number = %s",
                    (course_id, section_number)
                )
                row = cursor.fetchone()
                if not row:
                    return jsonify({"success": False, "message": "رقم المادة أو رقم الشعبة غير مطروح في هذا الفصل"}), 404
                section_id = row[0]

                # ب. فحص التخصص (إذا لم يكن force_specialization مفعّلاً)
                if not force_specialization:
                    cursor.execute(
                        "SELECT c.specialization, s.specialization FROM courses c, students s "
                        "WHERE c.course_id = %s AND s.student_id = %s",
                        (course_id, student_id)
                    )
                    spec_row = cursor.fetchone()
                    if spec_row:
                        course_spec, student_spec = spec_row
                        if course_spec != 'مشترك' and course_spec != student_spec:
                            return jsonify({
                                "success":              False,
                                "type":                 "spec_warning",
                                "message":              "هذه المادة ليست ضمن خطة تخصصك",
                                "course_specialization": course_spec,
                                "student_specialization": student_spec
                            }), 200

                # د. التحقق من عدم التكرار في الانتظار
                cursor.execute(
                    "SELECT 1 FROM registration_requests WHERE student_id = %s AND section_id = %s AND status = 'معلق'",
                    (student_id, section_id)
                )
                if cursor.fetchone():
                    return jsonify({"success": False, "message": "هذه المادة موجودة بالفعل في قائمة الانتظار لديك"}), 400

                # هـ. التحقق من عدم التسجيل المسبق
                cursor.execute(
                    "SELECT 1 FROM enrollments WHERE student_id = %s AND section_id = %s",
                    (student_id, section_id)
                )
                if cursor.fetchone():
                    return jsonify({"success": False, "message": "أنت مسجل في هذه المادة ومثبتة في جدولك بالفعل"}), 400

                # و. جلب بيانات الطالب لحساب الأولوية
                cursor.execute(
                    "SELECT academic_year, completed_hours, gpa FROM students WHERE student_id = %s",
                    (student_id,)
                )
                student = cursor.fetchone()
                if not student:
                    return jsonify({"success": False, "message": "الطالب غير موجود"}), 404

                # ز. جلب عدد مرات الرسوب في هذه المادة
                cursor.execute(
                    "SELECT COUNT(*) FROM student_records WHERE student_id = %s AND course_id = %s AND final_grade < 50",
                    (student_id, course_id)
                )
                fail_count = cursor.fetchone()[0]

                # ح. حساب الأولوية
                priority_score = _calc_priority(student[0], student[1], fail_count, student[2])
                priority_label = _priority_label(priority_score)

                # ط. إدراج الطلب بالأولوية المحسوبة
                cursor.execute(
                    "INSERT INTO registration_requests (student_id, section_id, priority_score, status) VALUES (%s, %s, %s, 'معلق')",
                    (student_id, section_id, priority_score)
                )
                conn.commit()

        return jsonify({
            "success":        True,
            "message":        "➕ تم إضافة المادة إلى قائمة الانتظار",
            "priority_score": priority_score,
            "priority_label": priority_label
        }), 201

    except mysql.connector.Error as err:
        return jsonify({"success": False, "message": f"خطأ أثناء معالجة الطلب: {str(err)}"}), 500


# 4. حذف طلب من قائمة الانتظار
@student_registration_bp.route('/api/delete_pending_request', methods=['POST'])
def delete_pending_request():
    try:
        data       = request.get_json()
        student_id = data.get('student_id')
        request_id = data.get('request_id')

        if not all([student_id, request_id]):
            return jsonify({"success": False, "message": "بيانات ناقصة"}), 400

        with get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    "DELETE FROM registration_requests WHERE request_id = %s AND student_id = %s AND status = 'معلق'",
                    (request_id, student_id)
                )
                conn.commit()

                if cursor.rowcount == 0:
                    return jsonify({"success": False, "message": "الطلب غير موجود أو لا يمكن حذفه"}), 404

        return jsonify({"success": True, "message": "تم حذف المادة من قائمة الانتظار"}), 200

    except mysql.connector.Error as err:
        return jsonify({"success": False, "message": f"خطأ في قاعدة البيانات: {str(err)}"}), 500
