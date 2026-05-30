from API import settings as st
from flask import Blueprint, request, jsonify
import mysql.connector
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

instructor_notification_bp = Blueprint('instructor_notification', __name__)

GMAIL_USER      = "alialkhataybeh@gmail.com"
GMAIL_PASSWORD  = "zpkb hbqy omyq caov"
UNIVERSITY_NAME = "جامعة مؤتة"

COLUMN_MAP = {
    'وقت':  'start_time',
    'قاعة': 'room',
    'مدرس': 'instructor_id',
    'يوم':  'days',
}

CHANGE_LABELS = {
    'وقت':  'وقت المحاضرة',
    'قاعة': 'قاعة المحاضرة',
    'مدرس': 'مدرس المادة',
    'يوم':  'يوم المحاضرة',
}


def get_connection():
    return mysql.connector.connect(**st.DB_CONFIG)


def send_email(to_email, subject, body):
    msg = MIMEMultipart()
    msg["From"]    = GMAIL_USER
    msg["To"]      = to_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain", "utf-8"))
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(GMAIL_USER, GMAIL_PASSWORD)
        server.send_message(msg)


@instructor_notification_bp.route('/api/instructor/notify', methods=['POST'])
def instructor_notify():
    data          = request.get_json() or {}
    section_id    = data.get('section_id')
    change_type   = data.get('change_type')
    new_value     = data.get('new_value')
    instructor_id = data.get('instructor_id')

    if not all([section_id, change_type, new_value, instructor_id]):
        return jsonify({"success": False, "message": "البيانات غير مكتملة"}), 400

    column = COLUMN_MAP.get(change_type)
    if not column:
        return jsonify({"success": False, "message": "نوع التغيير غير صحيح"}), 400

    try:
        with get_connection() as conn:
            with conn.cursor(dictionary=True) as cursor:

                # 1. التحقق أن الشعبة تخص هذا المحاضر
                cursor.execute("""
                    SELECT s.*, c.course_name
                    FROM sections s
                    JOIN courses c ON s.course_id = c.course_id
                    WHERE s.section_id = %s AND s.instructor_id = %s
                """, (section_id, instructor_id))
                section = cursor.fetchone()

                if not section:
                    return jsonify({"success": False,
                                    "message": "الشعبة غير موجودة أو لا تنتمي إليك"}), 403

                old_value   = str(section.get(column, '—'))
                course_name = section['course_name']

                # 2. تحديث الشعبة في قاعدة البيانات
                cursor.execute(
                    f"UPDATE sections SET {column} = %s WHERE section_id = %s",
                    (new_value, section_id)
                )

                # 3. جلب الطلاب المسجلين في الشعبة
                cursor.execute("""
                    SELECT st.student_id, st.full_name, st.email
                    FROM enrollments e
                    JOIN students st ON e.student_id = st.student_id
                    WHERE e.section_id = %s
                """, (section_id,))
                students = cursor.fetchall()

            conn.commit()

        if not students:
            return jsonify({
                "success": True,
                "message": "تم التحديث — لا يوجد طلاب مسجلين في هذه الشعبة",
                "sent": 0, "failed": 0
            })

        subject = f"إشعار: تغيير {CHANGE_LABELS.get(change_type, change_type)} في مادة {course_name}"
        sent   = 0
        failed = 0

        for student in students:
            message = (
                f"عزيزي {student['full_name']}،\n\n"
                f"نُعلمك بأنه تم تغيير {CHANGE_LABELS.get(change_type, change_type)} "
                f"لمادة {course_name} من ( {old_value} ) إلى ( {new_value} ).\n\n"
                f"يرجى الأخذ بعين الاعتبار هذا التغيير.\n\n"
                f"مع تحيات،\n{UNIVERSITY_NAME} — كلية تكنولوجيا المعلومات"
            )
            try:
                send_email(student['email'], subject, message)
                with get_connection() as conn2:
                    with conn2.cursor() as c2:
                        c2.execute("""
                            INSERT INTO private_notification
                            (student_id, section_id, change_type, old_value, new_value, message)
                            VALUES (%s, %s, %s, %s, %s, %s)
                        """, (student['student_id'], section_id,
                              change_type, old_value, new_value, message))
                    conn2.commit()
                sent += 1
            except Exception as e:
                print(f"فشل الإرسال لـ {student['full_name']}: {e}")
                failed += 1

        return jsonify({
            "success": True,
            "message": f"تم إرسال {sent} إشعار بنجاح",
            "sent":    sent,
            "failed":  failed
        })

    except mysql.connector.Error as err:
        return jsonify({"success": False,
                        "message": f"خطأ في قاعدة البيانات: {str(err)}"}), 500
