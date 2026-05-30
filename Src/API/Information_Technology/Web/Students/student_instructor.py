from API import settings as st
from flask import Blueprint, jsonify
import mysql.connector

student_instructor_bp = Blueprint('student_instructor', __name__)


def get_connection():
    return mysql.connector.connect(**st.DB_CONFIG)


# جلب قائمة أعضاء الهيئة التدريسية كاملة للطلاب بناءً على الهيكل الفعلي
@student_instructor_bp.route('/api/student_instructor', methods=['GET'])
def get_instructors_list():
    try:
        with get_connection() as conn:
            with conn.cursor(dictionary=True) as cursor:
                # تم تصحيح الاستعلام: instructor_id وحذف photo_path غير الموجود بالجدول
                cursor.execute("""
                    SELECT instructor_id, full_name, academic_rank, specialization 
                    FROM instructors
                    ORDER BY full_name ASC
                """)
                instructors = cursor.fetchall()

        return jsonify({
            "success": True,
            "data": instructors
        }), 200

    except mysql.connector.Error as err:
        return jsonify({"success": False, "message": f"خطأ في قاعدة البيانات: {str(err)}"}), 500
