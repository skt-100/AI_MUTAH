from API import settings as st
from flask import Blueprint, jsonify
import mysql.connector

student_honorboard_bp = Blueprint('student_honorboard', __name__)


def get_connection():
    return mysql.connector.connect(**st.DB_CONFIG)


# جلب قائمة لوحة الشرف مرتبة وموزعة حسب التخصص والمراكز
@student_honorboard_bp.route('/api/student_honorboard', methods=['GET'])
def get_honor_board():
    try:
        with get_connection() as conn:
            with conn.cursor(dictionary=True) as cursor:
                # استعلام يحسب ترتيب المراكز تلقائياً داخل كل تخصص بناءً على المعدل
                cursor.execute("""
                    SELECT 
                        full_name,
                        completed_hours,
                        gpa,
                        specialization,
                        DENSE_RANK() OVER (PARTITION BY specialization ORDER BY gpa DESC) AS student_rank
                    FROM students
                    WHERE gpa >= 3.50
                    ORDER BY specialization, gpa DESC
                """)
                honor_data = cursor.fetchall()

        return jsonify({
            "success": True,
            "data": honor_data
        }), 200

    except mysql.connector.Error as err:
        return jsonify({"success": False, "message": f"خطأ في قاعدة البيانات: {str(err)}"}), 500
