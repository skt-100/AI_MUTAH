from database import get_enrolled_students, get_course_name, get_section, update_section, save_notification
from message  import build_message, build_subject
from sender   import send_email


def notify_section_change(section_id, change_type, new_value):
    """
    الدالة الرئيسية:
    1. تجلب القيمة القديمة
    2. تحدث قاعدة البيانات
    3. ترسل الإشعارات للطلاب
    """
    # 1. جلب بيانات الشعبة الحالية
    section = get_section(section_id)
    if not section:
        return {"status": "error", "message": "الشعبة غير موجودة"}

    # 2. تحديد القيمة القديمة
    column_map = {
        "وقت":  "start_time",
        "قاعة": "room",
        "مدرس": "instructor_id",
        "يوم":  "days",
    }
    column    = column_map.get(change_type)
    old_value = str(section.get(column, "غير محدد"))

    # 3. تحديث قاعدة البيانات
    updated = update_section(section_id, change_type, new_value)
    if not updated:
        return {"status": "error", "message": "نوع التغيير غير صحيح"}

    # 4. جلب الطلاب المعنيين
    students    = get_enrolled_students(section_id)
    course_name = get_course_name(section_id)

    if not students:
        return {"status": "ok", "message": "تم التحديث — لا يوجد طلاب مسجلين"}

    # 5. إرسال الإشعارات
    subject = build_subject(course_name, change_type)
    success = 0
    failed  = 0

    for student in students:
        message = build_message(
            student["full_name"], course_name,
            change_type, old_value, new_value
        )
        try:
            send_email(student["email"], subject, message)
            save_notification(
                student["student_id"], section_id,
                change_type, old_value, new_value, message
            )
            success += 1
        except Exception as e:
            print(f"❌ فشل إرسال لـ {student['full_name']}: {e}")
            failed += 1

    return {
        "status":  "done",
        "message": f"تم التحديث وإرسال {success} إشعار",
        "success": success,
        "failed":  failed,
    }


if __name__ == "__main__":
    section_id  = int(input("رقم الشعبة: "))
    change_type = input("نوع التغيير (وقت/قاعة/مدرس/يوم): ")
    new_value   = input("القيمة الجديدة: ")
    result      = notify_section_change(section_id, change_type, new_value)
    print(result["message"])
