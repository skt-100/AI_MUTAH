import json
import settings as st


def load_json(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


faculty_list      = load_json(st.FACULTY_JSON)
hours_list        = load_json(st.HOURS_JSON)
materials_list    = load_json(st.MATERIALS_JSON)
calender_list     = load_json(st.CALENDER_JSON)
laws_list         = load_json(st.LAWS_JSON)
instructions_list = load_json(st.INSTRUCTIONS_JSON)

chunks = []

# ── Faculty Hub ───────────────────────────────────────────────────────────
for item in faculty_list:
    chunks.append({
        "النوع":  item["النوع"],
        "الاسم":  item["الاسم"],
        "الرتبة": item.get("الرتبة", ""),
        "القسم":  item.get("القسم", ""),
        "البريد": item.get("البريد", ""),
        "النص":   item["النص"],
    })

# ── Hours ─────────────────────────────────────────────────────────────────
for item in hours_list:
    chunks.append({
        "النوع":   item["النوع"],
        "التخصص": item["التخصص"],
        "النص":    item["النص"],
    })

# ── Materials — chunk واحد لكل مادة يحتوي كل شعبها ───────────────────────
for item in materials_list:
    chunks.append({
        "النوع":          item["النوع"],
        "رقم_المادة":    item["رقم_المادة"],
        "اسم_المادة":    item["اسم_المادة"],
        "التخصص":        item.get("التخصص", ""),
        "إجمالي_الشعب": item.get("إجمالي_الشعب", 1),
        "النص":          item["النص"],
    })

# ── Calender ──────────────────────────────────────────────────────────────
for item in calender_list:
    chunks.append({
        "النوع":         item["النوع"],
        "المناسبة":      item["المناسبة"],
        "التاريخ":       item.get("التاريخ", ""),
        "التاريخ_من":    item.get("التاريخ_من", ""),
        "التاريخ_إلى":  item.get("التاريخ_إلى", ""),
        "عطلة":          item.get("عطلة", False),
        "تقديري":        item.get("تقديري", False),
        "الفصل":         item.get("الفصل", ""),
        "العام_الجامعي": item.get("العام_الجامعي", ""),
        "النص":          item["النص"],
    })

# ── Laws ──────────────────────────────────────────────────────────────────
for item in laws_list:
    chunks.append({
        "النوع":          item["النوع"],
        "رقم_الوثيقة":   item.get("رقم_الوثيقة", ""),
        "عنوان_الوثيقة": item.get("عنوان_الوثيقة", ""),
        "رقم_القانون":   item.get("رقم_القانون", ""),
        "عنوان_القانون": item.get("عنوان_القانون", ""),
        "النص":          item["النص"],
    })

# ── Instructions ──────────────────────────────────────────────────────────
for item in instructions_list:
    chunks.append({
        "النوع":          item["النوع"],
        "رقم_الوثيقة":   item.get("رقم_الوثيقة", ""),
        "عنوان_الوثيقة": item.get("عنوان_الوثيقة", ""),
        "رقم_المادة":    item.get("رقم_المادة", ""),
        "عنوان_المادة":  item.get("عنوان_المادة", ""),
        "النص":          item["النص"],
    })


if __name__ == "__main__":
    print(f"تم! عدد الـ chunks: {len(chunks)}")
    print(f"  أعضاء هيئة تدريس : {len(faculty_list)}")
    print(f"  تخصصات (ساعات)   : {len(hours_list)}")
    print(f"  مواد              : {len(materials_list)}")
    print(f"  أحداث التقويم    : {len(calender_list)}")
    print(f"  قوانين جامعية    : {len(laws_list)}")
    print(f"  تعليمات جامعية   : {len(instructions_list)}")
