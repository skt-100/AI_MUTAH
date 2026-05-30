# =============================================================================
# sections_generation.py — حقن بيانات الشعب من Excel إلى جدول sections
# =============================================================================

import pandas as pd
import mysql.connector
import re
import sys
import os

# ─── إضافة مسار settings ───
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..', 'API'))
from settings import DB_CONFIG

# ─── مسار ملف Excel ───
EXCEL_PATH = os.path.join(os.path.dirname(__file__), './Data/materials.xlsx')

# ─── وقت افتراضي للمواد التي ليس لها وقت محدد (تدريب ميداني، مشاريع تخرج) ───
DEFAULT_TIME = '00:00:00'


# =============================================================================
# دوال التطبيع — نفس المنطق المستخدم في instructors_generation.py
# =============================================================================

def normalize_arabic_name(name):
    """
    تطبيع الاسم العربي لضمان تطابقه مع ما هو مخزن في قاعدة البيانات:
    - إزالة التشكيل
    - توحيد الهمزات: أإآ → ا
    - توحيد التاء المربوطة: ة → ه
    - إزالة المسافات الزائدة
    """
    if not name:
        return name
    name = re.sub(r'[\u0617-\u061A\u064B-\u0652]', '', name)
    name = re.sub(r'[أإآ]', 'ا', name)
    name = name.replace('ة', 'ه')
    name = re.sub(r'\s+', ' ', name).strip()
    return name


# =============================================================================
# دوال المعالجة
# =============================================================================

def parse_time(time_str):
    """تحويل الوقت من صيغة '8:30-10:30' إلى (start_time, end_time)"""
    time_str = time_str.strip()
    if not time_str or time_str == 'غير محدد':
        return DEFAULT_TIME, DEFAULT_TIME
    try:
        parts = time_str.split('-')
        start = parts[0].strip()
        end   = parts[1].strip()
        if start.count(':') == 1: start += ':00'
        if end.count(':') == 1:   end   += ':00'
        return start, end
    except Exception:
        return DEFAULT_TIME, DEFAULT_TIME


def parse_days(days_str):
    """تنظيف عمود الأيام"""
    days_str = days_str.strip()
    if not days_str or days_str == 'غير محدد':
        return 'غير محدد'
    return days_str


def parse_status(status_str):
    """تحويل الحالة — مغلق أو مفتوح فقط"""
    if status_str.strip() == 'مغلق':
        return 'مغلق'
    return 'مفتوح'


# =============================================================================
# تحميل البيانات
# =============================================================================

def load_instructor_map(conn):
    """
    جلب خريطة { full_name_normalized: instructor_id } من جدول instructors.
    الأسماء مطبّعة مسبقاً عند الإدخال، لكن نطبّعها مجدداً للتأكد.
    """
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT instructor_id, full_name FROM instructors")
    rows = cursor.fetchall()
    cursor.close()
    # المفتاح هو الاسم المطبّع
    return {normalize_arabic_name(row['full_name']): row['instructor_id'] for row in rows}


def load_sections_from_excel():
    """قراءة كل الشعب من ملف Excel"""
    df = pd.read_excel(EXCEL_PATH, sheet_name='المواد', dtype=str)
    df.columns = [
        'رقم المادة', 'اسم المادة', 'عدد الساعات المعتمدة', 'المتطلب السابق',
        'التخصص', 'مدرس المادة', 'رقم الشعبة', 'سعة الشعبة', 'عدد الطلاب',
        'الايام', 'الساعة', 'الموقع', 'نمط التدريس', 'حالة الشعبة'
    ]
    df = df.fillna('')
    return df


# =============================================================================
# حقن البيانات
# =============================================================================

def inject_sections(df, instructor_map):
    """حقن الشعب في جدول sections"""
    conn   = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()

    success      = 0
    skipped      = 0
    errors       = 0
    unknown_inst = set()

    for _, row in df.iterrows():
        try:
            course_id      = int(row['رقم المادة'])
            section_number = int(row['رقم الشعبة']) if row['رقم الشعبة'].strip() else None
            capacity       = int(row['سعة الشعبة']) if row['سعة الشعبة'].strip() else 25
            days           = parse_days(row['الايام'])
            start_time, end_time = parse_time(row['الساعة'])
            room           = row['الموقع'].strip() if row['الموقع'].strip() not in ('غير محدد', '') else None
            status         = parse_status(row['حالة الشعبة'])

            # ─── تطبيع اسم المدرس قبل البحث في الخريطة ───
            instructor_name         = row['مدرس المادة'].strip()
            instructor_name_norm    = normalize_arabic_name(instructor_name)
            instructor_id           = instructor_map.get(instructor_name_norm)

            if instructor_id is None and instructor_name not in ('غير محدد', 'هيئة تدريس', 'مشرف مختبر', ''):
                unknown_inst.add(instructor_name)

            if section_number is None:
                skipped += 1
                continue

            cursor.execute("""
                INSERT INTO sections 
                    (course_id, instructor_id, section_number, days, start_time, end_time, room, capacity, status)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (course_id, instructor_id, section_number, days, start_time, end_time, room, capacity, status))

            success += 1

        except mysql.connector.errors.IntegrityError as e:
            skipped += 1
        except Exception as e:
            print(f"  ✗ خطأ في الصف {_}: {e}")
            errors += 1

    conn.commit()
    cursor.close()
    conn.close()

    return success, skipped, errors, unknown_inst


# =============================================================================
# التشغيل الرئيسي
# =============================================================================

def main():
    print("=" * 55)
    print("  حقن بيانات الشعب → جدول sections")
    print("=" * 55)

    print("\n① قراءة ملف Excel...")
    df = load_sections_from_excel()
    print(f"   تم قراءة {len(df)} شعبة")

    print("\n② جلب بيانات المدرسين من قاعدة البيانات...")
    conn = mysql.connector.connect(**DB_CONFIG)
    instructor_map = load_instructor_map(conn)
    conn.close()
    print(f"   تم جلب {len(instructor_map)} مدرس")

    print("\n③ حقن البيانات في قاعدة البيانات...")
    success, skipped, errors, unknown_inst = inject_sections(df, instructor_map)

    print("\n" + "=" * 55)
    print(f"  ✅ تم إدخال  : {success} شعبة")
    print(f"  ⚠️  متخطاة   : {skipped} شعبة")
    print(f"  ✗  أخطاء    : {errors} شعبة")

    if unknown_inst:
        print(f"\n  ⚠️  مدرسون غير موجودين في قاعدة البيانات ({len(unknown_inst)}):")
        for name in sorted(unknown_inst):
            print(f"     - {name}")
    print("=" * 55)


if __name__ == '__main__':
    main()
