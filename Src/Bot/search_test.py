from search import get_context, hybrid_search
from query_normalize import normalize_query

def test_query(question):
    print(f"السؤال الأصلي: {question}")
    
    clean_question = normalize_query(question)
    print(f"السؤال بعد التنظيف: {clean_question}")
    
    top_chunks = hybrid_search(clean_question)
    print(f"\nالـ chunks المرجعة:")
    for i, chunk in enumerate(top_chunks):
        print(f"\n--- chunk {i+1} ---")
        print(chunk["النص"])

if __name__ == "__main__":
    while True:
        question = input("\nاكتب سؤالك: ")
        if question == "خروج":
            break
        test_query(question)
        clean_question = normalize_query(question)
        print(f"الكلمات بعد التنظيف: {clean_question.split()}")
