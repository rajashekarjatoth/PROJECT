import re
from typing import Dict, List, Any, Tuple, Optional
from app.rag_engine import search_knowledge_base

AMBIGUOUS_PATTERNS = [
    (r"^(what is best|which is better|which one should i use|which is best)\??$",
     "To help you evaluate that effectively, could you specify your target workload, latency requirements, and team constraints? Different systems excel under different trade-offs!"),
    (r"^(how do i fix (my|the) (bug|error|code))\??$",
     "I'd be glad to help troubleshoot! Could you share the specific error message, stack trace, and the relevant code snippet?"),
    (r"^(tell me about (system design|architecture|databases|coding))\??$",
     "That is a broad and exciting topic! Are you focusing on relational vs NoSQL storage, high-throughput streaming, caching strategies, or an upcoming interview problem?"),
    (r"^(how to prepare|interview prep)\??$",
     "Let's create a targeted prep plan for you! Which role (Backend, AI/ML, Full-stack) and what interview stage (Coding, System Design, Behavioral) are you targeting?")
]


def detect_ambiguity(message: str) -> Tuple[bool, Optional[str]]:
    cleaned = message.strip().lower()
    for pattern, clarification in AMBIGUOUS_PATTERNS:
        if re.search(pattern, cleaned):
            return True, clarification
    
    # Generic short query check
    if len(cleaned.split()) <= 2 and not any(cleaned.startswith(k) for k in ["hi", "hello", "hey", "help", "quit", "exit"]):
        return True, f"You asked about '{message.strip()}'. Would you like a high-level conceptual overview, practical code examples, or common technical interview questions on this topic?"

    return False, None


def generate_mentor_reply(
    message: str,
    mode: str = "mentor",
    level: str = "intermediate",
    use_rag: bool = True
) -> Dict[str, Any]:
    # Check ambiguity first
    is_ambiguous, clarification = detect_ambiguity(message)
    if is_ambiguous:
        return {
            "reply": f"🤔 **Mentor Clarification**\n\n{clarification}",
            "is_ambiguous": True,
            "clarification_question": clarification,
            "level": level,
            "mode": mode,
            "rag_sources": []
        }

    rag_sources = []
    rag_context_text = ""
    if use_rag:
        retrieved = search_knowledge_base(message, top_k=3)
        if retrieved:
            rag_sources = retrieved
            rag_context_text = "\n\n".join([f"[{r['title']} - Chunk {r['chunk_index']}]: {r['text'][:300]}..." for r in retrieved])

    response_text = ""

    # Mentor Persona vs Direct Persona
    if mode == "mentor":
        greeting = "👨‍🏫 **Technical Mentor Perspective**\n\n"
        if level == "beginner":
            tone = "Let's break this down step-by-step using an intuitive analogy:\n\n"
        elif level == "advanced":
            tone = "Let's analyze this from an architectural and systems-level perspective, examining trade-offs and runtime characteristics:\n\n"
        else:
            tone = "Here is how to approach this systematically as an engineer:\n\n"
        
        body = generate_structured_explanation(message, level, rag_context_text)
        socratic_prompt = "\n\n💡 **Checkpoint for You**: How would you handle this if scale grew by 100x, or what potential edge case would you test first?"
        response_text = f"{greeting}{tone}{body}{socratic_prompt}"
    else:
        # Direct Mode
        header = f"📌 **Technical Reference Guide** ({level.capitalize()} Level)\n\n"
        body = generate_structured_explanation(message, level, rag_context_text)
        response_text = f"{header}{body}"

    # Append RAG citations if available
    if rag_sources:
        rag_badge = "\n\n---\n📚 **Retrieved Knowledge Citations** (RAG Grounding):\n"
        for s in rag_sources:
            rag_badge += f"- *{s['title']}* (Relevance: {int(s['similarity_score'] * 100)}%) — `{s['filename']}`\n"
        response_text += rag_badge

    return {
        "reply": response_text,
        "is_ambiguous": False,
        "clarification_question": None,
        "level": level,
        "mode": mode,
        "rag_sources": rag_sources
    }


def generate_structured_explanation(query: str, level: str, rag_context: str = "") -> str:
    lower_q = query.lower()

    if any(k in lower_q for k in ["gil", "global interpreter lock", "concurrency", "thread"]):
        if level == "beginner":
            return (
                "**1. What is the GIL?**\n"
                "Imagine a busy kitchen with multiple chefs (threads), but only **one chef's knife (the GIL)**. Even though multiple chefs are ready to cook, only one chef can hold the knife and prepare dishes at any split second.\n\n"
                "**2. Why does Python have it?**\n"
                "Python's default interpreter (CPython) uses reference counting to clean up memory. The GIL prevents race conditions where two threads try to modify an object's reference counter simultaneously.\n\n"
                "**3. Practical Rule of Thumb:**\n"
                "- **I/O-Bound** (Downloading web pages, reading files): Threads or `asyncio` work great because threads release the lock while waiting.\n"
                "- **CPU-Bound** (Image resizing, number crunching): Use `multiprocessing` to spawn separate processes with their own memory spaces."
            )
        elif level == "advanced":
            return (
                "**1. CPython GIL Internals & PyObject Reference Counting**\n"
                "At the C level, CPython uses `PyMutex` and reference counts (`ob_refcnt`). The GIL guarantees thread safety across atomic bytecode dispatches without requiring fine-grained locks across all hash tables and memory allocations.\n\n"
                "**2. Performance Profiling & Syscall Behavior**\n"
                "- When a thread executes I/O (e.g. `socket.recv`, file read), CPython invokes `Py_BEGIN_ALLOW_THREADS`, yielding the GIL to other threads.\n"
                "- On multi-core processors, thread contention on CPU-bound workloads causes severe cache invalidation and kernel scheduling latency (the 'convoy effect').\n\n"
                "**3. Modern Workarounds & PEP 703**\n"
                "- **PEP 703 (Free-threaded Python 3.13+)**: Introduces biased reference counting, immortal objects, and mimalloc to make GIL optional.\n"
                "- For production pipelines: use process pools (`ProcessPoolExecutor`), shared memory buffers (`multiprocessing.shared_memory`), or offload compute to C/Rust bindings releasing the GIL (`nogil`)."
            )
        else:
            return (
                "**1. Core Mechanism**\n"
                "The Global Interpreter Lock (GIL) is a mutex in CPython that ensures only one native OS thread executes Python bytecode at a time.\n\n"
                "**2. Impact on Concurrency**\n"
                "- **CPU-bound tasks**: Multithreading does not provide performance gains on multi-core systems; use the `multiprocessing` module instead.\n"
                "- **I/O-bound tasks**: Multithreading or `asyncio` effectively boosts throughput because threads yield the lock during network and disk wait states.\n\n"
                "**3. Key Interview Takeaways**\n"
                "- Distinguish between CPython (has GIL) vs Jython/IronPython (no GIL).\n"
                "- Mention `concurrent.futures.ProcessPoolExecutor` for parallelizing CPU tasks."
            )

    if any(k in lower_q for k in ["rag", "retrieval", "vector", "embedding"]):
        return (
            "**1. The RAG Workflow Breakdown**\n"
            "Retrieval-Augmented Generation bridges the gap between static LLM knowledge and dynamic enterprise documents:\n"
            "- **Step 1: Document Chunking**: Raw PDFs/documents are split into overlapping token chunks.\n"
            "- **Step 2: Vector Embeddings**: Mathematical representations generated via embedding models capture semantic meaning.\n"
            "- **Step 3: Vector DB Indexing**: Vectors are stored in indexes like ChromaDB or FAISS for sub-millisecond similarity search.\n"
            "- **Step 4: Prompt Augmentation**: Top-K retrieved passages are formatted into a context-enriched prompt for the LLM.\n\n"
            "**2. Why Mentors Champion RAG**\n"
            "- Zero hallucination on private data.\n"
            "- Avoids expensive model fine-tuning.\n"
            "- Provides auditable source citations."
        )

    if any(k in lower_q for k in ["index", "sql", "acid", "database"]):
        return (
            "**1. Relational Database Architecture**\n"
            "Databases organize data for rapid retrieval using structured indexing and transaction guarantees:\n"
            "- **B+ Tree Indexes**: Keep keys sorted in internal nodes while actual data rows (or pointers) live in linked leaf nodes, facilitating O(log N) lookup and sequential range scans.\n"
            "- **Clustered vs Non-Clustered**: Clustered index physically sorts the table; non-clustered creates an auxiliary lookup structure.\n\n"
            "**2. The ACID Guarantees**\n"
            "- **A**: All or nothing transaction execution.\n"
            "- **C**: Referential integrity and constraint adherence.\n"
            "- **I**: Concurrent transaction isolation (e.g. Read Committed, Serializable).\n"
            "- **D**: Write-Ahead Logging (WAL) guarantees persistence across system failures."
        )

    # General structured technical synthesis
    return (
        f"**1. Conceptual Overview**\n"
        f"When approaching '{query}', modern engineering practices emphasize clean separation of concerns, defensive programming, and scalable architectural boundaries.\n\n"
        f"**2. Key Technical Considerations ({level.capitalize()} Level)**\n"
        f"- **Reliability & Idempotency**: Ensure operations can be repeated safely without unexpected side effects.\n"
        f"- **Resource Management**: Monitor memory lifecycle, socket connections, and concurrency limits.\n"
        f"- **Verification & Observability**: Add structured logging, unit test suites, and benchmark execution paths.\n\n"
        f"**3. Recommended Next Steps**\n"
        f"Would you like to explore an interactive coding exercise, run an interview simulation on this topic, or inspect technical reference documents from the vector database?"
    )
