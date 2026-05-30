import settings as st


def build_message(student_name, course_name, change_type, old_value, new_value):
    """بناء نص الإشعار بناءً على نوع التغيير"""

    changes = {
        "وقت":  f"تم تغيير وقت محاضرة مادة {course_name} من {old_value} إلى {new_value}.",
        "قاعة": f"تم تغيير قاعة محاضرة مادة {course_name} من {old_value} إلى {new_value}.",
        "مدرس": f"تم تغيير مدرس مادة {course_name} من {old_value} إلى {new_value}.",
        "يوم":  f"تم تغيير يوم محاضرة مادة {course_name} من {old_value} إلى {new_value}.",
    }

    body = changes.get(change_type, f"تم تغيير {change_type} في مادة {course_name}.")

    message = f"""\
عزيزي {student_name}،

{body}

مع تحيات،
{st.UNIVERSITY_NAME} — {st.SYSTEM_NAME}
"""
    return message


def build_subject(course_name, change_type):
    """بناء عنوان البريد الإلكتروني"""
    return f"إشعار: تغيير {change_type} في مادة {course_name}"
