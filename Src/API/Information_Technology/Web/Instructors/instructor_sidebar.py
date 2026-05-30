from API import settings as st
from flask import Blueprint, jsonify
import mysql.connector

instructor_sidebar_bp = Blueprint('instructor_sidebar', __name__)


def get_connection():
    return mysql.connector.connect(**st.DB_CONFIG)


# جلب بيانات المحاضر للقائمة الجانبية
@instructor_sidebar_bp.route('/api/instructors/<int:instructor_id>', methods=['GET'])
def get_sidebar_instructor_data(instructor_id):
    try:
        with get_connection() as conn:
            with conn.cursor(dictionary=True) as cursor:
                cursor.execute("""
                    SELECT full_name, specialization, academic_rank
                    FROM instructors
                    WHERE instructor_id = %s
                """, (instructor_id,))
                instructor = cursor.fetchone()

        if instructor:
            return jsonify({"success": True, "instructor": instructor}), 200

        return jsonify({"success": False, "message": "المحاضر غير موجود"}), 404

    except mysql.connector.Error as err:
        return jsonify({"success": False, "message": f"خطأ في قاعدة البيانات: {str(err)}"}), 500
