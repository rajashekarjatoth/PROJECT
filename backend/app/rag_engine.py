import os
import re
import json
from pathlib import Path
from typing import List, Dict, Any, Tuple
import pypdf
import chromadb
from chromadb.config import Settings
from app.config import CHROMA_DIR, DOCS_DIR

# Global vector collection & storage
_chroma_client = None
_collection = None
_local_vector_index: List[Dict[str, Any]] = []


import hashlib
import numpy as np
from chromadb.api.types import Documents, EmbeddingFunction, Embeddings

class FastOfflineEmbeddingFunction(EmbeddingFunction):
    def __init__(self, dim: int = 128):
        self.dim = dim

    def __call__(self, input: Documents) -> Embeddings:
        embeddings = []
        for doc in input:
            vec = np.zeros(self.dim, dtype=np.float32)
            words = re.findall(r'\b[a-zA-Z0-9_]{2,}\b', doc.lower())
            for word in words:
                h = int(hashlib.md5(word.encode('utf-8')).hexdigest(), 16)
                idx = h % self.dim
                sign = 1.0 if ((h >> 8) & 1) else -1.0
                vec[idx] += sign
            norm = np.linalg.norm(vec)
            if norm > 0:
                vec = vec / norm
            embeddings.append(vec.tolist())
        return embeddings

_fast_embedder = FastOfflineEmbeddingFunction()

def get_chroma_collection():
    global _chroma_client, _collection
    if _collection is None:
        try:
            _chroma_client = chromadb.PersistentClient(path=str(CHROMA_DIR))
            _collection = _chroma_client.get_or_create_collection(
                name="interview_knowledge_base",
                embedding_function=_fast_embedder,
                metadata={"hnsw:space": "cosine"}
            )
        except Exception as e:
            print(f"[RAG Engine] Warning: ChromaDB native initialization fallback: {e}")
            _collection = None
    return _collection


def extract_text_from_pdf(filepath: str) -> str:
    full_text = []
    try:
        reader = pypdf.PdfReader(filepath)
        for page_num, page in enumerate(reader.pages):
            text = page.extract_text()
            if text:
                full_text.append(f"--- Page {page_num + 1} ---\n" + text)
    except Exception as e:
        print(f"[RAG Engine] PDF Extraction Error: {e}")
    return "\n\n".join(full_text)


def extract_text_from_file(filepath: str) -> str:
    path = Path(filepath)
    ext = path.suffix.lower()
    if ext == ".pdf":
        return extract_text_from_pdf(filepath)
    elif ext in [".txt", ".md", ".json", ".py", ".sql"]:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()
    else:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()


def chunk_text(text: str, chunk_size: int = 500, chunk_overlap: int = 80) -> List[str]:
    # Clean text
    text = re.sub(r'\r\n', '\n', text)
    paragraphs = text.split('\n\n')
    chunks = []
    current_chunk = []
    current_length = 0

    for para in paragraphs:
        para = para.strip()
        if not para:
            continue
        words = para.split()
        if current_length + len(words) <= chunk_size:
            current_chunk.extend(words)
            current_length += len(words)
        else:
            if current_chunk:
                chunks.append(" ".join(current_chunk))
            # Keep overlap
            overlap_words = current_chunk[-chunk_overlap:] if len(current_chunk) > chunk_overlap else current_chunk
            current_chunk = overlap_words + words
            current_length = len(current_chunk)

    if current_chunk:
        chunks.append(" ".join(current_chunk))

    # Fallback if text has few newlines
    if not chunks and text.strip():
        words = text.split()
        for i in range(0, len(words), chunk_size - chunk_overlap):
            chunks.append(" ".join(words[i:i + chunk_size]))

    return chunks


def simple_semantic_similarity(query: str, text: str) -> float:
    """
    Lightweight, deterministic lexical-semantic matcher
    Combines exact match, token overlap, and technical term density.
    """
    query_tokens = set(re.findall(r'\b[a-zA-Z0-9_]{3,}\b', query.lower()))
    text_tokens = set(re.findall(r'\b[a-zA-Z0-9_]{3,}\b', text.lower()))

    if not query_tokens or not text_tokens:
        return 0.0

    intersection = query_tokens.intersection(text_tokens)
    jaccard = len(intersection) / len(query_tokens.union(text_tokens))
    query_coverage = len(intersection) / len(query_tokens)

    # Boost score when query terms appear in sequence or key technical phrases match
    phrase_boost = 0.2 if query.lower() in text.lower() else 0.0
    score = (0.7 * query_coverage) + (0.3 * jaccard) + phrase_boost
    return min(1.0, round(score, 4))


def ingest_document(doc_id: int, title: str, filepath: str, filename: str) -> int:
    raw_text = extract_text_from_file(filepath)
    if not raw_text.strip():
        return 0

    chunks = chunk_text(raw_text)
    collection = get_chroma_collection()

    ids = []
    documents = []
    metadatas = []

    for idx, chunk in enumerate(chunks):
        chunk_id = f"doc_{doc_id}_chunk_{idx}"
        metadata = {
            "doc_id": doc_id,
            "title": title,
            "filename": filename,
            "chunk_index": idx,
            "total_chunks": len(chunks)
        }
        ids.append(chunk_id)
        documents.append(chunk)
        metadatas.append(metadata)

        # Mirror in fallback index
        _local_vector_index.append({
            "id": chunk_id,
            "text": chunk,
            "metadata": metadata
        })

    if collection:
        try:
            collection.add(
                ids=ids,
                documents=documents,
                metadatas=metadatas
            )
        except Exception as e:
            print(f"[RAG Engine] ChromaDB add error: {e}")

    return len(chunks)


def search_knowledge_base(query: str, top_k: int = 4) -> List[Dict[str, Any]]:
    collection = get_chroma_collection()
    results = []

    if collection and collection.count() > 0:
        try:
            chroma_results = collection.query(
                query_texts=[query],
                n_results=min(top_k, collection.count())
            )
            if chroma_results and chroma_results.get("documents"):
                docs = chroma_results["documents"][0]
                metas = chroma_results["metadatas"][0]
                distances = chroma_results.get("distances", [[]])[0]

                for idx, doc in enumerate(docs):
                    meta = metas[idx]
                    distance = distances[idx] if idx < len(distances) else 0.5
                    # Convert cosine distance to similarity score
                    sim_score = round(max(0.0, 1.0 - (distance if distance is not None else 0.5)), 3)
                    results.append({
                        "chunk_id": f"doc_{meta.get('doc_id')}_{meta.get('chunk_index')}",
                        "title": meta.get("title", "Document"),
                        "filename": meta.get("filename", "unknown"),
                        "chunk_index": meta.get("chunk_index", 0),
                        "similarity_score": sim_score,
                        "text": doc
                    })
        except Exception as e:
            print(f"[RAG Engine] Chroma query exception: {e}")

    # Fallback to local semantic vector index if chroma returns empty or fails
    if not results and _local_vector_index:
        scored = []
        for item in _local_vector_index:
            score = simple_semantic_similarity(query, item["text"])
            if score > 0.05:
                scored.append((score, item))
        scored.sort(key=lambda x: x[0], reverse=True)

        for score, item in scored[:top_k]:
            results.append({
                "chunk_id": item["id"],
                "title": item["metadata"]["title"],
                "filename": item["metadata"]["filename"],
                "chunk_index": item["metadata"]["chunk_index"],
                "similarity_score": score,
                "text": item["text"]
            })

    return results


def seed_default_knowledge_base():
    """Seeds standard curated interview preparation notes and technical handbooks"""
    default_docs = [
        {
            "filename": "python_concurrency_and_gil.md",
            "title": "Python Architecture, Concurrency & GIL Deep Dive",
            "content": """# Python Internals, Concurrency, and the GIL

## The Global Interpreter Lock (GIL)
The CPython interpreter uses a mutex called the Global Interpreter Lock (GIL) to synchronize execution of threads.
Because CPython's memory management is not thread-safe (reference counting `PyObject`), the GIL prevents multiple native threads from executing Python bytecode simultaneously.

### Key Points for Technical Interviews:
1. **CPU-bound vs I/O-bound**:
   - For CPU-bound tasks (matrix multiplication, image processing), multithreading in Python does NOT achieve true multi-core speedup because threads fight for the GIL. Use `multiprocessing` or `concurrent.futures.ProcessPoolExecutor` instead.
   - For I/O-bound tasks (network requests, database queries, file reads), multithreading (`threading` or `asyncio`) provides massive speedups because threads release the GIL while waiting on system calls.
2. **AsyncIO**:
   - Uses single-threaded cooperative multitasking with an Event Loop.
   - Coroutines defined with `async def` and `await` yield control back to the loop when awaiting I/O.
3. **Generators & Iterators**:
   - Generators yield values one at a time using `yield`, keeping O(1) auxiliary space rather than allocating full lists in memory."""
        },
        {
            "filename": "sql_indexing_and_optimization.md",
            "title": "Relational Databases, ACID, and SQL Query Optimization",
            "content": """# SQL & Relational Database Engineering

## ACID Properties Explained:
- **Atomicity**: Entire transaction succeeds or rolls back completely (All or Nothing).
- **Consistency**: The database moves from one valid state to another, respecting all constraints, foreign keys, and triggers.
- **Isolation**: Concurrent transactions execute as if sequential. Isolation levels: Read Uncommitted, Read Committed, Repeatable Read, Serializable.
- **Durability**: Once committed, changes survive power outages or server crashes via Write-Ahead Logging (WAL).

## Indexing Fundamentals (B-Trees):
- Relational databases (PostgreSQL, MySQL InnoDB) use B+ Tree indexes for fast logarithmic search O(log N).
- **Composite Indexes**: The "Leftmost Prefix Rule" dictates that an index on (A, B, C) can be used for queries filtering on (A), (A, B), or (A, B, C), but NOT on (B, C) alone.
- Avoid applying functions on indexed columns in `WHERE` clauses (e.g., `WHERE YEAR(created_at) = 2024` prevents index lookup; use range scan instead: `WHERE created_at >= '2024-01-01' AND created_at < '2025-01-01'`)."""
        },
        {
            "filename": "machine_learning_and_rag_systems.md",
            "title": "Machine Learning Foundations, Transformers & RAG Architecture",
            "content": """# Machine Learning & RAG Systems Architecture

## The RAG (Retrieval-Augmented Generation) Paradigm:
1. **Document Preprocessing**: Chunking raw text into coherent semantic windows (typically 250-500 tokens with 10-20% overlap).
2. **Dense Vector Embeddings**: Transforming text chunks into high-dimensional latent vectors using models like `sentence-transformers` or text-embedding-3.
3. **Vector Similarity Search**: Utilizing HNSW (Hierarchical Navigable Small World) or Inverted File Flat (IVFFlat) indexes with Cosine Similarity or Dot Product to retrieve Top-K closest passages.
4. **Context Injection**: Constructing a structured system prompt combining retrieved passages, user persona, and user question, preventing hallucinations.

## Bias-Variance Tradeoff:
- **High Bias (Underfitting)**: Model is overly simplistic, fails to capture underlying patterns. Remedy: Increase model complexity, engineer informative features, reduce regularization.
- **High Variance (Overfitting)**: Model memorizes training noise, fails to generalize to validation data. Remedy: L1/L2 regularization, dropout, cross-validation, data augmentation."""
        },
        {
            "filename": "behavioral_hr_star_method.md",
            "title": "HR & Behavioral Interview Mastery (STAR Method)",
            "content": """# The STAR Framework for Behavioral Interviews

## STAR Breakdown:
- **S - Situation**: Set the scene. Give concise context (company, project scale, timeline, stakeholders).
- **T - Task**: Clearly describe your specific responsibility or the challenge you faced.
- **A - Action**: Detail the specific steps YOU took (not just the team). Highlight leadership, technical problem-solving, collaboration, and data-driven decisions.
- **R - Result**: Quantify the impact! Mention latency reduced (e.g. 40%), revenue increased, downtime averted, or lessons learned.

## Common Behavioral Themes:
1. **Conflict Resolution**: How you handled technical disagreements with senior engineers or product managers.
2. **Failure / Mistakes**: A production bug or missed deadline, what root cause analysis (RCA) you performed, and preventative guardrails built.
3. **Mentorship & Ownership**: How you helped onboard junior developers or championed code quality initiatives."""
        }
    ]

    for item in default_docs:
        filepath = DOCS_DIR / item["filename"]
        if not filepath.exists():
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(item["content"])
        # Check if already indexed
        ingest_document(
            doc_id=abs(hash(item["filename"])) % 10000,
            title=item["title"],
            filepath=str(filepath),
            filename=item["filename"]
        )
