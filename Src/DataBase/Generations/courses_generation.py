# =============================================================================
# courses_generation.py — حقن بيانات المواد من Excel إلى جدول courses
# =============================================================================

import pandas as pd
import mysql.connector
import sys
import os

# ─── إضافة مسار settings ───
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..', 'API'))
from settings import DB_CONFIG

# ─── مسار ملف Excel ───
EXCEL_PATH = os.path.join(os.path.dirname(__file__), './Data/materials.xlsx')


def load_courses_from_excel():
    """قراءة المواد الفريدة من ملف Excel"""
    df = pd.read_excel(EXCEL_PATH, sheet_name='المواد', dtype=str)
    df.columns = [
        'رقم المادة', 'اسم المادة', 'عدد الساعات المعتمدة', 'المتطلب السابق',
        'التخصص', 'مدرس المادة', 'رقم الشعبة', 'سعة الشعبة', 'عدد الطلاب',
        'الايام', 'الساعة', 'الموقع', 'نمط التدريس', 'حالة الشعبة'
    ]
    df = df.fillna('')

    # جلب المواد الفريدة فقط بدون تكرار الشعب
    courses_df = df[['رقم المادة', 'اسم المادة', 'عدد الساعات المعتمدة', 'المتطلب السابق', 'التخصص']].drop_duplicates(subset=['رقم المادة'])
    return courses_df


def inject_courses(courses_df):
    """حقن المواد في جدول courses"""
    conn   = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()

    success = 0
    skipped = 0
    errors  = 0

    for _, row in courses_df.iterrows():
        try:
            course_id    = int(row['رقم المادة'])
            course_name  = row['اسم المادة'].strip()
            credit_hours = int(row['عدد الساعات المعتمدة']) if row['عدد الساعات المعتمدة'] else 3
            prerequisite = int(row['المتطلب السابق']) if row['المتطلب السابق'].strip() else None
            specialization = row['التخصص'].strip()

            cursor.execute("""
                INSERT INTO courses (course_id, course_name, credit_hours, prerequisite, specialization)
                VALUES (%s, %s, %s, %s, %s)
            """, (course_id, course_name, credit_hours, prerequisite, specialization))

            success += 1

        except mysql.connector.errors.IntegrityError:
            skipped += 1
        except Exception as e:
            print(f"  ✗ خطأ في المادة {row['رقم المادة']}: {e}")
            errors += 1

    conn.commit()
    cursor.close()
    conn.close()

    return success, skipped, errors


def main():
    print("=" * 50)
    print("  حقن بيانات المواد → جدول courses")
    print("=" * 50)

    print("\n① قراءة ملف Excel...")
    courses_df = load_courses_from_excel()
    print(f"   تم قراءة {len(courses_df)} مادة فريدة")

    print("\n② حقن البيانات في قاعدة البيانات...")
    success, skipped, errors = inject_courses(courses_df)

    print("\n" + "=" * 50)
    print(f"  ✅ تم إدخال  : {success} مادة")
    print(f"  ⚠️  مكررة    : {skipped} مادة")
    print(f"  ✗  أخطاء    : {errors} مادة")
    print("=" * 50)


if __name__ == '__main__':
    main()
