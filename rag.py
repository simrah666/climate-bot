"""RAG logic for the Climate Information Bot, in one file so Streamlit can run it directly.

No separate backend, no torch and no ChromaDB: guides are embedded with a small
ONNX model (fastembed) at startup and searched with numpy. This keeps memory low
enough for free hosting.
"""
import os
import re
from pathlib import Path

import numpy as np
import streamlit as st
from fastembed import TextEmbedding
from groq import Groq

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data" if (BASE_DIR / "data").is_dir() else BASE_DIR

EMBEDDING_MODEL = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
GROQ_MODEL = "openai/gpt-oss-120b"  # use the model name that works for you
TOP_K = 4

SOURCE_LABELS = {
    "floods_pk.md": "Flood Safety Guide (Pakistan)",
    "earthquake_pk.md": "Earthquake Safety Guide (Pakistan)",
    "heatwave_pk.md": "Heatwave Safety Guide (Pakistan)",
    "emergency_kit.md": "Emergency Kit Guide (Pakistan)",
    "glaciers_glof_pk.md": "Glacier & GLOF Safety Guide (Chitral)",
}


def friendly_source_name(filename: str) -> str:
    return SOURCE_LABELS.get(filename, filename.replace("_", " ").replace(".md", "").title())


def split_chunks(text: str, max_len: int = 1200):
    """Split at markdown headings; break very long sections into smaller pieces."""
    pieces = []
    for part in re.split(r"\n(?=#{1,3} )", text):
        part = part.strip()
        if len(part) <= max_len:
            pieces.append(part)
            continue
        current = ""
        for para in re.split(r"\n\s*\n", part):
            if current and len(current) + len(para) > max_len:
                pieces.append(current.strip())
                current = ""
            current += para + "\n\n"
        pieces.append(current.strip())
    return [p for p in pieces if len(p) > 40]


@st.cache_resource(show_spinner="Loading safety guides...")
def load_index():
    model = TextEmbedding(model_name=EMBEDDING_MODEL)
    chunks, sources = [], []
    for path in sorted(DATA_DIR.glob("*.md")):
        for chunk in split_chunks(path.read_text(encoding="utf-8")):
            chunks.append(chunk)
            sources.append(path.name)
    vectors = np.array(list(model.embed(chunks)), dtype="float32")
    vectors /= np.linalg.norm(vectors, axis=1, keepdims=True)
    return model, chunks, sources, vectors


def retrieve(query: str):
    model, chunks, sources, vectors = load_index()
    q = np.array(list(model.embed([query])), dtype="float32")[0]
    q /= np.linalg.norm(q)
    scores = vectors @ q
    top = np.argsort(scores)[::-1][:TOP_K]
    return [(chunks[i], sources[i]) for i in top]


def get_groq_key():
    key = os.getenv("GROQ_API_KEY")
    if key:
        return key
    try:
        return st.secrets["GROQ_API_KEY"]
    except Exception:
        return None


def build_prompts(query: str, location: str, context_items):
    context_text = "\n\n".join(doc for doc, _ in context_items)

    system_prompt = f"""
You are a helpful assistant for climate and disaster preparedness, with a focus on
Chitral, Khyber Pakhtunkhwa. When relevant, mention hazards such as river flooding, glacier-lake outburst floods (GLOFs), landslides, cold waves, and heatwaves.

Use the following retrieved context to answer the user's question about {location}.
If the context does not contain enough detail, give general but practical preparedness
advice and clearly tell the user to follow local authorities (district administration,
PDMA, PMD, Rescue 1122).
Reply in the same language as the user's question (English or Urdu).
Keep the answer concise, under 250 words.
Only state specific numbers or measurements (distances, amounts, times) if they appear in the retrieved context.

Retrieved context:
{context_text}
"""
    user_prompt = f"""
Question: {query}

Answer in clear, simple language. If useful, structure your answer with short bullet points.
If you mention specific actions, make them practical and easy to follow.
"""
    return system_prompt, user_prompt


def answer_question(query: str, location: str = "Chitral, Khyber Pakhtunkhwa"):
    """Returns {"answer": str, "sources": [labels]}, the same shape the old backend returned."""
    context_items = retrieve(query)
    if not context_items:
        return {
            "answer": (
                "I don't have confirmed information on this topic in the reference material. "
                "Please check official sources such as the district administration, PDMA, "
                "or the Rescue 1122 hotline."
            ),
            "sources": [],
        }

    system_prompt, user_prompt = build_prompts(query, location, context_items)

    try:
        client = Groq(api_key=get_groq_key())
        completion = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.3,
            max_tokens=1200,
        )
        answer = completion.choices[0].message.content
    except Exception as error:
        print(f"LLM error: {error}")
        answer = (
            "Sorry, I could not generate an answer right now. In an emergency, contact "
            "Rescue 1122 and follow notices from the district administration, PDMA, and PMD."
        )

    sources = list(dict.fromkeys(friendly_source_name(src) for _, src in context_items))
    return {"answer": answer, "sources": sources}
