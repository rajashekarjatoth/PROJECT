# Python Internals, Concurrency, and the GIL

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
   - Generators yield values one at a time using `yield`, keeping O(1) auxiliary space rather than allocating full lists in memory.