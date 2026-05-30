import database as db
import priority as pr


def submit_request(student_id, course_id, section_number):
    """
    تقديم طلب التسجيل — لا يسجل فوراً بل يخزن الطلب مع الأولوية
    """
    # 1. جلب بيانات الطالب
    student = db.get_student(student_id)
    if not student:
        return {"status": "error", "message": "الطالب غير موجود"}

    # 2. جلب بيانات المادة
    course = db.get_course(course_id)
    if not course:
        return {"status": "error", "message": "المادة غير موجودة"}

    # 3. جلب بيانات الشعبة
    section = db.get_section(course_id, section_number)
    if not section:
        return {"status": "error", "message": "الشعبة غير موجودة"}

    # 4. جلب عدد مرات الرسوب
    fail_count = db.get_fail_count(student_id, course_id)

    # 5. حساب الأولوية
    priority_score = pr.calculate_priority(student, fail_count)
    priority_label = pr.get_priority_label(priority_score)

    # 6. تخزين الطلب
    section_id = section["section_id"]
    request_id = db.add_request(student_id, section_id, priority_score)
    if not request_id:
        return {"status": "error", "message": "لديك طلب مسبق لهذه الشعبة"}

    return {
        "status":         "معلق",
        "message":        "تم تقديم طلبك بنجاح، انتظر نتيجة المعالجة",
        "priority_score": priority_score,
        "priority_label": priority_label,
        "student_name":   student["full_name"],
        "course_name":    course["course_name"],
        "section_number": section_number,
    }


def process_all(section_id):
    """
    معالجة جميع الطلبات وتوزيع المقاعد — يستدعيها الأدمن فقط
    """
    return db.process_registrations(section_id)


def get_requests(section_id):
    """
    عرض الطلبات مرتبة بالأولوية
    """
    requests = db.get_requests(section_id)
    if not requests:
        return {"status": "empty", "message": "لا يوجد طلبات لهذه الشعبة"}
    return {"status": "ok", "requests": requests}
