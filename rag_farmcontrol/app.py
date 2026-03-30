import os
import pickle
import re
import numpy as np
import faiss
import requests
import streamlit as st
import pandas as pd
from sentence_transformers import SentenceTransformer

MODEL_NAME = "intfloat/multilingual-e5-base"
MODEL_CACHE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "models")
OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "llama3.2:3b"
LLM_ENABLED = False


@st.cache_resource
def load_resources():
    index = faiss.read_index("data/faiss_index.bin")
    with open("data/bm25_index.pkl", "rb") as f:
        bm25 = pickle.load(f)
    with open("data/metadata.pkl", "rb") as f:
        metadata = pickle.load(f)
    model = SentenceTransformer(MODEL_NAME, cache_folder=MODEL_CACHE_DIR)
    return index, bm25, metadata, model


def check_ollama_status():
    if not LLM_ENABLED:
        return False
    try:
        resp = requests.get("http://localhost:11434/api/tags", timeout=3)
        return resp.status_code == 200
    except Exception:
        return False


def tokenize(text: str):
    return text.lower().split()


def hybrid_search_inference(query, index, bm25, metadata, model,
                            top_k=15, dense_weight=0.7, bm25_weight=0.3,
                            min_score=0.6, gap_ratio=0.0):
    query_emb = model.encode(["query: " + query], normalize_embeddings=True).astype("float32")

    dense_scores, dense_ids = index.search(query_emb, min(top_k * 3, index.ntotal))
    dense_scores = dense_scores[0]
    dense_ids = dense_ids[0]

    bm25_scores = bm25.get_scores(tokenize(query))
    combined = {}
    dense_max = dense_scores.max() if dense_scores.max() > 0 else 1.0
    bm25_max = bm25_scores.max() if bm25_scores.max() > 0 else 1.0

    for i, idx in enumerate(dense_ids):
        combined[idx] = dense_weight * (dense_scores[i] / dense_max)

    for idx in np.argsort(bm25_scores)[-(top_k * 3):]:
        b = bm25_weight * (bm25_scores[idx] / bm25_max)
        combined[idx] = combined.get(idx, 0) + b

    ranked = sorted(combined.items(), key=lambda x: x[1], reverse=True)

    if not ranked:
        return []

    top_score = ranked[0][1]
    cutoff = max(min_score, top_score * gap_ratio)

    results = []
    for idx, score in ranked:
        if score < cutoff:
            break
        results.append((metadata[idx], score))
        if len(results) >= top_k:
            break
    return results


def call_ollama(prompt: str) -> str | None:
    if not LLM_ENABLED:
        return None
    try:
        resp = requests.post(
            OLLAMA_URL,
            json={"model": OLLAMA_MODEL, "prompt": prompt, "stream": False},
            timeout=30,
        )
        resp.raise_for_status()
        return resp.json().get("response", "").strip()
    except Exception:
        return None


def make_prompt(query: str, match: dict, verdict: str, user_price: float,
                nds: int = 0, adjusted_limit: float = 0.0) -> str:
    mnn = match.get("МНН", "")
    trade = match.get("Торговое_наименование", "")
    forma = match.get("Лекарственная_форма", "")
    producer = match.get("производитель_чист", match.get("Производитель", ""))
    limit = match.get("Предельная_цена", "")
    qty = match.get("Количество", "")

    return (
        f"Ты помощник по проверке цен на лекарства в реестре ЖНВЛП Минздрава РФ.\n"
        f"Пользователь искал: {query}\n"
        f"Найден препарат: {mnn} ({trade})\n"
        f"Форма выпуска: {forma}\n"
        f"Количество: {qty}\n"
        f"Производитель: {producer}\n"
        f"Предельная цена по реестру (без НДС): {limit} руб.\n"
        f"НДС: {nds}%\n"
        f"Предельная цена с НДС: {adjusted_limit:.2f} руб.\n"
        f"Цена пользователя: {user_price} руб.\n"
        f"Вердикт: {verdict}\n\n"
        f"Дай краткий понятный ответ пользователю на русском языке (2–3 предложения). "
        f"Без приветствий и лишних слов."
    )


def fallback_text(match: dict, verdict: str, user_price: float,
                   nds: int = 0, adjusted_limit: float = 0.0) -> str:
    mnn = match.get("МНН", "—")
    trade = match.get("Торговое_наименование", "—")
    forma = match.get("Лекарственная_форма", "—")
    limit = match.get("Предельная_цена", "—")
    producer = match.get("производитель_чист", match.get("Производитель", "—"))
    return (
        f"**Препарат:** {mnn} ({trade})\n\n"
        f"**Форма выпуска:** {forma}\n\n"
        f"**Производитель:** {producer}\n\n"
        f"**Предельная цена по реестру:** {limit} руб. (без НДС)\n\n"
        f"**С учётом НДС {nds}%:** {adjusted_limit:.2f} руб.\n\n"
        f"**Ваша цена:** {user_price} руб.\n\n"
        f"**Вывод:** {verdict}"
    )


st.set_page_config(
    page_title="Фарм-контроль",
    page_icon="💊",
    layout="centered",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
    .block-container { padding-top: 2rem; }
    div[data-testid="stForm"] {
        border: 1px solid rgba(49, 51, 63, 0.2);
        border-radius: 0.75rem;
        padding: 1.5rem;
    }
    .status-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 500;
    }
    .status-online {
        background: rgba(0, 180, 0, 0.1);
        color: #00b400;
        border: 1px solid rgba(0, 180, 0, 0.25);
    }
    .status-offline {
        background: rgba(180, 0, 0, 0.1);
        color: #b40000;
        border: 1px solid rgba(180, 0, 0, 0.25);
    }
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.header("⚙️ Настройки поиска")

    st.subheader("Параметры гибридного поиска")

    bm25_weight = st.slider(
        "Вес BM25 (ключевые слова)",
        min_value=0.0, max_value=1.0, value=0.3, step=0.05,
        help="Доля поиска по ключевым словам (BM25). "
             "Плотный (семантический) поиск = 1 − это значение.",
    )
    dense_weight = 1.0 - bm25_weight
    st.caption(f"Семантический поиск: **{dense_weight:.2f}** · BM25: **{bm25_weight:.2f}**")

    st.divider()

    min_score = st.slider(
        "Минимальный порог релевантности",
        min_value=0.0, max_value=1.0, value=0.6, step=0.05,
        help="Результаты с комбинированным скором ниже этого значения отсекаются.",
    )

    gap_ratio = st.slider(
        "Коэффициент отсечения (gap ratio)",
        min_value=0.0, max_value=1.0, value=0.0, step=0.05,
        help="Отсекает результаты, чей скор ниже (лучший скор × gap ratio). "
             "При 0 — не влияет. При 0.8 — остаются только очень близкие к лучшему.",
    )

    top_k = st.slider(
        "Макс. результатов",
        min_value=1, max_value=30, value=15, step=1,
        help="Максимальное количество найденных записей в реестре.",
    )

    st.divider()
    st.subheader("Информация")

    llm_online = check_ollama_status()
    if LLM_ENABLED:
        if llm_online:
            st.markdown(
                f'<span class="status-badge status-online">● LLM подключена: {OLLAMA_MODEL}</span>',
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                f'<span class="status-badge status-offline">○ LLM недоступна ({OLLAMA_MODEL})</span>',
                unsafe_allow_html=True,
            )
            st.caption("Ответ будет сформирован без языковой модели.")
    else:
        st.markdown(
            '<span class="status-badge status-offline">○ Офлайн</span>',
            unsafe_allow_html=True,
        )

st.title("💊 Фарм-контроль")
st.caption("Проверка цен на лекарства по реестру ЖНВЛП Минздрава РФ")

with st.form("check_form"):
    query = st.text_input(
        "Информация о лекарстве",
        placeholder="Например: аспирин кардио 100мг таблетки",
    )
    col_price, col_nds = st.columns([2, 1])
    with col_price:
        price_input = st.text_input(
            "Цена (руб.)",
            placeholder="Например: 350",
        )
    with col_nds:
        nds = st.selectbox("НДС (%)", options=[0, 5, 10, 15, 20, 22, 25, 30], index=2)

    submitted = st.form_submit_button("Проверить цену", use_container_width=True)

if submitted:
    query = query.strip()
    price_input = price_input.strip()

    if not query:
        st.warning("Введите название лекарства.")
        st.stop()
    if not price_input:
        st.warning("Введите цену.")
        st.stop()

    try:
        user_price = float(re.sub(r'[^\d.,]', '', price_input).replace(',', '.'))
    except ValueError:
        st.error("Некорректный формат цены. Введите число, например: 350 или 120.50")
        st.stop()

    with st.spinner("Ищем в реестре…"):
        index, bm25, metadata, model = load_resources()
        results = hybrid_search_inference(
            query, index, bm25, metadata, model,
            top_k=top_k,
            dense_weight=dense_weight,
            bm25_weight=bm25_weight,
            min_score=min_score,
            gap_ratio=gap_ratio,
        )

    if not results:
        st.error("Извините, данного лекарства нет в реестре ЖНВЛП.")
        st.stop()

    match, score = results[0]
    limit_price = float(match["Предельная_цена"])
    adjusted_limit = limit_price * (1 + nds / 100)

    if user_price > adjusted_limit:
        pct = round((user_price - adjusted_limit) / adjusted_limit * 100)
        verdict = f"ПРЕВЫШЕНИЕ ЦЕНЫ на {pct}%"
        verdict_color = "error"
    else:
        pct = round((adjusted_limit - user_price) / adjusted_limit * 100)
        verdict = f"Цена в норме — ниже предельной на {pct}%"
        verdict_color = "success"

    st.divider()

    if verdict_color == "error":
        st.error(f"⚠️ {verdict}")
    else:
        st.success(f"✅ {verdict}")

    col_reg, col_user = st.columns(2)
    with col_reg:
        st.metric("Предельная цена (с НДС)", f"{adjusted_limit:.2f} ₽")
        st.caption(f"Без НДС: {limit_price:.2f} ₽ · НДС: {nds}%")
    with col_user:
        delta = user_price - adjusted_limit
        st.metric(
            "Ваша цена",
            f"{user_price:.2f} ₽",
            delta=f"{delta:+.2f} ₽",
            delta_color="inverse",
        )

    if LLM_ENABLED:
        with st.spinner("Формируем ответ…"):
            prompt = make_prompt(query, match, verdict, user_price, nds, adjusted_limit)
            llm_response = call_ollama(prompt)
    else:
        llm_response = None

    if llm_response:
        st.info(llm_response, icon="🤖")
    else:
        st.markdown(fallback_text(match, verdict, user_price, nds, adjusted_limit))

    st.divider()
    st.subheader("Найденные записи в реестре")

    table_data = []
    for meta, s in results:
        table_data.append({
            "Скор": round(s, 3),
            "МНН": meta.get("МНН", "—"),
            "Торговое наименование": meta.get("Торговое_наименование", "—"),
            "Форма выпуска": meta.get("форма_выпуска", "—"),
            "Дозировка": meta.get("дозировка", "—"),
            "Количество": meta.get("Количество", "—"),
            "Предельная цена (руб.)": meta.get("Предельная_цена", "—"),
            "Производитель": meta.get("производитель_чист", meta.get("Производитель", "—")),
            "Код АТХ": meta.get("Код_АТХ", "—"),
            "Номер РУ": meta.get("Номер_РУ", "—"),
            "Дата регистрации": meta.get("Дата_регистрации", "—"),
            "Дата вступления": meta.get("Дата_вступления", "—"),
            "Штрихкод": meta.get("Штрихкод", "—"),
        })

    df_results = pd.DataFrame(table_data)

    main_cols = ["Скор", "МНН", "Торговое наименование", "Форма выпуска",
                 "Дозировка", "Предельная цена (руб.)"]
    st.dataframe(
        df_results[main_cols],
        use_container_width=True,
        hide_index=True,
    )

    with st.expander("Показать все метаданные"):
        st.dataframe(df_results, use_container_width=True, hide_index=True)