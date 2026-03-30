import os
import pickle
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer

MODEL_NAME = "intfloat/multilingual-e5-base"
MODEL_CACHE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "models")

print("Загрузка FAISS индекса...")
index = faiss.read_index("data/faiss_index.bin")
print(f"  Векторов: {index.ntotal}, размерность: {index.d}")

print("Загрузка BM25 индекса...")
with open("data/bm25_index.pkl", "rb") as f:
    bm25 = pickle.load(f)

with open("data/metadata.pkl", "rb") as f:
    metadata = pickle.load(f)

with open("data/corpus_tokenized.pkl", "rb") as f:
    corpus_tokenized = pickle.load(f)

print(f"  Документов: {len(metadata)}")

print(f"Загрузка модели {MODEL_NAME}...")
model = SentenceTransformer(MODEL_NAME, cache_folder=MODEL_CACHE_DIR)


def tokenize(text):
    return text.lower().split()

def hybrid_search(
    query,
    top_k=10,
    bm25_weight=0.3,
    dense_weight=0.7,
    min_score=0.3,       # абсолютный порог — ниже не показываем
    gap_ratio=0.5,       # если score < top_score * gap_ratio — обрезаем
    debug=False,
):
    query_emb = model.encode(["query: " + query], normalize_embeddings=True).astype("float32")
    dense_scores, dense_ids = index.search(query_emb, min(top_k * 3, index.ntotal))
    dense_scores = dense_scores[0]
    dense_ids = dense_ids[0]

    bm25_scores = bm25.get_scores(tokenize(query))

    combined = {}
    score_details = {}

    dense_max = dense_scores.max() if dense_scores.max() > 0 else 1.0
    bm25_max = bm25_scores.max() if bm25_scores.max() > 0 else 1.0

    for i, idx in enumerate(dense_ids):
        d = dense_weight * (dense_scores[i] / dense_max)
        combined[idx] = d
        score_details[idx] = {"dense": d, "bm25": 0.0}

    for idx in np.argsort(bm25_scores)[-top_k * 3:]:
        b = bm25_weight * (bm25_scores[idx] / bm25_max)
        combined[idx] = combined.get(idx, 0) + b
        if idx not in score_details:
            score_details[idx] = {"dense": 0.0, "bm25": 0.0}
        score_details[idx]["bm25"] = b

    ranked = sorted(combined.items(), key=lambda x: x[1], reverse=True)

    if not ranked:
        return []

    top_score = ranked[0][1]
    cutoff = max(min_score, top_score * gap_ratio)

    filtered = []
    for idx, score in ranked:
        if score < cutoff:
            break
        filtered.append((metadata[idx], score, score_details.get(idx, {})))
        if len(filtered) >= top_k:
            break

    if debug and ranked:
        print(f"    [debug] top_score={top_score:.3f}, cutoff={cutoff:.3f}, "
              f"до фильтра={len(ranked)}, после={len(filtered)}")

    return filtered

def print_results(query, results, debug=False):
    print(f"\n{'='*80}")
    print(f"  ЗАПРОС: '{query}'")
    print(f"{'='*80}")
    if not results:
        print("  (ничего не найдено)")
        return
    for i, (meta, score, details) in enumerate(results, 1):
        d = details.get("dense", 0)
        b = details.get("bm25", 0)
        tag = ""
        if b > 0 and d > 0:
            tag = " [dense+bm25]"
        elif b > 0:
            tag = " [bm25]"
        else:
            tag = " [dense]"
        print(f"  {i}. [{score:.3f}] (d={d:.2f} b={b:.2f}){tag} {meta['for_embeding']}")
        print(f"     Форма: {meta.get('форма_выпуска', '—')} | Доза: {meta.get('дозировка', '—')} "
              f"| Цена: {meta['Предельная_цена']} | Кол-во: {meta.get('Количество', '—')}")
    print()


tests = {
    "Точное совпадение МНН": [
        "парацетамол",
        "ибупрофен",
        "амоксициллин",
    ],

    "Торговое наименование (должен найти МНН)": [
        "Панадол",        # парацетамол
        "Нурофен",        # ибупрофен
        "Сумамед",        # азитромицин
        "Мезим",          # панкреатин
    ],

    "Опечатки / неточный ввод": [
        "порацетамол",
        "ибупрафен",
        "амоксицилин",    # одна 'л' вместо двух
    ],

    "Производитель в запросе": [
        "парацетамол Фармстандарт",
        "ибупрофен Синтез",
    ],

    "Комбинированные препараты": [
        "амоксициллин клавулановая кислота",
    ],

    "Латиница / транслит": [
        "paracetamol",
        "ibuprofen",
    ],

    "Разговорный / бытовой запрос": [
        "обезболивающее",
        "антибиотик",
        "от давления",
    ],
}

for category, queries in tests.items():
    print()
    print(f"КАТЕГОРИЯ: {category}")
    print()
    for q in queries:
        results = hybrid_search(q, top_k=5)
        print_results(q, results)