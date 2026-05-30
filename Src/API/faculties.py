from API import settings as st
from flask import Blueprint, jsonify
import mysql.connector

faculties_bp = Blueprint('faculties', __name__)


def get_connection():
    return mysql.connector.connect(**st.DB_CONFIG)


# جلب قائمة الكليات بالكامل لعرضها في الصفحة الرئيسية
@faculties_bp.route('/api/faculties', methods=['GET'])
def get_all_faculties():
    try:
        with get_connection() as conn:
            with conn.cursor(dictionary=True) as cursor:
                # استعلام لجلب الكليات مع ترتيب الكلية المميزة أولاً ثم الأقدم تأسست
                cursor.execute("""
                    SELECT faculty_id, faculty_name, description, dept_label, is_featured, icon_path
                    FROM faculties
                    ORDER BY is_featured DESC, faculty_id ASC
                """)
                faculties_list = cursor.fetchall()

        # تحويل القيمة الرقمية لـ is_featured إلى Boolean لتتوافق تماماً مع كود الجافاسكريبت المكتوب
        for faculty in faculties_list:
            faculty['is_featured'] = bool(faculty['is_featured'])

        return jsonify({
            "success": True,
            "faculties": faculties_list
        }), 200

    except mysql.connector.Error as err:
        return jsonify({"success": False, "message": f"خطأ في قاعدة البيانات: {str(err)}"}), 500
