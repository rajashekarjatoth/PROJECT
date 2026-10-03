import random
import re
from typing import Dict, List, Any, Optional

QUESTION_BANK: Dict[str, List[Dict[str, Any]]] = {
    "Python": [
        {
            "id": "py_1",
            "domain": "Python",
            "difficulty": "intermediate",
            "interview_type": "technical",
            "question": "Explain how Python manages memory. How does reference counting work with the generational garbage collector, and how are cyclical references resolved?",
            "hints": [
                "Think about how Python tracks active variables using `ob_refcnt` in CPython.",
                "Reference counting alone cannot free objects that point to each other (A -> B and B -> A). What secondary mechanism detects cyclic graphs?",
                "Python divides objects into 3 generations (Gen 0, Gen 1, Gen 2) based on survival across collection cycles using the `gc` module."
            ],
            "rubric_keywords": ["reference counting", "garbage collection", "cyclic", "generations", "cpython", "gc", "deallocation", "threshold"],
            "ideal_concepts": "CPython uses reference counting as its primary memory management mechanism. When refcount hits zero, deallocation is immediate. To handle circular references, Python employs a cyclical garbage collector dividing surviving objects into Generation 0, 1, and 2 with frequency thresholds.",
            "follow_up": "How does using `__del__` methods historically complicate Python's cycle detector, and what changes were introduced in PEP 442?"
        },
        {
            "id": "py_2",
            "domain": "Python",
            "difficulty": "advanced",
            "interview_type": "technical",
            "question": "What is the Global Interpreter Lock (GIL) in CPython? How does it affect CPU-bound vs I/O-bound concurrency, and what are the workarounds?",
            "hints": [
                "The GIL is a mutex designed to make CPython's reference counting thread-safe.",
                "Consider whether multiple native threads can execute Python bytecode in parallel on multiple cores.",
                "For CPU-bound tasks, what module bypasses the GIL by creating independent processes with their own memory spaces?"
            ],
            "rubric_keywords": ["gil", "global interpreter lock", "cpython", "cpu-bound", "i/o-bound", "multiprocessing", "threading", "asyncio", "mutex"],
            "ideal_concepts": "The GIL is a mutual exclusion lock preventing multiple threads from executing Python bytecodes at once. CPU-bound tasks suffer performance bottlenecks in multithreading; developers use multiprocessing, PyPy/nogil, or C-extensions releasing the GIL. I/O-bound tasks release the GIL during syscalls.",
            "follow_up": "Under what exact conditions does a Python thread release the GIL during system calls or long-running C extensions?"
        },
        {
            "id": "py_3",
            "domain": "Python",
            "difficulty": "beginner",
            "interview_type": "technical",
            "question": "What is the difference between a list and a tuple in Python? When would you prefer one over the other for performance and safety?",
            "hints": [
                "Think about mutability: can elements be altered after creation?",
                "Consider hashability: can one of them be used as a dictionary key or set element?",
                "Tuples have smaller memory overhead and fixed allocation compared to dynamic list over-allocation."
            ],
            "rubric_keywords": ["mutable", "immutable", "tuple", "list", "hashable", "dictionary key", "memory", "performance"],
            "ideal_concepts": "Lists are mutable, dynamic arrays; tuples are immutable fixed sequences. Tuples are hashable and can serve as dictionary keys. Tuples also have lower memory overhead and execution speed due to preallocation.",
            "follow_up": "If a tuple contains a mutable object like a list `t = ([1, 2], 3)`, is `t` still hashable? Why or why not?"
        }
    ],
    "SQL": [
        {
            "id": "sql_1",
            "domain": "SQL",
            "difficulty": "intermediate",
            "interview_type": "sql",
            "question": "Explain the difference between WHERE and HAVING clauses. Write a sample query illustrating when HAVING is mandatory.",
            "hints": [
                "Think about the query execution order: does filtering happen before or after aggregation?",
                "Can you use aggregate functions like `COUNT()` or `AVG()` inside a `WHERE` clause?",
                "HAVING filters groups produced by `GROUP BY`."
            ],
            "rubric_keywords": ["where", "having", "group by", "aggregation", "filter", "count", "sum", "execution order"],
            "ideal_concepts": "WHERE filters rows before any group-by aggregation occurs and cannot evaluate aggregate functions. HAVING filters aggregated group results after GROUP BY evaluation.",
            "follow_up": "What is the internal SQL execution pipeline order from FROM, WHERE, GROUP BY, HAVING, SELECT, to ORDER BY?"
        },
        {
            "id": "sql_2",
            "domain": "SQL",
            "difficulty": "advanced",
            "interview_type": "sql",
            "question": "What is the difference between Clustered and Non-Clustered Indexes? How does a B+ Tree index accelerate range queries?",
            "hints": [
                "How many clustered indexes can a table have? Think about physical row ordering on disk.",
                "Non-clustered indexes contain pointers to row locators or primary keys.",
                "In a B+ Tree, leaf nodes form a doubly linked list. How does that help `BETWEEN` or inequality comparisons?"
            ],
            "rubric_keywords": ["clustered index", "non-clustered index", "b+ tree", "leaf nodes", "physical order", "pointers", "range scan", "primary key"],
            "ideal_concepts": "A clustered index physically sorts table rows on disk, allowing only one per table. Non-clustered indexes create separate lookup structures with pointers to rows. B+ Trees keep data only in linked leaf nodes, enabling rapid sequential scans for range queries.",
            "follow_up": "What is an 'Index Seek' versus an 'Index Scan', and when does an optimizer choose to scan the entire index?"
        }
    ],
    "Machine Learning": [
        {
            "id": "ml_1",
            "domain": "Machine Learning",
            "difficulty": "intermediate",
            "interview_type": "aiml",
            "question": "Explain the Bias-Variance tradeoff. What practical techniques do you use to diagnose and mitigate high variance?",
            "hints": [
                "Bias is underfitting; Variance is overfitting.",
                "High variance means the model performs well on training data but poorly on validation/test data.",
                "Techniques: Regularization (L1/L2), Dropout, Data Augmentation, Cross-Validation, Ensembling."
            ],
            "rubric_keywords": ["bias", "variance", "tradeoff", "overfitting", "underfitting", "regularization", "l1", "l2", "cross-validation", "generalization"],
            "ideal_concepts": "Bias measures error from erroneous assumptions (underfitting). Variance measures sensitivity to small fluctuations in training data (overfitting). High variance is mitigated via L1/L2 regularization, dropout, pruning, early stopping, and cross-validation.",
            "follow_up": "How does Ridge regression (L2) differ mathematically from Lasso regression (L1) in terms of weight shrinkage and feature sparsity?"
        },
        {
            "id": "ml_2",
            "domain": "Machine Learning",
            "difficulty": "advanced",
            "interview_type": "aiml",
            "question": "How does Self-Attention work in the Transformer architecture? Explain Query, Key, and Value vectors and the scaled dot-product formula.",
            "hints": [
                "Each token projection yields Q (what I'm looking for), K (what I contain), and V (my content).",
                "The attention weight is computed as `Softmax(Q * K^T / sqrt(d_k))`.",
                "Why do we divide by `sqrt(d_k)`? What happens to softmax gradients for large dot products?"
            ],
            "rubric_keywords": ["self-attention", "query", "key", "value", "scaled dot-product", "softmax", "dimension", "gradients", "transformer"],
            "ideal_concepts": "Self-attention computes dynamic contextual representations. Input embeddings are projected into Query, Key, and Value matrices. Scaled dot-product `Softmax(QK^T / sqrt(d_k))V` normalizes attention across sequence tokens, where `sqrt(d_k)` prevents vanishing gradients in the softmax tail.",
            "follow_up": "Why is multi-head attention superior to a single wide attention head?"
        }
    ],
    "AI": [
        {
            "id": "ai_1",
            "domain": "AI",
            "difficulty": "intermediate",
            "interview_type": "aiml",
            "question": "What is Retrieval-Augmented Generation (RAG)? How does combining dense vector retrieval with LLMs mitigate hallucinations and context limitations?",
            "hints": [
                "RAG connects LLMs to external, up-to-date, or private proprietary knowledge bases without fine-tuning.",
                "Steps: Ingestion, Chunking, Embedding, Vector Search, Prompt Augmentation, Generation.",
                "Grounding answers with citations prevents LLM parametric memory hallucination."
            ],
            "rubric_keywords": ["rag", "retrieval-augmented generation", "vector search", "embeddings", "hallucination", "context window", "grounding", "knowledge base"],
            "ideal_concepts": "RAG enhances generative models by fetching relevant context from vector databases (dense vector search) and injecting it into the prompt. This anchors the LLM output in factual enterprise data, eliminating stale model cutoffs and reducing hallucination.",
            "follow_up": "What strategies (e.g., chunk overlap, parent document retrieval, re-ranking) address the loss of semantic continuity during chunking?"
        }
    ],
    "Java": [
        {
            "id": "java_1",
            "domain": "Java",
            "difficulty": "intermediate",
            "interview_type": "technical",
            "question": "Explain Java's memory model: what is stored in the Stack vs the Heap? How does garbage collection operate in the JVM?",
            "hints": [
                "Stack stores thread-specific execution frames, primitive values, and object references.",
                "Heap stores actual object instances shared across threads.",
                "JVM GC divides Heap into Young Generation (Eden, Survivor) and Old/Tenured Generation."
            ],
            "rubric_keywords": ["stack", "heap", "primitives", "references", "garbage collection", "jvm", "young generation", "eden", "tenured"],
            "ideal_concepts": "The Stack holds method frames and local reference pointers, managed with LIFO execution. The Heap holds dynamically allocated objects. JVM garbage collectors (G1, ZGC) collect unreachable objects via generational mark-and-sweep.",
            "follow_up": "What is the difference between `==` and `.equals()` in Java, and why must you override `hashCode()` when overriding `.equals()`?"
        }
    ],
    "Web Development": [
        {
            "id": "web_1",
            "domain": "Web Development",
            "difficulty": "intermediate",
            "interview_type": "technical",
            "question": "Explain the Critical Rendering Path in modern web browsers. How do HTML, CSSOM, Render Tree, Layout, and Paint interact?",
            "hints": [
                "Browser parses HTML to create DOM, and CSS to create CSSOM.",
                "DOM + CSSOM merge into the Render Tree (only visible elements).",
                "Layout computes exact geometric coordinates; Paint fills in pixels."
            ],
            "rubric_keywords": ["critical rendering path", "dom", "cssom", "render tree", "layout", "paint", "reflow", "repaint", "blocking"],
            "ideal_concepts": "The Critical Rendering Path processes HTML into DOM and CSS into CSSOM, combines them into a Render Tree, calculates layout geometry (reflow), and paints pixels to screen. Minimizing render-blocking CSS/JS accelerates First Contentful Paint.",
            "follow_up": "How do `async` and `defer` attributes on script tags modify the HTML parsing and execution order?"
        }
    ],
    "Cloud": [
        {
            "id": "cloud_1",
            "domain": "Cloud",
            "difficulty": "intermediate",
            "interview_type": "technical",
            "question": "Explain the CAP Theorem in distributed cloud architectures. Can a distributed database achieve Consistency, Availability, and Partition Tolerance simultaneously?",
            "hints": [
                "Network partitions (P) are unavoidable in distributed physical networks.",
                "You must choose between Consistency (C - every read gets the latest write) and Availability (A - every request gets a non-error response).",
                "Examples: CP (MongoDB, HBase, Consul) vs AP (Cassandra, DynamoDB, CouchDB)."
            ],
            "rubric_keywords": ["cap theorem", "consistency", "availability", "partition tolerance", "network partition", "distributed", "eventual consistency"],
            "ideal_concepts": "CAP theorem states that a distributed data store can guarantee at most two out of Consistency, Availability, and Partition tolerance. Because network partitions (P) inevitably occur, systems must choose between Consistency (CP) or Availability (AP) during partitions.",
            "follow_up": "How does PACELC theorem extend the CAP theorem when the network is operating normally (without partitions)?"
        }
    ],
    "HR": [
        {
            "id": "hr_1",
            "domain": "HR",
            "difficulty": "intermediate",
            "interview_type": "hr",
            "question": "Describe a situation where you had a significant technical disagreement with a colleague or lead. How did you handle it and what was the outcome?",
            "hints": [
                "Structure your answer using STAR: Situation, Task, Action, Result.",
                "Focus on remaining objective, utilizing data, benchmarks, or prototypes to evaluate options.",
                "Emphasize professional communication, alignment, and commitment to the team's shared goal."
            ],
            "rubric_keywords": ["star method", "situation", "task", "action", "result", "disagreement", "data", "prototype", "collaboration", "resolution"],
            "ideal_concepts": "A strong behavioral response sets the context (S/T), explains how the candidate used evidence/prototypes rather than emotional arguments (A), and concludes with positive business outcome, team alignment, and relationship preservation (R).",
            "follow_up": "If the team ultimately decided on an approach you still disagreed with, how did you commit to supporting its execution?"
        },
        {
            "id": "hr_2",
            "domain": "HR",
            "difficulty": "intermediate",
            "interview_type": "hr",
            "question": "Tell me about a time you caused or encountered a severe production bug or critical system failure. What actions did you take?",
            "hints": [
                "Acknowledge responsibility and composure under pressure.",
                "Detail incident triage: rollback/mitigation first, root cause analysis second.",
                "Highlight blameless post-mortem, monitoring improvements, and preventative unit/integration tests added."
            ],
            "rubric_keywords": ["star method", "production bug", "incident", "mitigation", "rollback", "post-mortem", "root cause", "monitoring", "ownership"],
            "ideal_concepts": "Demonstrates high accountability, calm prioritization of user impact mitigation (rollback/circuit breaker), rigorous root cause investigation (5 Whys), and systemic guardrails added so the error never recurs.",
            "follow_up": "How did you communicate system status and timeline expectations to non-technical stakeholders during the outage?"
        }
    ]
}


def get_random_or_indexed_question(domain: str, interview_type: str, difficulty: str, exclude_ids: List[str] = None) -> Dict[str, Any]:
    exclude_ids = exclude_ids or []
    
    # Try exact domain match
    pool = QUESTION_BANK.get(domain, [])
    # Filter by interview type if domain is general
    if not pool or interview_type == "hr":
        pool = QUESTION_BANK.get("HR", []) if interview_type == "hr" else QUESTION_BANK.get("Python", [])
    
    available = [q for q in pool if q["id"] not in exclude_ids]
    if not available:
        available = pool

    if available:
        chosen = random.choice(available)
        return chosen
    
    # Generic fallback
    return {
        "id": f"dyn_{random.randint(100, 999)}",
        "domain": domain,
        "difficulty": difficulty,
        "interview_type": interview_type,
        "question": f"Discuss the core design principles, trade-offs, and best practices in {domain} when building scalable applications.",
        "hints": [
            f"Think about maintainability, testability, and runtime efficiency in {domain}.",
            "Identify key bottleneck areas such as I/O, concurrency, or data serialization.",
            "Contrast a naive implementation with an optimized architecture."
        ],
        "rubric_keywords": ["scalability", "architecture", "trade-offs", "performance", "design patterns", "best practices"],
        "ideal_concepts": f"Demonstrates solid foundational and architectural understanding of {domain}.",
        "follow_up": f"How do you profile and benchmark performance bottlenecks in {domain}?"
    }


def evaluate_candidate_answer(question_data: Dict[str, Any], answer: str, hints_used: int = 0) -> Dict[str, Any]:
    cleaned_answer = answer.strip()
    words = cleaned_answer.split()
    word_count = len(words)

    if word_count < 5:
        return {
            "score_correctness": 20.0,
            "score_clarity": 30.0,
            "score_depth": 15.0,
            "overall_turn_score": 21.0,
            "feedback": "Your response is too brief. In a technical interview, elaborate on the underlying principles, mechanisms, and real-world implications.",
            "strengths": ["Attempted response"],
            "missing_concepts": question_data.get("rubric_keywords", [])[:4],
            "follow_up_question": "Can you elaborate further and explain the step-by-step mechanism?"
        }

    rubric = question_data.get("rubric_keywords", [])
    lower_answer = cleaned_answer.lower()

    # Keyword coverage
    matched_keywords = [k for k in rubric if k in lower_answer]
    missing_keywords = [k for k in rubric if k not in lower_answer]

    coverage_ratio = len(matched_keywords) / max(1, len(rubric))
    
    # Calculate Correctness
    base_correctness = min(96.0, 50.0 + (coverage_ratio * 46.0))
    # Penalty for hints used (mentor guidance tracking)
    hint_penalty = min(20.0, hints_used * 5.0)
    score_correctness = max(35.0, round(base_correctness - hint_penalty, 1))

    # Calculate Clarity based on structure, sentence length, and vocabulary
    clarity_score = 75.0
    if word_count > 30:
        clarity_score += 15.0
    if any(trans in lower_answer for trans in ["because", "therefore", "in contrast", "for example", "specifically", "firstly", "furthermore"]):
        clarity_score += 10.0
    score_clarity = min(98.0, round(clarity_score, 1))

    # Calculate Technical Depth
    depth_score = 45.0 + (coverage_ratio * 40.0)
    if word_count > 60:
        depth_score += 10.0
    score_depth = min(95.0, round(depth_score, 1))

    # Overall Turn Score
    overall_turn_score = round((score_correctness * 0.45) + (score_depth * 0.35) + (score_clarity * 0.20), 1)

    # Strengths extraction
    strengths = []
    if matched_keywords:
        strengths.append(f"Successfully identified key concepts: {', '.join(matched_keywords[:3])}")
    if word_count >= 40:
        strengths.append("Structured and articulate explanation with good descriptive context")
    if not strengths:
        strengths.append("Clear communication and structured attempt")

    # Constructive Mentor Feedback
    feedback_parts = []
    if overall_turn_score >= 80:
        feedback_parts.append("Excellent, comprehensive answer demonstrating strong technical mastery!")
    elif overall_turn_score >= 60:
        feedback_parts.append("Good conceptual foundation! To make this answer top-tier, weave in more precise internal mechanics and practical trade-offs.")
    else:
        feedback_parts.append("Solid initial thought, but the answer lacks key technical terminology and mechanistic depth expected by senior interviewers.")

    if missing_keywords:
        feedback_parts.append(f"Key areas to incorporate: emphasize {', '.join(missing_keywords[:3])}.")

    feedback_str = " ".join(feedback_parts)

    return {
        "score_correctness": score_correctness,
        "score_clarity": score_clarity,
        "score_depth": score_depth,
        "overall_turn_score": overall_turn_score,
        "feedback": feedback_str,
        "strengths": strengths,
        "missing_concepts": missing_keywords[:4],
        "follow_up_question": question_data.get("follow_up", "What are the key trade-offs of this approach in high-throughput production?")
    }


def generate_final_interview_report(session: Any, turns: List[Any]) -> Dict[str, Any]:
    if not turns:
        return {
            "overall_score": 0.0,
            "readiness_level": "Incomplete",
            "grade": "N/A",
            "summary_feedback": "No interview questions were answered in this session.",
            "metric_averages": {"correctness": 0, "clarity": 0, "depth": 0},
            "key_strengths": [],
            "recommended_topics": []
        }

    correctness_vals = [t.score_correctness for t in turns if t.score_correctness is not None]
    clarity_vals = [t.score_clarity for t in turns if t.score_clarity is not None]
    depth_vals = [t.score_depth for t in turns if t.score_depth is not None]
    turn_scores = [t.overall_turn_score for t in turns if t.overall_turn_score is not None]

    avg_correctness = round(sum(correctness_vals) / len(correctness_vals), 1) if correctness_vals else 0
    avg_clarity = round(sum(clarity_vals) / len(clarity_vals), 1) if clarity_vals else 0
    avg_depth = round(sum(depth_vals) / len(depth_vals), 1) if depth_vals else 0
    overall = round(sum(turn_scores) / len(turn_scores), 1) if turn_scores else 0

    if overall >= 88:
        readiness = "Senior Ready / Highly Competitive"
        grade = "A+"
        summary = "Outstanding performance! You articulate deep architectural concepts, anticipate interviewer follow-ups, and communicate trade-offs crisply."
    elif overall >= 78:
        readiness = "Interview Ready (Standard Bar)"
        grade = "A"
        summary = "Strong domain competence. Your explanations are well-structured with solid technical accuracy. Continuing to practice edge cases will push you into top percentiles."
    elif overall >= 65:
        readiness = "Approaching Readiness"
        grade = "B"
        summary = "Good foundational knowledge. Focus on strengthening vocabulary precision, memory/concurrency internals, and concrete production examples."
    else:
        readiness = "Foundations Need Practice"
        grade = "C"
        summary = "Promising start, but additional preparation is recommended on core computer science foundations, system boundaries, and structured problem framing."

    # Collect missing concepts for recommendations
    all_missing = []
    all_strengths = []
    for t in turns:
        if t.missing_concepts:
            for item in t.missing_concepts.split(","):
                item_clean = item.strip()
                if item_clean and item_clean not in all_missing:
                    all_missing.append(item_clean)
        if t.strengths:
            for s in t.strengths.split("\n"):
                s_clean = s.strip()
                if s_clean and s_clean not in all_strengths:
                    all_strengths.append(s_clean)

    return {
        "overall_score": overall,
        "readiness_level": readiness,
        "grade": grade,
        "summary_feedback": summary,
        "metric_averages": {
            "correctness": avg_correctness,
            "clarity": avg_clarity,
            "depth": avg_depth
        },
        "key_strengths": all_strengths[:5] or ["Clear problem-solving attitude", "Responsive to hints"],
        "recommended_topics": all_missing[:6] or [f"{session.domain} system internals", "Time and space complexity proofs", "Failure recovery strategies"]
    }
