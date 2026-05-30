import re
from search import get_context, semantic_search
from query_normalize import normalize_query
from prompts import ACADEMIC_PROMPT, GENERAL_PROMPT
import keywords as key
import ollama


# ─── client بدون timeout ───
ollama_client = ollama.Client(timeout=None)


# =============================================================================
# دوال مساعدة
# =============================================================================

def _quick_normalize(text):
    """تطبيع سريع للكشف عن الكلمات المفتاحية (دون حذف stop words)"""
    text = re.sub(r'[\u0617-\u061A\u064B-\u0652]', '', text)
    text = re.sub(r'[أإآا]', 'ا', text)
    text = re.sub(r'[ة]', 'ه', text)
    text = re.sub(r'[^\w\s]', '', text)
    return text


def format_history(history):
    formatted = ""
    for turn in history:
        formatted += f"طالب: {turn['question']}\n"
        formatted += f"مساعد: {turn['answer']}\n"
    return formatted


# =============================================================================
# مجموعات الكلمات المفتاحية
# =============================================================================

ALL_ACADEMIC_KEYWORDS = (
    key.FACULTY_KEYWORDS      |
    key.HOURS_KEYWORDS        |
    key.MATERIALS_KEYWORDS    |
    key.CALENDER_KEYWORDS     |
    key.LAWS_KEYWORDS         |
    key.INSTRUCTIONS_KEYWORDS
)


# =============================================================================
# تحديد نوع السؤال
# =============================================================================

def is_academic_question(question, threshold=0.42):
    """تحديد إذا كان السؤال أكاديمياً عبر الكلمات المفتاحية أولاً ثم الدلالة"""
    normalized = _quick_normalize(question)
    words = set(normalized.split())
    if words & ALL_ACADEMIC_KEYWORDS:
        return True

    results   = semantic_search(question, top_k=1)
    top_score = results[0][1]
    print(f"نسبة التشابه: {top_score:.2f}")
    return top_score >= threshold


# =============================================================================
# الدالة الرئيسية
# =============================================================================

def ask(question, history=None, student_id=None):
    if history is None:
        history = []

    # ─── سؤال أكاديمي (FAISS) ───
    if is_academic_question(question):
        clean_question = normalize_query(question)
        context        = get_context(clean_question)
        print(f"--- context ---\n{context}\n---------------")
        prompt = ACADEMIC_PROMPT.format(
            context=context,
            history=format_history(history),
            query=question
        )

    # ─── سؤال عام ───
    else:
        prompt = GENERAL_PROMPT.format(
            history=format_history(history),
            query=question
        )

    response = ollama_client.chat(
        model="llama3",
        messages=[{"role": "user", "content": prompt}]
    )
    try:
        answer = response.message.content
    except AttributeError:
        answer = response["message"]["content"]

    history.append({"question": question, "answer": answer})
    return answer, history


# =============================================================================
# تشغيل من الـ  sofyan tarawneh Terminal مباشرة (للاختبار)
# =============================================================================

if __name__ == "__main__":
    history = []
    print("مرحباً! أنا المساعد الأكاديمي لجامعة مؤتة. اكتب 'خروج' للإنهاء.\n")
    while True:
        question = input("سؤالك: ")
        if question == "خروج":
            break
        answer, history = ask(question, history, student_id=None)
        print(f"\nالجواب: {answer}\n")
