from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import pickle
from chunks import chunks

def create_embeddings():
    # 1. تحميل النموذج
    print("--- جاري تحميل نموذج BGE-M3 ---")
    model = SentenceTransformer('BAAI/bge-m3')

    # 2. استخراج النصوص
    texts = [chunk["النص"] for chunk in chunks]
    print(f"--- جاري تحويل {len(texts)} chunks إلى متجهات ---")

    # 3. توليد الـ embeddings مع normalize
    embeddings = model.encode(texts, show_progress_bar=True, normalize_embeddings=True)

    # 4. بناء فهرس FAISS
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatIP(dimension)
    index.add(np.array(embeddings).astype('float32'))

    # 5. حفظ الفهرس
    faiss.write_index(index, "DB.index")
    print("--- تم حفظ الفهرس بنجاح ---")

    # 6. حفظ الـ chunks
    with open("chunks.pkl", "wb") as f:
        pickle.dump(chunks, f)
    print("--- تم حفظ الـ chunks بنجاح ---")

if __name__ == "__main__":
    create_embeddings()
