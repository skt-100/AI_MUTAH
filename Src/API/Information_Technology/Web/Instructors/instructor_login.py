from API import settings as st
from flask import Blueprint, request, jsonify
import mysql.connector

instructor_login_bp = Blueprint('instructor_login', __name__)


def get_connection():
    return mysql.connector.connect(**st.DB_CONFIG)


@instructor_login_bp.route('/api/instructor_login', methods=['POST'])
def instructor_login():
    data = request.get_json() or {}
    instructor_id = data.get('instructor_id')
    password      = data.get('password')

    if not instructor_id or not password:
        return jsonify({"success": False, "message": "الرجاء إدخال الرقم الوظيفي وكلمة المرور"}), 400

    try:
        with get_connection() as conn:
            with conn.cursor(dictionary=True) as cursor:
                cursor.execute("""
                    SELECT instructor_id, full_name
                    FROM instructors
                    WHERE instructor_id = %s AND password = %s
                """, (instructor_id, password))

                instructor = cursor.fetchone()

        if instructor:
            return jsonify({
                "success":  True,
                "id":       instructor['instructor_id'],
                "name":     instructor['full_name'],
                "role":     "admin",
                "redirect": "/Information_Technology/HTML/Instructors/instructor_dashboard.html"
            })

        return jsonify({"success": False, "message": "الرقم الوظيفي أو كلمة المرور غير صحيحة"}), 401

    except mysql.connector.Error as err:
        return jsonify({"success": False, "message": f"خطأ في قاعدة البيانات: {str(err)}"}), 500
