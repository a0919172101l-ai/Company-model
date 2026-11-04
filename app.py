import json
import re
from pathlib import Path
from typing import List, Dict, Any

import numpy as np
import streamlit as st
from sentence_transformers import SentenceTransformer

# -----------------------------
# Configuration
# -----------------------------
APP_DIR = Path(__file__).parent
DATA_FILE = APP_DIR / "data" / "company_data.json"
MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
TOP_K = 4
MIN_SIMILARITY = 0.28  # Tune using the test questions in README.

st.set_page_config(
    page_title="Lyla | Company AI Assistant",
    page_icon="💡",
    layout="wide",
)

# -----------------------------
# Data loading and validation
# -----------------------------
def load_company_data() -> List[Dict[str, str]]:
    """Load company knowledge records from JSON. No Q&A pairs are stored in code."""
    if not DATA_FILE.exists():
        return []

    try:
        with DATA_FILE.open("r", encoding="utf-8") as f:
            raw = json.load(f)
    except (json.JSONDecodeError, OSError) as exc:
        st.error(f"Could not read company_data.json: {exc}")
        return []

    if not isinstance(raw, list):
        st.error("company_data.json must contain a JSON list of records.")
        return []

    records = []
    for item in raw:
        if not isinstance(item, dict):
            continue
        title = str(item.get("title", "")).strip()
        category = str(item.get("category", "General")).strip()
        content = str(item.get("content", "")).strip()
        source = str(item.get("source", "Company knowledge base")).strip()

        if title and content:
            records.append({
                "title": title,
                "category": category or "General",
                "content": content,
                "source": source or "Company knowledge base",
            })
    return records


# -----------------------------
# Local semantic model
# -----------------------------
@st.cache_resource(show_spinner="Loading Lyla's local language model...")
def load_model():
    # Downloads the open model on first run, then loads it locally.
    # This is NOT an AI API call.
    return SentenceTransformer(MODEL_NAME)


def split_into_sentences(text: str) -> List[str]:
    """Simple sentence splitter for evidence-based answer extraction."""
    pieces = re.split(r"(?<=[.!?])\s+|\n+", text.strip())
    return [p.strip() for p in pieces if p.strip()]


@st.cache_data(show_spinner=False)
def create_embeddings(texts: tuple, model_name: str) -> np.ndarray:
    # A tuple is used so Streamlit can cache this function.
    model = load_model()
    vectors = model.encode(
        list(texts),
        normalize_embeddings=True,
        convert_to_numpy=True,
        show_progress_bar=False,
    )
    return vectors.astype("float32")


def retrieve_relevant_records(
    question: str,
    records: List[Dict[str, str]],
    model,
) -> List[Dict[str, Any]]:
    """Retrieve company records by semantic similarity, not fixed question matching."""
    if not question.strip() or not records:
        return []

    record_texts = [
        f"Category: {r['category']}. Title: {r['title']}. Information: {r['content']}"
        for r in records
    ]

    record_vectors = model.encode(
        record_texts,
        normalize_embeddings=True,
        convert_to_numpy=True,
        show_progress_bar=False,
    )
    question_vector = model.encode(
        [question],
        normalize_embeddings=True,
        convert_to_numpy=True,
        show_progress_bar=False,
    )[0]

    # Normalized vectors make dot product equivalent to cosine similarity.
    scores = np.dot(record_vectors, question_vector)

    ranked_indices = np.argsort(scores)[::-1][:TOP_K]
    results = []
    for idx in ranked_indices:
        record = records[int(idx)]
        results.append({
            **record,
            "score": float(scores[int(idx)]),
        })
    return results


# -----------------------------
# Evidence-based response builder
# -----------------------------
def build_evidence_answer(results: List[Dict[str, Any]]) -> str:
    """
    Build a response only from retrieved source text.
    This is extractive retrieval, not free-form generative AI.
    """
    if not results:
        return "I couldn't find relevant information in the company knowledge base."

    # Split retrieved records into sentences and rank each sentence against
    # the user's question in the caller. This function is kept separate
    # to make the evidence-based response behavior clear.
    selected = []
    seen = set()

    for result in results:
        sentences = split_into_sentences(result["content"])
        for sentence in sentences:
            normalized = re.sub(r"\s+", " ", sentence).strip().lower()
            if normalized and normalized not in seen:
                selected.append((sentence, result))
                seen.add(normalized)

    if not selected:
        return "I found related records, but they do not contain a readable answer."

    # Keep only source sentences from the retrieved records.
    return "\n\n".join(sentence for sentence, _ in selected[:5])


def answer_question(question: str, records: List[Dict[str, str]], model):
    results = retrieve_relevant_records(question, records, model)

    if not results:
        return (
            "I couldn't find sufficient information in our company knowledge base. "
            "Please ask about information documented by the company.",
            [],
            False,
        )

    best_score = results[0]["score"]
    if best_score < MIN_SIMILARITY:
        return (
            "I couldn't find sufficient relevant information in our company "
            "knowledge base, so I don't want to guess.",
            results,
            False,
        )

    # Re-rank individual evidence sentences against the actual user question.
    candidate_sentences = []
    for record in results:
        for sentence in split_into_sentences(record["content"]):
            candidate_sentences.append((sentence, record))

    if not candidate_sentences:
        return (
            "I found related records, but they do not contain readable information.",
            results,
            False,
        )

    sentence_texts = [s for s, _ in candidate_sentences]
    sentence_vectors = model.encode(
        sentence_texts,
        normalize_embeddings=True,
        convert_to_numpy=True,
        show_progress_bar=False,
    )
    q_vector = model.encode(
        [question],
        normalize_embeddings=True,
        convert_to_numpy=True,
        show_progress_bar=False,
    )[0]
    sentence_scores = np.dot(sentence_vectors, q_vector)

    order = np.argsort(sentence_scores)[::-1]
    answer_lines = []
    used = set()

    for idx in order:
        score = float(sentence_scores[int(idx)])
        sentence, source_record = candidate_sentences[int(idx)]
        normalized = re.sub(r"\s+", " ", sentence).strip().lower()
        if score < MIN_SIMILARITY or normalized in used:
            continue
        answer_lines.append(sentence)
        used.add(normalized)
        if len(answer_lines) >= 4:
            break

    if not answer_lines:
        return (
            "I couldn't find sufficient relevant information in our company "
            "knowledge base, so I don't want to guess.",
            results,
            False,
        )

    answer = "Here is what I found in the company knowledge base:\n\n" + "\n\n".join(
        f"• {line}" for line in answer_lines
    )
    return answer, results, True


# -----------------------------
# User interface
# -----------------------------
st.title("💡 Lyla")
st.subheader("Company AI Assistant")
st.caption(
    "A local NLP-based assistant that searches the company's knowledge base. "
    "It does not use an external generative AI API."
)

with st.sidebar:
    st.header("About Lyla")
    st.write(
        "Lyla analyzes each question with a local sentence-embedding model, "
        "retrieves semantically related company information, and presents "
        "evidence from the knowledge base."
    )
    st.divider()
    st.write(f"**Knowledge records:** {len(load_company_data())}")
    st.write("**Model:** all-MiniLM-L6-v2")
    st.write("**Method:** Semantic retrieval + extractive answers")
    st.caption(
        "Note: The first launch downloads the model files. After that, "
        "the model can run locally where those files are available."
    )

records = load_company_data()

if not records:
    st.warning(
        "Your company knowledge base is empty. Add real company information "
        "to data/company_data.json before testing Lyla."
    )

model = load_model()

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if message.get("sources"):
            with st.expander("View retrieved company data"):
                for source in message["sources"]:
                    st.markdown(
                        f"**{source['title']}** · {source['category']}  \n"
                        f"{source['content']}  \n"
                        f"<small>Source: {source['source']} · "
                        f"Similarity: {source['score']:.3f}</small>",
                        unsafe_allow_html=True,
                    )

question = st.chat_input("Ask Lyla a question about our company...")

if question:
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        with st.spinner("Reading your question and searching company data..."):
            answer, retrieved, found = answer_question(question, records, model)
        st.markdown(answer)

        if retrieved:
            with st.expander("View retrieved company data"):
                for source in retrieved:
                    st.markdown(
                        f"**{source['title']}** · {source['category']}  \n"
                        f"{source['content']}  \n"
                        f"Source: {source['source']} · "
                        f"Similarity: {source['score']:.3f}"
                    )

    st.session_state.messages.append({
        "role": "assistant",
        "content": answer,
        "sources": retrieved,
    })

if st.button("Clear conversation"):
    st.session_state.messages = []
    st.rerun()
