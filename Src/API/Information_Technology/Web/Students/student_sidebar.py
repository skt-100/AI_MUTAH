from API import settings as st
from flask import Blueprint, jsonify
import mysql.connector

student_sidebar_bp = Blueprint('student_sidebar', __name__)


def get_connection():
    return mysql.connector.connect(**st.DB_CONFIG)


# جلب بيانات الصورة الشخصية والجنس للطالب في القائمة الجانبية
@student_sidebar_bp.route('/api/students/<int:student_id>', methods=['GET'])
def get_sidebar_student_data(student_id):
    try:
        with get_connection() as conn:
            with conn.cursor(dictionary=True) as cursor:
                # استعلام جلب حقول الهوية البصرية للطالب فقط
                cursor.execute("""
                    SELECT gender, profile_img 
                    FROM students 
                    WHERE student_id = %s
                """, (student_id,))
                student = cursor.fetchone()

        if student:
            return jsonify({
                "success": True,
                "student": student
            }), 200
        
        return jsonify({"success": False, "message": "الطالب غير موجود"}), 404

    except mysql.connector.Error as err:
        return jsonify({"success": False, "message": f"خطأ في قاعدة البيانات: {str(err)}"}), 500
