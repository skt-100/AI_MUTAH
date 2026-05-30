from API import settings as st
from flask import Blueprint, request, jsonify
import mysql.connector

student_login_bp = Blueprint('student_login', __name__)


def get_connection():
    return mysql.connector.connect(**st.DB_CONFIG)


# عملية تسجيل دخول الطالب
@student_login_bp.route('/api/student_login', methods=['POST'])
def student_login():
    data = request.get_json() or {}
    user_id = data.get('userId')
    password = data.get('password')

    # التحقق من المدخلات الأساسية
    if not user_id or not password:
        return jsonify({"success": False, "message": "الرجاء إدخال الرقم الجامعي وكلمة المرور"}), 400

    try:
        with get_connection() as conn:
            with conn.cursor(dictionary=True) as cursor:
                # الاستعلام للتحقق من الطالب وكلمة المرور
                cursor.execute("""
                    SELECT student_id, full_name 
                    FROM students 
                    WHERE student_id = %s AND password = %s
                """, (user_id, password))
                
                student = cursor.fetchone()

        # إذا كانت البيانات صحيحة
        if student:
            return jsonify({
                "success": True,
                "id": student['student_id'],
                "name": student['full_name'],
                "role": "student",
                "redirect": "/Information_Technology/HTML/Students/student_dashboard.html" # مسار التوجيه بعد النجاح
            })
        
        # إذا كانت البيانات خاطئة
        return jsonify({"success": False, "message": "الرقم الجامعي أو كلمة المرور غير صحيحة"}), 401

    except mysql.connector.Error as err:
        return jsonify({"success": False, "message": f"خطأ في قاعدة البيانات: {str(err)}"}), 500
