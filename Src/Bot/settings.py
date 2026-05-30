import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ─── ملفات Excel ───
FACULTY_EXCEL   = os.path.join(BASE_DIR, "Bot_Memory", "Excel", "Faculty_Hub.xlsx")
HOURS_EXCEL     = os.path.join(BASE_DIR, "Bot_Memory", "Excel", "Hours.xlsx")
MATERIALS_EXCEL = os.path.join(BASE_DIR, "Bot_Memory", "Excel", "Materials_Newpaper.xlsx")

# ─── ملفات JSON ───
FACULTY_JSON      = os.path.join(BASE_DIR, "Bot_Memory", "Json", "Faculty_Hub.json")
HOURS_JSON        = os.path.join(BASE_DIR, "Bot_Memory", "Json", "Hours.json")
MATERIALS_JSON    = os.path.join(BASE_DIR, "Bot_Memory", "Json", "materials.json")
CALENDER_JSON     = os.path.join(BASE_DIR, "Bot_Memory", "Json", "calender.json")
LAWS_JSON         = os.path.join(BASE_DIR, "Bot_Memory", "Json", "laws.json")
INSTRUCTIONS_JSON = os.path.join(BASE_DIR, "Bot_Memory", "Json", "instructions.json")

# ─── ملفات FAISS ───
FAISS_INDEX = os.path.join(BASE_DIR, "DB.index")
CHUNKS_PKL  = os.path.join(BASE_DIR, "chunks.pkl")

