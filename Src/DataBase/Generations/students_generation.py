import random
import mysql.connector

# ── إعدادات قاعدة البيانات ────────────────────────────────
DB_HOST     = "localhost"
DB_USER     = "sofyan"
DB_PASSWORD = "Mutah@2026"
DB_NAME     = "smart_it_faculty"

# ── أسماء أولى ───────────────────────────────────────────
FIRST_NAMES = [
    "سفيان", "أحمد", "محمد", "عمر", "يوسف", "خالد", "علي", "إبراهيم",
    "عبدالله", "عبدالرحمن", "فيصل", "سامي", "طارق", "وليد", "زياد",
    "ملاك", "فاطمة", "نور", "لينا", "سارة", "رغد", "جود", "ريم",
    "هند", "لبنى", "ميار", "دانا", "شذى", "سلمى", "رنا",
    "ماجد", "راشد", "نواف", "تركي", "بندر", "منصور", "هاني", "كريم",
    "امجد", "باسل", "حسام", "رامي", "نزار", "أنس", "لؤي", "مراد",
]

# ── أسماء الأب ───────────────────────────────────────────
MIDDLE_NAMES = [
    "خلف", "محمد", "أحمد", "علي", "حسن", "عمر", "يوسف", "خالد",
    "إبراهيم", "سالم", "ناصر", "جمال", "كمال", "فارس", "وليد",
    "طارق", "سمير", "عادل", "رشيد", "منير", "فؤاد", "زياد", "ماهر",
    "نضال", "غازي", "راتب", "صالح", "حامد", "رافع", "سعيد",
]

# ── أسماء العائلة ─────────────────────────────────────────
LAST_NAMES = [
    "الطراونة", "العمري", "الزيود", "الرواشدة", "المومني", "الحسن",
    "الخطيب", "الشوابكة", "العبادي", "القضاة", "النوايسة", "الحيصة",
    "الربابعة", "الفواعير", "الجراح", "البطاينة", "العجارمة", "الصرايرة",
    "الحوامدة", "المعايطة", "الذيابات", "الزبون", "الحمود", "السرور",
    "الغرايبة", "القرالة", "الشريدة", "الحموري", "الزعبي", "العزام",
    "الكساسبة", "الدويري", "الجبور", "الحدادين", "المساعيد", "الشديفات",
    "الحيالي", "الفريحات", "الطوالبة", "العضايلة",
]

# ── التخصصات الموحدة المتوافقة تماماً مع لوحة الشرف ───
MAJORS = [
    {"name": "هندسة البرمجيات",                 "code": "22"},
    {"name": "علم الحاسوب",                      "code": "23"},
    {"name": "الذكاء الاصطناعي وعلم البيانات",   "code": "24"},
    {"name": "امن معلومات",                       "code": "25"},
    {"name": "نظم معلومات حاسوبية",               "code": "26"},
]

# ── سنوات القبول ──────────────────────────────────────────
ADMISSION_YEARS = ["2022", "2023", "2024", "2025"]


def generate_password():
    chars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
    return ''.join(random.choices(chars, k=6))


def generate_student_id(admission_year, major_code, sequence):
    return int(f"{admission_year}{major_code}{sequence:06d}")


def get_academic_year(completed_hours):
    if completed_hours >= 99:   return 4
    elif completed_hours >= 66: return 3
    elif completed_hours >= 33: return 2
    return 1


def generate_students():
    students    = []
    used_ids    = set()
    used_emails = set()

    # المرور على كل تخصص من التخصصات الخمسة وتوليد 25 طالباً له بشكل مستقل
    for major in MAJORS:
        major_generated_count = 0
        
        while major_generated_count < 25:
            first  = random.choice(FIRST_NAMES)
            middle = random.choice(MIDDLE_NAMES)
            last   = random.choice(LAST_NAMES)
            name   = f"{first} {middle} {last}"

            admission_year = random.choice(ADMISSION_YEARS)

            sequence   = random.randint(1, 9999)
            student_id = generate_student_id(admission_year, major["code"], sequence)

            while student_id in used_ids:
                sequence   = random.randint(1, 9999)
                student_id = generate_student_id(admission_year, major["code"], sequence)
            
            email = f"{student_id}@mutah.edu.jo"
            if email in used_emails:
                continue

            used_ids.add(student_id)
            used_emails.add(email)

            year_diff = 2026 - int(admission_year)
            if year_diff >= 3:   completed = random.randint(99, 132)
            elif year_diff == 2: completed = random.randint(66, 98)
            elif year_diff == 1: completed = random.randint(33, 65)
            else:                completed = random.randint(0, 32)

            gpa           = round(random.uniform(60.0, 100.0), 2)
            academic_year = get_academic_year(completed)

            students.append({
                "student_id":      student_id,
                "full_name":       name,
                "email":           email,
                "password":        generate_password(),
                "academic_year":   academic_year,
                "gpa":             gpa,
                "completed_hours": completed,
                "specialization":  major["name"],
            })
            
            major_generated_count += 1

    return students


def insert_students(students):
    conn   = mysql.connector.connect(
        host=DB_HOST, user=DB_USER,
        password=DB_PASSWORD, database=DB_NAME
    )
    cursor = conn.cursor()

    sql = """
        INSERT INTO students
        (student_id, full_name, email, password,
         academic_year, gpa, completed_hours, specialization)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """

    success = 0
    for s in students:
        try:
            cursor.execute(sql, (
                s["student_id"], s["full_name"],   s["email"],
                s["password"],  s["academic_year"], s["gpa"],
                s["completed_hours"], s["specialization"],
            ))
            success += 1
        except mysql.connector.Error as e:
            print(f"خطأ في إدخال {s['student_id']}: {e}")

    conn.commit()
    cursor.close()
    conn.close()
    print(f"✅ تم إدخال {success} طالب بنجاح!")


if __name__ == "__main__":
    print("⏳ جاري توليد الطلاب بالتساوي حسب التخصصات...")
    students = generate_students()

    print("\n=== عينة من الطلاب المولدين ===")
    for s in list(students)[::15]: # أخذ عينات متباعدة لتغطية التخصصات المختلفة في المعاينة
        print(f"{s['student_id']} | {s['full_name']} | {s['specialization']} | المعدل: {s['gpa']}%")

    print(f"\n📊 إجمالي الطلاب الجاهزين للرفع: {len(students)} طالب (25 طالب لكل تخصص)")
    confirm = input("\nهل تريد إدخال البيانات الحالية في قاعدة البيانات؟ (y/n): ")
    if confirm.lower() == "y":
        insert_students(students)
