import os
import pandas as pd
import numpy as np
import re
import pickle
import faiss
from sentence_transformers import SentenceTransformer
from rank_bm25 import BM25Okapi

# 470 MB, 118M params — хватает для коротких текстов? замени на intfloat/multilingual-e5-base - если есть ошибки
MODEL_NAME = "intfloat/multilingual-e5-base"
MODEL_CACHE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "models")  # кеш рядом с проектом


df = pd.read_excel("data/medicines.xlsx", skiprows=2, dtype=str)
df.columns = [
    "МНН", "Торговое_наименование", "Лекарственная_форма",
    "Производитель", "Код_АТХ", "Количество", "Предельная_цена",
    "Цена_указана", "Номер_РУ", "Дата_регистрации", "Штрихкод", "Дата_вступления"
]
df["Предельная_цена"] = (
    df["Предельная_цена"].str.replace(r"\s+", "", regex=True)
    .str.replace(",", ".").astype(float)
)
df["Количество"] = pd.to_numeric(df["Количество"].str.strip(), errors="coerce").astype("Int64")


UNITS = (
    r'(?:'
    r'мг/мл|мкг/мл|мг/г|мкг/доза|мг/доза|МЕ/мл|ЕД/мл|мг/сут|АЕ/доза'
    r'|млн\.?\s*МЕ|тыс\.?\s*МЕ|тыс\.?\s*Ед\.?\s*Евр\.?\s*Ф\.?|тыс\.?\s*ЕД'
    r'|мг|г|мл|мкг|%|МЕ|ЕД|ТЕД|ммоль|КИЕ|МБк|кг|л'
    r'|накожн\w*\s+доз\w*|доз\w?'
    r'|см'
    r')'
)
DOSE_PATTERN = re.compile(
    r'(\d+[\.,]?\d*(?:\s*[\+\-]\s*\d+[\.,]?\d*)*\s*' + UNITS + r')(?:/(?:мл|г|доза|таб|сут))?'
)
DIMENSIONS_PATTERN = re.compile(
    r'(\d+[\.,]?\d*\s*[хxХX×]\s*\d+[\.,]?\d*(?:\s*[хxХX×]\s*\d+[\.,]?\d*)?\s*см)'
)
RANGE_DOSE_PATTERN = re.compile(r'(\d+[\-–]\d+\s*' + UNITS + r')')

def parse_lek_forma(s):
    if pd.isna(s):
        return pd.Series({"форма_выпуска": None, "дозировка": None})
    s = str(s).strip()
    forma_match = re.match(r'^([^,]+)', s)
    forma = forma_match.group(1).strip() if forma_match else None
    if re.search(r'\bNULL\b|Не указано', s):
        return pd.Series({"форма_выпуска": forma, "дозировка": None})
    dims = DIMENSIONS_PATTERN.findall(s)
    if dims:
        return pd.Series({"форма_выпуска": forma, "дозировка": dims[0].strip()})
    range_match = RANGE_DOSE_PATTERN.findall(s)
    if range_match:
        return pd.Series({"форма_выпуска": forma, "дозировка": range_match[0].strip()})
    doses = DOSE_PATTERN.findall(s)
    if doses:
        return pd.Series({"форма_выпуска": forma, "дозировка": doses[0].strip()})
    bare_number = re.search(r',\s*(\d+[,\.]\d+)\s*,', s)
    if bare_number:
        return pd.Series({"форма_выпуска": forma, "дозировка": bare_number.group(1)})
    return pd.Series({"форма_выпуска": forma, "дозировка": None})

parsed = df["Лекарственная_форма"].apply(parse_lek_forma)
df["форма_выпуска"] = parsed["форма_выпуска"]
df["дозировка"] = parsed["дозировка"]


def extract_owner(s):
    if pd.isna(s):
        return None
    s = str(s).strip()
    s = re.sub(r'^(?:Вл\.)?(?:Вып\.к\.)?(?:Перв\.Уп\.)?(?:Втор\.Уп\.)?(?:Пр\.)?', '', s).strip()
    first_company = s.split(';')[0].strip()
    return clean_name(first_company)

def clean_name(s):
    if not s:
        return None
    s = re.sub(r'(?:Открытое |Закрытое |Непубличное |Публичное )?[Аа]кционерное общество\s*', '', s)
    s = re.sub(r'Общество с ограниченной ответственностью\s*', '', s)
    s = re.sub(r'Федеральное государственное унитарное предприятие\s*', '', s)
    s = re.sub(r'Государственное унитарное предприятие\s*', '', s)
    s = re.sub(r'Унитарное предприятие\s*', '', s)
    s = re.sub(
        r'\(\s*(?:ОАО|ООО|ЗАО|ПАО|АО|НАО|НПАО|ФГУП|ГУП|НПО)\s*["\u00AB\'].*?[\'\u00BB"]\s*\)', '', s
    )
    s = re.sub(r'\(\s*\d{10,13}\s*\)', '', s)
    s = re.sub(r'["\u00AB\u00BB\'\u2018\u2019\u201C\u201D]', '', s)
    s = re.sub(r'\b(?:Вл|Вып|Перв|Втор|Пр)\.\S*', '', s)
    s = re.sub(r'\(\s*\)', '', s)
    s = re.sub(r'[;,]\s*$', '', s)
    s = re.sub(r'\s{2,}', ' ', s).strip()
    s = re.sub(r'^,\s*', '', s).strip()
    return s if s else None

df["производитель_чист"] = df["Производитель"].apply(extract_owner)


def preprocess_lek_forma(s):
    """Обрезает строку Лекарственная_форма до первого дефиса/тире."""
    if pd.isna(s):
        return ""
    s = str(s).strip()
    return re.split(r'\s*[-–—]\s*', s)[0].strip()


def build_embedding_text(row):
    mnn = str(row["МНН"]).strip() if pd.notna(row["МНН"]) else ""
    trade = str(row["Торговое_наименование"]).strip() if pd.notna(row["Торговое_наименование"]) else ""
    manufacturer = str(row["производитель_чист"]).strip() if pd.notna(row["производитель_чист"]) else ""

    if mnn.lower() == trade.lower():
        name_part = mnn
    else:
        name_part = f"{mnn} {trade}"

    parts = [p for p in [name_part, manufacturer] if p]
    return " | ".join(parts)

def build_for_embeding(row):
    """Итоговый текст для FAISS-энкодера и BM25.
    Структура: name_part + clean(форма_до_тире + производитель_чист)
    где clean = lowercase, пунктуация/дефисы/слэши → пробелы.
    """
    mnn = str(row["МНН"]).strip() if pd.notna(row["МНН"]) else ""
    trade = str(row["Торговое_наименование"]).strip() if pd.notna(row["Торговое_наименование"]) else ""
    name_part = mnn if mnn.lower() == trade.lower() else f"{mnn} {trade}"

    forma = preprocess_lek_forma(row["Лекарственная_форма"])
    producer = str(row["производитель_чист"]).strip() if pd.notna(row["производитель_чист"]) else ""
    extra = f"{forma} {producer}".lower()
    extra = re.sub(r'[-/\\]', ' ', extra)
    extra = re.sub(r'[^\w\s]', ' ', extra)
    extra = re.sub(r'\s+', ' ', extra).strip()

    return f"{name_part} {extra}".strip()


df["for_embeding"] = df.apply(build_for_embeding, axis=1)

print(f"Записей: {len(df)}")
print(f"\nПримеры for_embeding:")
for v in df["for_embeding"].sample(10, random_state=42).values:
    print(f"  {v}")

print(f"\nЗагрузка модели {MODEL_NAME}...")
print(f"Кеш: {MODEL_CACHE_DIR}")
model = SentenceTransformer(MODEL_NAME, cache_folder=MODEL_CACHE_DIR)

passages = ["passage: " + t for t in df["for_embeding"].values]

print("Кодирование документов...")
embeddings = model.encode(passages, batch_size=256, show_progress_bar=True, normalize_embeddings=True)
embeddings = np.array(embeddings, dtype="float32")

dimension = embeddings.shape[1]
index = faiss.IndexFlatIP(dimension)
index.add(embeddings)

print(f"FAISS индекс построен: {index.ntotal} векторов, размерность {dimension}")

def tokenize(text):
    return text.lower().split()

corpus_tokenized = [tokenize(t) for t in df["for_embeding"].values]
bm25 = BM25Okapi(corpus_tokenized)

print(f"BM25 индекс построен: {len(corpus_tokenized)} документов")

metadata = df.to_dict(orient="records")

faiss.write_index(index, "data/faiss_index.bin")

with open("data/bm25_index.pkl", "wb") as f:
    pickle.dump(bm25, f)

with open("data/metadata.pkl", "wb") as f:
    pickle.dump(metadata, f)

with open("data/corpus_tokenized.pkl", "wb") as f:
    pickle.dump(corpus_tokenized, f)

print("\nСохранено:")
print("  data/faiss_index.bin — FAISS индекс")
print("  data/bm25_index.pkl — BM25 индекс")
print("  data/metadata.pkl — метаданные записей")
print("  data/corpus_tokenized.pkl — токенизированный корпус для BM25")

def hybrid_search(query, top_k=10, bm25_weight=0.4):
    query_emb = model.encode(["query: " + query], normalize_embeddings=True).astype("float32")
    dense_scores, dense_ids = index.search(query_emb, min(top_k * 3, index.ntotal))
    dense_scores = dense_scores[0]
    dense_ids = dense_ids[0]
    dense_weight = 1.0 - bm25_weight

    bm25_scores = bm25.get_scores(tokenize(query))

    combined = {}
    dense_max = dense_scores.max() if dense_scores.max() > 0 else 1.0
    bm25_max = bm25_scores.max() if bm25_scores.max() > 0 else 1.0

    for i, idx in enumerate(dense_ids):
        combined[idx] = dense_weight * (dense_scores[i] / dense_max)

    for idx in np.argsort(bm25_scores)[-top_k * 3:]:
        score = bm25_weight * (bm25_scores[idx] / bm25_max)
        combined[idx] = combined.get(idx, 0) + score

    ranked = sorted(combined.items(), key=lambda x: x[1], reverse=True)[:top_k]
    return [(metadata[idx], score) for idx, score in ranked]


if __name__ == '__main__':
    test_queries = [
        "парацетамол",
        "ибупрофен таблетки",
        "амоксициллин",
        "Панадол",
    ]

    for q in test_queries:
        print(f"\nЗапрос: '{q}'")
        print("-" * 60)
        results = hybrid_search(q, top_k=5)
        for meta, score in results:
            print(f"  [{score:.3f}] {meta['for_embeding']}")
            print(f"         Форма: {meta['форма_выпуска']} | Доза: {meta['дозировка']} | Цена: {meta['Предельная_цена']}")
            print(f"количество={meta['Количество']} код АТХ={meta['Код_АТХ']}")