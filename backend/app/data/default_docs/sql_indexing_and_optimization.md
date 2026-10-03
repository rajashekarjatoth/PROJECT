# SQL & Relational Database Engineering

## ACID Properties Explained:
- **Atomicity**: Entire transaction succeeds or rolls back completely (All or Nothing).
- **Consistency**: The database moves from one valid state to another, respecting all constraints, foreign keys, and triggers.
- **Isolation**: Concurrent transactions execute as if sequential. Isolation levels: Read Uncommitted, Read Committed, Repeatable Read, Serializable.
- **Durability**: Once committed, changes survive power outages or server crashes via Write-Ahead Logging (WAL).

## Indexing Fundamentals (B-Trees):
- Relational databases (PostgreSQL, MySQL InnoDB) use B+ Tree indexes for fast logarithmic search O(log N).
- **Composite Indexes**: The "Leftmost Prefix Rule" dictates that an index on (A, B, C) can be used for queries filtering on (A), (A, B), or (A, B, C), but NOT on (B, C) alone.
- Avoid applying functions on indexed columns in `WHERE` clauses (e.g., `WHERE YEAR(created_at) = 2024` prevents index lookup; use range scan instead: `WHERE created_at >= '2024-01-01' AND created_at < '2025-01-01'`).