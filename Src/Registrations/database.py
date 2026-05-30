import mysql.connector
import settings as st


def get_connection():
    """إنشاء اتصال بقاعدة البيانات"""
    return mysql.connector.connect(
        host=st.DB_HOST,
        user=st.DB_USER,
        password=st.DB_PASSWORD,
        database=st.DB_NAME
    )


def get_student(student_id):
    """جلب بيانات الطالب"""
    conn   = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM students WHERE student_id = %s", (student_id,))
    student = cursor.fetchone()
    cursor.close()
    conn.close()
    return student


def get_course(course_id):
    """جلب بيانات المادة"""
    conn   = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM courses WHERE course_id = %s", (course_id,))
    course = cursor.fetchone()
    cursor.close()
    conn.close()
    return course


def get_section(course_id, section_number):
    """جلب بيانات الشعبة"""
    conn   = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT * FROM sections
        WHERE course_id = %s AND section_number = %s
    """, (course_id, section_number))
    section = cursor.fetchone()
    cursor.close()
    conn.close()
    return section


def get_fail_count(student_id, course_id):
    """جلب عدد مرات رسوب الطالب في المادة"""
    conn   = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT COUNT(*) as fail_count
        FROM student_records
        WHERE student_id = %s
        AND course_id = %s
        AND final_grade < 50
    """, (student_id, course_id))
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    return result["fail_count"] if result else 0


def get_enrolled_count(section_id):
    """جلب عدد المسجلين الحاليين في الشعبة"""
    conn   = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT COUNT(*) as count FROM enrollments
        WHERE section_id = %s
    """, (section_id,))
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    return result["count"] if result else 0


def add_request(student_id, section_id, priority_score):
    """تخزين طلب التسجيل مع الأولوية"""
    conn   = get_connection()
    cursor = conn.cursor()

    # التحقق من عدم تكرار الطلب
    cursor.execute("""
        SELECT request_id FROM registration_requests
        WHERE student_id = %s AND section_id = %s
    """, (student_id, section_id))

    if cursor.fetchone():
        cursor.close()
        conn.close()
        return None

    cursor.execute("""
        INSERT INTO registration_requests (student_id, section_id, priority_score)
        VALUES (%s, %s, %s)
    """, (student_id, section_id, priority_score))

    conn.commit()
    request_id = cursor.lastrowid
    cursor.close()
    conn.close()
    return request_id


def get_registration_requests(section_id):
    """جلب الطلبات المعلقة مرتبة تنازلياً بالأولوية"""
    conn   = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT r.request_id, r.student_id, s.full_name,
               s.academic_year, s.gpa, s.completed_hours,
               r.priority_score, r.status, r.created_at
        FROM registration_requests r
        JOIN students s ON r.student_id = s.student_id
        WHERE r.section_id = %s
        AND r.status = 'معلق'
        ORDER BY r.priority_score DESC
    """, (section_id,))
    result = cursor.fetchall()
    cursor.close()
    conn.close()
    return result


def enroll_student(student_id, section_id):
    """تسجيل الطالب في الشعبة وتحديث حالة طلبه"""
    conn   = get_connection()
    cursor = conn.cursor()

    # إضافة للـ enrollments
    cursor.execute("""
        INSERT INTO enrollments (student_id, section_id)
        VALUES (%s, %s)
    """, (student_id, section_id))

    # تحديث حالة الطلب إلى مقبول
    cursor.execute("""
        UPDATE registration_requests SET status = 'مقبول'
        WHERE student_id = %s AND section_id = %s
    """, (student_id, section_id))

    # تحديث حالة الشعبة إذا امتلأت
    cursor.execute("""
        UPDATE sections
        SET status = CASE
            WHEN (
                SELECT COUNT(*) FROM enrollments
                WHERE section_id = %s
            ) >= capacity THEN 'مغلق'
            ELSE 'مفتوح'
        END
        WHERE section_id = %s
    """, (section_id, section_id))

    conn.commit()
    cursor.close()
    conn.close()


def reject_student(student_id, section_id):
    """رفض طلب الطالب"""
    conn   = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE registration_requests SET status = 'مرفوض'
        WHERE student_id = %s AND section_id = %s
    """, (student_id, section_id))
    conn.commit()
    cursor.close()
    conn.close()


def process_registrations(section_id):
    """معالجة التسجيل — توزيع المقاعد حسب الأولوية"""
    conn   = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM sections WHERE section_id = %s", (section_id,))
    section = cursor.fetchone()
    cursor.close()
    conn.close()

    if not section:
        return {"status": "error", "message": "الشعبة غير موجودة"}

    capacity      = section["capacity"]
    enrolled      = get_enrolled_count(section_id)
    available     = capacity - enrolled
    registration_requests      = get_registration_requests(section_id)

    if not registration_requests:
        return {"status": "error", "message": "لا يوجد طلبات لهذه الشعبة"}

    approved_list = []
    rejected_list = []

    for i, req in enumerate(registration_requests):
        if i < available:
            enroll_student(req["student_id"], section_id)
            approved_list.append({
                "name":           req["full_name"],
                "priority_score": float(req["priority_score"]),
            })
        else:
            reject_student(req["student_id"], section_id)
            rejected_list.append({
                "name":           req["full_name"],
                "priority_score": float(req["priority_score"]),
            })

    return {
        "status":    "done",
        "available": available,
        "approved":  approved_list,
        "rejected":  rejected_list,
    }
