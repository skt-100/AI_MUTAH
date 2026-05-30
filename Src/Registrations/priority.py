import settings as st

TOTAL_HOURS = 132  # ثابت لجميع الطلاب


def get_year_score(academic_year):
    """
    تحويل السنة الدراسية (1-4) لقيمة بين 0 و1
    سنة 4 = 1.0 (أعلى أولوية)
    سنة 1 = 0.25 (أقل أولوية)
    """
    year_map = {
        4: 1.0,
        3: 0.75,
        2: 0.50,
        1: 0.25,
    }
    return year_map.get(int(academic_year), 0.25)


def get_hours_score(completed_hours):
    """
    كلما زادت الساعات المنجزة زادت الأولوية
    طالب أنجز 120 ساعة = أولوية أعلى من أنجز 30 ساعة
    """
    return round(min(completed_hours, TOTAL_HOURS) / TOTAL_HOURS, 2)


def get_fail_score(fail_count):
    """
    0 مرات رسوب = 0.0
    1 مرة        = 0.5
    2 مرات+      = 1.0
    """
    if fail_count == 0:   return 0.0
    elif fail_count == 1: return 0.5
    return 1.0


def get_gpa_score(gpa):
    """
    تحويل المعدل (0-100) لقيمة بين 0 و1
    """
    return round(min(float(gpa), 100) / 100, 2)


def calculate_priority(student, fail_count):
    """
    حساب الأولوية النهائية بناءً على المعادلة
    """
    year_score  = get_year_score(student["academic_year"])
    hours_score = get_hours_score(student["completed_hours"])
    fail_score  = get_fail_score(fail_count)
    gpa_score   = get_gpa_score(student["gpa"])

    priority = (
        year_score  * st.W_YEAR  +
        hours_score * st.W_HOURS +
        fail_score  * st.W_FAIL  +
        gpa_score   * st.W_GPA
    )

    return round(priority, 4)


def get_priority_label(priority):
    """
    تحديد تصنيف الأولوية بناءً على الـ Thresholds
    """
    if priority >= st.THRESHOLD_AUTO:
        return "تسجيل فوري"
    elif priority >= st.THRESHOLD_HIGH:
        return "انتظار أولوية عالية"
    elif priority >= st.THRESHOLD_NORMAL:
        return "انتظار عادية"
    return "آخر القائمة"
