# Machine Learning & RAG Systems Architecture

## The RAG (Retrieval-Augmented Generation) Paradigm:
1. **Document Preprocessing**: Chunking raw text into coherent semantic windows (typically 250-500 tokens with 10-20% overlap).
2. **Dense Vector Embeddings**: Transforming text chunks into high-dimensional latent vectors using models like `sentence-transformers` or text-embedding-3.
3. **Vector Similarity Search**: Utilizing HNSW (Hierarchical Navigable Small World) or Inverted File Flat (IVFFlat) indexes with Cosine Similarity or Dot Product to retrieve Top-K closest passages.
4. **Context Injection**: Constructing a structured system prompt combining retrieved passages, user persona, and user question, preventing hallucinations.

## Bias-Variance Tradeoff:
- **High Bias (Underfitting)**: Model is overly simplistic, fails to capture underlying patterns. Remedy: Increase model complexity, engineer informative features, reduce regularization.
- **High Variance (Overfitting)**: Model memorizes training noise, fails to generalize to validation data. Remedy: L1/L2 regularization, dropout, cross-validation, data augmentation.