"""
RAG evaluation script using RAGAS framework.

Metrics (без LLM):
  - semantic_similarity — косинусное сходство эмбеддингов ответа и ground_truth(эталонный ответ найденный из метадаты)

Запуск (из корня проекта):
    python3.10 ragas_test/evaluate_rag.py

Требования:
  - Построенные индексы (python3.10 engine.py)
  - Ollama не нужен
"""

import os
import sys
import re
import json
import pickle
import random
import warnings
import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import faiss
from sentence_transformers import SentenceTransformer
from rank_bm25 import BM25Okapi
from ragas.metrics.collections import SemanticSimilarity
from ragas.embeddings import HuggingFaceEmbeddings as RagasHFEmbeddings
MODEL_NAME = "intfloat/multilingual-e5-base"
MODEL_CACHE_DIR = os.path.join(ROOT, "models")
DATA_DIR = os.path.join(ROOT, "data")

DATASET_SIZE = 30        # number of test queries to generate
TOP_K = 5                # documents retrieved per query
DENSE_WEIGHT = 0.7
BM25_WEIGHT = 0.3
MIN_SCORE = 0.3
GAP_RATIO = 0.5

RANDOM_SEED = 42
random.seed(RANDOM_SEED)
np.random.seed(RANDOM_SEED)

OUTPUT_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results.json")


def load_indexes():
    print("Загрузка индексов...")
    index = faiss.read_index(os.path.join(DATA_DIR, "faiss_index.bin"))
    with open(os.path.join(DATA_DIR, "bm25_index.pkl"), "rb") as f:
        bm25 = pickle.load(f)
    with open(os.path.join(DATA_DIR, "metadata.pkl"), "rb") as f:
        metadata = pickle.load(f)
    print(f"  FAISS: {index.ntotal} векторов  |  метаданные: {len(metadata)} записей")
    return index, bm25, metadata


def load_model():
    print(f"Загрузка эмбеддинговой модели {MODEL_NAME}...")
    return SentenceTransformer(MODEL_NAME, cache_folder=MODEL_CACHE_DIR)


def tokenize(text: str):
    return text.lower().split()


def hybrid_search(query, model, index, bm25, metadata, top_k=TOP_K):
    query_emb = model.encode(["query: " + query], normalize_embeddings=True).astype("float32")
    dense_scores, dense_ids = index.search(query_emb, min(top_k * 3, index.ntotal))
    dense_scores = dense_scores[0]
    dense_ids = dense_ids[0]

    bm25_scores = bm25.get_scores(tokenize(query))

    combined = {}
    dense_max = dense_scores.max() if dense_scores.max() > 0 else 1.0
    bm25_max = bm25_scores.max() if bm25_scores.max() > 0 else 1.0

    for i, idx in enumerate(dense_ids):
        combined[idx] = DENSE_WEIGHT * (dense_scores[i] / dense_max)

    for idx in np.argsort(bm25_scores)[-(top_k * 3):]:
        b = BM25_WEIGHT * (bm25_scores[idx] / bm25_max)
        combined[idx] = combined.get(idx, 0) + b

    ranked = sorted(combined.items(), key=lambda x: x[1], reverse=True)
    if not ranked:
        return []

    top_score = ranked[0][1]
    cutoff = max(MIN_SCORE, top_score * GAP_RATIO)

    results = []
    for idx, score in ranked:
        if score < cutoff:
            break
        results.append((metadata[idx], score))
        if len(results) >= top_k:
            break

    return results


def build_answer(query: str, results: list) -> str:
    if not results:
        return "Данное лекарство не найдено в реестре ЖНВЛП."

    top_meta, top_score = results[0]
    mnn = top_meta.get("МНН", "")
    trade = top_meta.get("Торговое_наименование", "")
    forma = top_meta.get("форма_выпуска", "")
    dose = top_meta.get("дозировка", "")
    price = top_meta.get("Предельная_цена", "")

    name = trade if trade else mnn
    answer = f"В реестре найден препарат «{name}»"
    if mnn and trade and mnn != trade:
        answer += f" (МНН: {mnn})"
    if forma:
        answer += f", форма выпуска: {forma}"
    if dose:
        answer += f", дозировка: {dose}"
    if price:
        answer += f". Предельная зарегистрированная цена: {price} руб."
    return answer + "."


def load_excel():
    path = os.path.join(DATA_DIR, "medicines.xlsx")
    df = pd.read_excel(path, skiprows=2, dtype=str)
    df.columns = [
        "МНН", "Торговое_наименование", "Лекарственная_форма",
        "Производитель", "Код_АТХ", "Количество", "Предельная_цена",
        "Цена_указана", "Номер_РУ", "Дата_регистрации", "Штрихкод", "Дата_вступления"
    ]
    df = df.dropna(subset=["МНН", "Торговое_наименование"]).copy()
    df["МНН"] = df["МНН"].str.strip()
    df["Торговое_наименование"] = df["Торговое_наименование"].str.strip()
    df["Лекарственная_форма"] = df["Лекарственная_форма"].fillna("").str.strip()
    return df


def extract_forma(lf: str) -> str:
    """Get form before first comma."""
    return lf.split(",")[0].strip() if lf else ""


def extract_forma_short(lf: str) -> str:
    """Первое слово + подстрока от первой цифры до первого тире/дефиса.
    Пример: 'таблетки, покрытые оболочкой, 400 мг, 30 шт. - банки'
             → 'таблетки 400 мг, 30 шт.'
    """
    if not lf:
        return ""
    first_word = lf.split()[0]
    digit_match = re.search(r'\d', lf)
    if not digit_match:
        return first_word
    start = digit_match.start()
    dash_match = re.search(r'\s*[-–—]\s*', lf[start:])
    if dash_match:
        dose_part = lf[start: start + dash_match.start()].strip()
    else:
        dose_part = lf[start:].strip()
    return f"{first_word} {dose_part}" if dose_part else first_word


def build_ground_truth(row: pd.Series) -> str:
    mnn = row["МНН"]
    trade = row["Торговое_наименование"]
    forma = row["Лекарственная_форма"]

    name = trade if trade else mnn
    gt = f"«{name}»"
    if mnn and trade and mnn.lower() != trade.lower():
        gt += f" (МНН: {mnn})"
    if forma:
        gt += f" — {forma}"
    return gt + " зарегистрирован в реестре ЖНВЛП."


def _mutate_mnn(mnn: str) -> str:
    """Применяет одну из мутаций к МНН (взаимоисключающие, p=0.2 каждая).
      - p < 0.2  → переставить местами два случайных соседних символа
      - p < 0.4  → обрезать последние 2 буквы
      - иначе    → оставить без изменений
    """
    p = random.random()
    if p < 0.2 and len(mnn) >= 2:
        i = random.randint(0, len(mnn) - 2)
        lst = list(mnn)
        lst[i], lst[i + 1] = lst[i + 1], lst[i]
        return "".join(lst)
    if p < 0.4 and len(mnn) > 2:
        return mnn[:-2]
    return mnn


# Query variants: МНН (с мутацией), торговое наименование, МНН+форма_short
def make_queries(row: pd.Series) -> list:
    mnn = row["МНН"]
    trade = row["Торговое_наименование"]
    lf = row["Лекарственная_форма"]

    forma_short = extract_forma_short(lf)   # первое слово + дозировка до тире

    queries = []
    queries.append(_mutate_mnn(mnn))              # МНН (иногда с опечаткой/обрезкой)
    if forma_short:
        queries.append(f"{mnn} {forma_short}")    # МНН + короткая форма
    return queries


def generate_test_dataset(df: pd.DataFrame, n: int = DATASET_SIZE):
    """Sample unique МНН, build (question, ground_truth) pairs."""
    unique_mnns = df["МНН"].dropna().unique().tolist()
    sampled_mnns = random.sample(unique_mnns, min(n, len(unique_mnns)))

    rows = []
    for mnn in sampled_mnns:
        sub = df[df["МНН"] == mnn]
        row = sub.iloc[0]

        queries = make_queries(row)
        query = random.choice(queries)
        ground_truth = build_ground_truth(row)

        rows.append({
            "question": query,
            "ground_truth": ground_truth,
            "mnn": mnn,
            "trade": row["Торговое_наименование"],
            "forma": extract_forma(row["Лекарственная_форма"]),
        })

    return rows



def main():
    index, bm25, metadata = load_indexes()
    model = load_model()
    print("\nГенерация тестового датасета...")
    df = load_excel()
    test_cases = generate_test_dataset(df, n=DATASET_SIZE)
    print(f"  Сгенерировано запросов: {len(test_cases)}")
    print("\nВыполнение гибридного поиска...")
    questions, answers, ground_truths = [], [], []

    for i, tc in enumerate(test_cases):
        query = tc["question"]
        results = hybrid_search(query, model, index, bm25, metadata)

        answer = build_answer(query, results)

        questions.append(query)
        answers.append(answer)
        ground_truths.append(tc["ground_truth"])

        if (i + 1) % 10 == 0 or i == 0:
            print(f"  [{i+1}/{len(test_cases)}] q='{query}'")


    print(f"\nНастройка эмбеддингов ({MODEL_NAME})...")
    ragas_emb = RagasHFEmbeddings(model=MODEL_NAME, cache_folder=MODEL_CACHE_DIR)
    sim_metric = SemanticSimilarity(embeddings=ragas_emb)
    print("\nВычисление метрик...")
    per_sample = []
    for i, (q, ans, gt) in enumerate(zip(questions, answers, ground_truths)):
        sim = sim_metric.score(reference=gt, response=ans).value
        per_sample.append({"question": q, "answer": ans, "ground_truth": gt,
                            "semantic_similarity": sim})
        if (i + 1) % 10 == 0 or i == 0:
            print(f"  [{i+1}/{len(questions)}] sim={sim:.3f}  q='{q}'")
    sim_vals = [r["semantic_similarity"] for r in per_sample]
    agg = {
        "semantic_similarity": round(float(np.mean(sim_vals)), 4),
    }
    print("\n" + "=" * 60)
    print("РЕЗУЛЬТАТЫ ОЦЕНКИ RAG")
    print("=" * 60)

    metric_map = {
        "semantic_similarity": "Semantic Similarity (косинусное сходство эмбеддингов)",
    }
    for key, label in metric_map.items():
        val = agg[key]
        marker = "✓" if val >= 0.7 else ("~" if val >= 0.5 else "✗")
        print(f"  [{marker}] {label}: {val:.4f}")

    print("=" * 60)

    output = {
        "config": {
            "dataset_size": DATASET_SIZE,
            "top_k": TOP_K,
            "dense_weight": DENSE_WEIGHT,
            "bm25_weight": BM25_WEIGHT,
            "min_score": MIN_SCORE,
            "gap_ratio": GAP_RATIO,
            "embeddings_model": MODEL_NAME,
        },
        "aggregate_scores": agg,
        "per_sample": per_sample,
    }

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2, default=str)

    print(f"\nРезультаты сохранены: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
