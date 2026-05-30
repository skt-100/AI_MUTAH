from sentence_transformers import SentenceTransformer, CrossEncoder
import faiss
import numpy as np
import pickle
import re
import keywords as key
from settings import FAISS_INDEX, CHUNKS_PKL

# ─── تحميل النموذج والفهرس والـ chunks (مرة واحدة عند بدء التشغيل) ───
model    = SentenceTransformer('BAAI/bge-m3')
index    = faiss.read_index(FAISS_INDEX)
reranker = CrossEncoder('BAAI/bge-reranker-base')

with open(CHUNKS_PKL, "rb") as f:
    chunks = pickle.load(f)


def _normalize(text):
    """تطبيع سريع قبل المقارنة بالكلمات المفتاحية"""
    text = re.sub(r'[\u0617-\u061A\u064B-\u0652]', '', text)
    text = re.sub(r'[أإآ]', 'ا', text)
    text = text.replace('ة', 'ه')
    return text


def detect_query_type(question):
    """تحديد نوع الاستعلام بناءً على الكلمات المفتاحية"""
    words = set(_normalize(question).split())
    scores = {
        "calender":     len(words & key.CALENDER_KEYWORDS),
        "laws":         len(words & key.LAWS_KEYWORDS),
        "instructions": len(words & key.INSTRUCTIONS_KEYWORDS),
        "hours":        len(words & key.HOURS_KEYWORDS),
        "faculty":      len(words & key.FACULTY_KEYWORDS),
        "materials":    len(words & key.MATERIALS_KEYWORDS),
    }
    best = max(scores, key=scores.get)
    if scores[best] > 0:
        return best
    return "general"


def keyword_search(question, top_k=5):
    words      = _normalize(question).split()
    results    = []

    for i, chunk in enumerate(chunks):
        score      = 0
        chunk_type = chunk.get("النوع", "")

        for word in words:
            if len(word) < 3:
                continue

            # --- مطابقة الحقول المحددة (أعلى أولوية) ---
            if "رقم_المادة"    in chunk and word in str(chunk["رقم_المادة"]):  score += 12
            if "اسم_المادة"    in chunk and word in chunk["اسم_المادة"]:       score += 8
            if "التخصص"        in chunk and word in chunk["التخصص"]:           score += 8
            if "الاسم"         in chunk and word in chunk["الاسم"]:            score += 8
            if "المناسبة"      in chunk and word in chunk["المناسبة"]:         score += 10
            if "عنوان_الوثيقة" in chunk and word in chunk["عنوان_الوثيقة"]:   score += 10
            if "عنوان_القانون" in chunk and word in chunk["عنوان_القانون"]:    score += 8
            if "عنوان_المادة"  in chunk and word in chunk["عنوان_المادة"]:     score += 8

            # --- مطابقة فئة الكلمة المفتاحية + وجودها في النص ---
            if word in key.HOURS_KEYWORDS     and word in chunk["النص"]: score += 5
            if word in key.FACULTY_KEYWORDS   and word in chunk["النص"]: score += 5
            if word in key.MATERIALS_KEYWORDS and word in chunk["النص"]: score += 5
            if word in key.CALENDER_KEYWORDS  and word in chunk["النص"]: score += 5

            # القوانين: score مرتفع فقط لـ chunk من نوع قوانين_جامعية
            if word in key.LAWS_KEYWORDS:
                if chunk_type == "قوانين_جامعية" and word in chunk["النص"]: score += 5
                elif word in chunk["النص"]:                                  score += 1

            # التعليمات: score مرتفع فقط لـ chunk من نوع تعليمات_جامعية
            if word in key.INSTRUCTIONS_KEYWORDS:
                if chunk_type == "تعليمات_جامعية" and word in chunk["النص"]: score += 5
                elif word in chunk["النص"]:                                    score += 1

            # --- مطابقة نصية عامة ---
            elif len(word) >= 4 and word in chunk["النص"]:
                score += 2

        if score > 0:
            results.append((i, score))

    results.sort(key=lambda x: x[1], reverse=True)
    return results[:top_k]


def semantic_search(question, top_k=5):
    question_vector = model.encode([question], normalize_embeddings=True)
    scores, indices = index.search(np.array(question_vector).astype('float32'), top_k)
    results = [(int(indices[0][i]), float(scores[0][i])) for i in range(top_k)]
    return results


def rerank(question, candidate_indices):
    """
    إعادة ترتيب المرشحين باستخدام BGE Reranker —
    يقيّم السؤال والـ chunk معاً في نفس الوقت (أدق من cos_sim)
    """
    pairs  = [(question, chunks[i]["النص"]) for i in candidate_indices]
    scores = reranker.predict(pairs)
    ranked = sorted(zip(candidate_indices, scores), key=lambda x: x[1], reverse=True)
    return ranked


def hybrid_search(question, top_k=5):
    retrieval_k = 20

    semantic_results = semantic_search(question, top_k=retrieval_k)
    keyword_results  = keyword_search(question,  top_k=retrieval_k)

    query_type = detect_query_type(question)
    max_kw     = max((s for _, s in keyword_results), default=1) if keyword_results else 1

    combined = {}

    # --- الجزء الدلالي (semantic) ---
    for i, score in semantic_results:

        # ─── عقوبة المختبر ───
        if ("اسم_المادة" in chunks[i] and
                not any(w in question for w in key.LAB_KEYWORDS) and
                any(w in chunks[i]["اسم_المادة"] for w in key.LAB_KEYWORDS)):
            score *= 0.3

        boost = 1.0
        if query_type == "hours"        and "التخصص"        in chunks[i]: boost = 1.5
        if query_type == "faculty"      and "الاسم"          in chunks[i]: boost = 1.5
        if query_type == "materials"    and "رقم_المادة"     in chunks[i]: boost = 1.5
        if query_type == "calender"     and "المناسبة"       in chunks[i]: boost = 1.8
        if (query_type == "laws" and
                "عنوان_الوثيقة" in chunks[i] and
                chunks[i].get("النوع") == "قوانين_جامعية"):               boost = 1.8
        if (query_type == "instructions" and
                "عنوان_الوثيقة" in chunks[i] and
                chunks[i].get("النوع") == "تعليمات_جامعية"):              boost = 1.8

        combined[i] = combined.get(i, 0) + score * boost

    # --- الجزء المعتمد على الكلمات المفتاحية ---
    for i, score in keyword_results:
        norm_score = score / max_kw
        combined[i] = combined.get(i, 0) + norm_score * 0.6

    # أخذ أفضل 10 مرشحين للـ reranker
    pre_ranked        = sorted(combined.items(), key=lambda x: x[1], reverse=True)[:10]
    candidate_indices = [i for i, _ in pre_ranked]

    # BGE Reranker — المرحلة النهائية
    reranked   = rerank(question, candidate_indices)
    top_chunks = [chunks[i] for i, _ in reranked[:top_k]]
    return top_chunks


def get_context(question):
    top_chunks = hybrid_search(question)
    parts      = [chunk["النص"] for chunk in top_chunks]
    return "\n---\n".join(parts)
