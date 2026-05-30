# =============================================================================
# instructors_generation.py — حقن بيانات المدرسين من Faculty_Hub.json
# =============================================================================

import json
import re
import random
import string
import mysql.connector
import sys
import os

# ─── إضافة مسار settings ───
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..', 'API'))
from settings import DB_CONFIG

# ─── مسار ملف JSON ───
JSON_PATH = os.path.join(os.path.dirname(__file__), './Data/Faculty_Hub.json')


# =============================================================================
# دوال المساعدة
# =============================================================================

def normalize_arabic_name(name):
    """
    تطبيع الاسم العربي:
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


def normalize_email(email):
    """تنظيف البريد الإلكتروني — يرجع None إذا كان غير محدد"""
    if not email or email.strip() == 'غير محدد':
        return None
    return email.strip().replace(' ', '')


def normalize_rank(rank):
    """تطبيع الرتبة الأكاديمية"""
    if not rank:
        return None
    rank = re.sub(r'[\u0617-\u061A\u064B-\u0652]', '', rank)
    rank = re.sub(r'[أإآ]', 'ا', rank)
    rank = rank.replace('ة', 'ه')
    return rank.strip()


def generate_password():
    """توليد كلمة مرور عشوائية: 3 أحرف صغيرة + 3 أرقام"""
    letters = random.choices(string.ascii_lowercase, k=3)
    digits  = random.choices(string.digits, k=3)
    return ''.join(letters + digits)


# =============================================================================
# تحميل البيانات
# =============================================================================

def load_instructors_from_json():
    """قراءة بيانات المدرسين من ملف JSON"""
    with open(JSON_PATH, encoding='utf-8') as f:
        data = json.load(f)

    instructors = []
    for item in data:
        if item.get('النوع') != 'عضو_هيئة_تدريس':
            continue

        instructors.append({
            'full_name':      normalize_arabic_name(item.get('الاسم', '')),
            'email':          normalize_email(item.get('البريد', '')),
            'specialization': normalize_arabic_name(item.get('القسم', '')),
            'academic_rank':  normalize_rank(item.get('الرتبة', '')),
        })

    return instructors


# =============================================================================
# حقن البيانات
# =============================================================================

def inject_instructors(instructors):
    """حقن المدرسين في جدول instructors"""
    conn   = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()

    success = 0
    skipped = 0
    errors  = 0

    for inst in instructors:
        try:
            password = generate_password()

            cursor.execute("""
                INSERT INTO instructors (full_name, email, password, specialization, academic_rank)
                VALUES (%s, %s, %s, %s, %s)
            """, (
                inst['full_name'],
                inst['email'],
                password,
                inst['specialization'],
                inst['academic_rank'],
            ))
            success += 1

        except mysql.connector.errors.IntegrityError:
            skipped += 1
        except Exception as e:
            print(f"  ✗ خطأ في المدرس {inst['full_name']}: {e}")
            errors += 1

    conn.commit()
    cursor.close()
    conn.close()

    return success, skipped, errors


# =============================================================================
# التشغيل الرئيسي
# =============================================================================

def main():
    print("=" * 55)
    print("  حقن بيانات المدرسين → جدول instructors")
    print("=" * 55)

    print("\n① قراءة ملف Faculty_Hub.json...")
    instructors = load_instructors_from_json()
    print(f"   تم قراءة {len(instructors)} مدرس")

    print("\n   الأسماء بعد التطبيع:")
    for inst in instructors:
        print(f"     - {inst['full_name']}")

    print("\n② حقن البيانات في قاعدة البيانات...")
    success, skipped, errors = inject_instructors(instructors)

    print("\n" + "=" * 55)
    print(f"  ✅ تم إدخال  : {success} مدرس")
    print(f"  ⚠️  مكرر     : {skipped} مدرس")
    print(f"  ✗  أخطاء    : {errors} مدرس")
    print("=" * 55)


if __name__ == '__main__':
    main()
