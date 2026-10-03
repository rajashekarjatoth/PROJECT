from typing import Dict, List, Any, Optional

CODING_PROBLEMS: Dict[str, Dict[str, Any]] = {
    "two-sum": {
        "id": "two-sum",
        "title": "Two Sum",
        "difficulty": "Easy",
        "category": "Arrays & Hashing",
        "description": "Given an array of integers `nums` and an integer `target`, return indices of the two numbers such that they add up to `target`. You may assume that each input would have exactly one solution, and you may not use the same element twice.",
        "examples": [
            {"input": "nums = [2, 7, 11, 15], target = 9", "output": "[0, 1]", "explanation": "Because nums[0] + nums[1] == 9, we return [0, 1]."},
            {"input": "nums = [3, 2, 4], target = 6", "output": "[1, 2]", "explanation": "nums[1] + nums[2] == 6."}
        ],
        "constraints": [
            "2 <= nums.length <= 10^4",
            "-10^9 <= nums[i] <= 10^9",
            "-10^9 <= target <= 10^9",
            "Only one valid answer exists."
        ],
        "starter_code": {
            "python": "def twoSum(nums: list[int], target: int) -> list[int]:\n    # Your solution here\n    pass\n",
            "javascript": "function twoSum(nums, target) {\n    // Your solution here\n}\n"
        },
        "hints": {
            1: {
                "type": "Intuition & Edge Cases",
                "content": "A brute-force solution checks every pair with nested loops, taking O(N^2) time. Can we do better? When inspecting an element `x`, what number are we desperately searching for? Exactly `complement = target - x`!"
            },
            2: {
                "type": "Optimal Approach & Data Structure",
                "content": "To check if `complement` exists in O(1) time, what data structure provides constant-time lookups? A Hash Map (dictionary)! We can store numbers as keys and their array indices as values as we iterate."
            },
            3: {
                "type": "Step-by-Step Pseudocode",
                "content": """1. Initialize an empty hash map `seen = {}`.
2. Loop through `nums` with index `i` and value `num`:
   a. Compute `complement = target - num`.
   b. If `complement` in `seen`, return `[seen[complement], i]`.
   c. Otherwise, record `seen[num] = i`.
3. Return empty list if no pair found."""
            },
            4: {
                "type": "Final Solution & Line-by-Line Breakdown",
                "code": """def twoSum(nums: list[int], target: int) -> list[int]:
    seen = {}
    for i, num in enumerate(nums):
        complement = target - num
        if complement in seen:
            return [seen[complement], i]
        seen[num] = i
    return []""",
                "breakdown": [
                    "Line 2: `seen = {}` initializes an empty hash map to store previously seen numbers and their indices.",
                    "Line 3: `for i, num in enumerate(nums):` iterates through the list in a single pass, giving us both the index `i` and value `num`.",
                    "Line 4: `complement = target - num` calculates the exact match needed to reach the target sum.",
                    "Line 5: `if complement in seen:` performs an O(1) average-time dictionary lookup to verify if the needed number was previously seen.",
                    "Line 6: `return [seen[complement], i]` returns the pair of indices immediately upon finding the match.",
                    "Line 7: `seen[num] = i` caches the current number and its index so subsequent elements can match against it.",
                    "Complexity: Time Complexity O(N) single-pass; Space Complexity O(N) auxiliary space for the hash table."
                ]
            }
        }
    },
    "valid-parentheses": {
        "id": "valid-parentheses",
        "title": "Valid Parentheses",
        "difficulty": "Easy",
        "category": "Stack",
        "description": "Given a string `s` containing just the characters '(', ')', '{', '}', '[' and ']', determine if the input string is valid.\nAn input string is valid if open brackets are closed by the same type of brackets in the correct LIFO order.",
        "examples": [
            {"input": 's = "()"', "output": "true", "explanation": "Properly opened and closed."},
            {"input": 's = "()[]{}"', "output": "true", "explanation": "All matched properly."},
            {"input": 's = "(]"', "output": "false", "explanation": "Mismatched closing bracket."}
        ],
        "constraints": [
            "1 <= s.length <= 10^4",
            "s consists of parentheses only '()[]{}'."
        ],
        "starter_code": {
            "python": "def isValid(s: str) -> bool:\n    # Your solution here\n    pass\n",
            "javascript": "function isValid(s) {\n    // Your solution here\n}\n"
        },
        "hints": {
            1: {
                "type": "Intuition & Edge Cases",
                "content": "Notice the ordering: the most recently opened bracket must be the first one closed. What fundamental data structure enforces Last-In, First-Out (LIFO) behavior? Also, check if string length is odd—if so, it can never be valid!"
            },
            2: {
                "type": "Approach & Mapping",
                "content": "Use a Stack! Map each closing bracket to its corresponding opening bracket: `mapping = {')': '(', '}': '{', ']': '['}`. When encountering an open bracket, push it onto the stack. When encountering a close bracket, verify the top of the stack matches."
            },
            3: {
                "type": "Step-by-Step Pseudocode",
                "content": """1. If length of `s` is odd, return False.
2. Initialize `stack = []` and `mapping = {')': '(', '}': '{', ']': '['}`.
3. For each char `c` in `s`:
   a. If `c` is in `mapping` (it is a closing bracket):
      - Pop top element from stack (or '#' if stack is empty).
      - If popped element does not match `mapping[c]`, return False.
   b. Else (it is an opening bracket):
      - Push `c` onto `stack`.
4. Return `len(stack) == 0` (stack must be empty at the end)."""
            },
            4: {
                "type": "Final Solution & Line-by-Line Breakdown",
                "code": """def isValid(s: str) -> bool:
    if len(s) % 2 != 0:
        return False
    stack = []
    mapping = {')': '(', '}': '{', ']': '['}
    for char in s:
        if char in mapping:
            top_element = stack.pop() if stack else '#'
            if mapping[char] != top_element:
                return False
        else:
            stack.append(char)
    return not stack""",
                "breakdown": [
                    "Line 2-3: `if len(s) % 2 != 0:` early exit guard clause; odd lengths cannot pair up.",
                    "Line 4: `stack = []` creates our LIFO stack.",
                    "Line 5: `mapping = ...` maps closing delimiters to expected opening counterparts.",
                    "Line 6-7: Iterates through each character. If it exists in `mapping`, it's a closing bracket.",
                    "Line 8: `stack.pop() if stack else '#'` safely retrieves the top element without raising IndexError on empty stack.",
                    "Line 9-10: Checks if the popped opening bracket matches the expected opener for this closing bracket.",
                    "Line 12: `stack.append(char)` pushes opening brackets onto the stack.",
                    "Line 13: `return not stack` returns True only if all brackets were resolved and stack is completely empty.",
                    "Complexity: Time Complexity O(N) linear scan; Space Complexity O(N) worst-case stack depth."
                ]
            }
        }
    },
    "lru-cache": {
        "id": "lru-cache",
        "title": "LRU (Least Recently Used) Cache",
        "difficulty": "Medium",
        "category": "Design & Data Structures",
        "description": "Design a data structure that follows the constraints of a Least Recently Used (LRU) cache. Implement the `LRUCache` class with `get(key)` and `put(key, value)` both running in O(1) average time complexity.",
        "examples": [
            {"input": 'lRUCache = new LRUCache(2); lRUCache.put(1, 1); lRUCache.put(2, 2); lRUCache.get(1); lRUCache.put(3, 3); // evicts key 2', "output": "null, null, null, 1, null", "explanation": "Key 2 was evicted because key 1 was accessed via get()."}
        ],
        "constraints": [
            "1 <= capacity <= 3000",
            "0 <= key <= 10^4",
            "0 <= value <= 10^5",
            "At most 2 * 10^5 calls to get and put."
        ],
        "starter_code": {
            "python": "class LRUCache:\n    def __init__(self, capacity: int):\n        pass\n    def get(self, key: int) -> int:\n        pass\n    def put(self, key: int, value: int) -> None:\n        pass\n",
            "javascript": "class LRUCache {\n    constructor(capacity) {}\n    get(key) {}\n    put(key, value) {}\n}\n"
        },
        "hints": {
            1: {
                "type": "Intuition & Requirements",
                "content": "We need O(1) lookup AND O(1) removal/insertion of elements. A Hash Map gives O(1) lookup but lacks ordering. An Array preserves ordering but requires O(N) to shift elements on eviction. What structure allows O(1) pointer updates anywhere?"
            },
            2: {
                "type": "Combined Data Structure",
                "content": "Combine a Hash Map with a Doubly Linked List! Hash map maps `key -> Node`. Doubly linked list maintains chronological order: dummy `head` for Most Recently Used, dummy `tail` for Least Recently Used. When accessed, detach node and re-insert at `head`."
            },
            3: {
                "type": "Step-by-Step Pseudocode",
                "content": """1. Define `Node(key, value, prev, next)`.
2. In `LRUCache`, create dummy `head` and `tail` nodes connected to each other.
3. Helper `_remove(node)`: connects `node.prev` to `node.next`.
4. Helper `_insert(node)`: inserts `node` right after `head`.
5. `get(key)`: if key in cache, move node to head via remove and insert, return value; else return -1.
6. `put(key, value)`: if key in cache, remove existing node. Create new node, insert at head, add to cache. If len > capacity, remove node before `tail` and delete from cache."""
            },
            4: {
                "type": "Final Solution & Line-by-Line Breakdown",
                "code": """class Node:
    def __init__(self, key: int, val: int):
        self.key, self.val = key, val
        self.prev = self.next = None

class LRUCache:
    def __init__(self, capacity: int):
        self.cap = capacity
        self.cache = {}  # key -> Node
        self.head, self.tail = Node(0, 0), Node(0, 0)
        self.head.next, self.tail.prev = self.tail, self.head

    def _remove(self, node: Node):
        prev, nxt = node.prev, node.next
        prev.next, nxt.prev = nxt, prev

    def _add(self, node: Node):
        node.prev = self.head
        node.next = self.head.next
        self.head.next.prev = node
        self.head.next = node

    def get(self, key: int) -> int:
        if key in self.cache:
            self._remove(self.cache[key])
            self._add(self.cache[key])
            return self.cache[key].val
        return -1

    def put(self, key: int, value: int) -> None:
        if key in self.cache:
            self._remove(self.cache[key])
        node = Node(key, value)
        self.cache[key] = node
        self._add(node)
        if len(self.cache) > self.cap:
            lru = self.tail.prev
            self._remove(lru)
            del self.cache[lru.key]""",
                "breakdown": [
                    "Lines 1-4: Doubly Linked List node with pointers to both previous and next nodes.",
                    "Lines 7-12: Constructor initializes dummy head and tail sentinels to eliminate null boundary checks.",
                    "Lines 14-16: `_remove()` unlinks node in O(1) pointer updates.",
                    "Lines 18-22: `_add()` inserts node directly behind head (marking it Most Recently Used).",
                    "Lines 24-29: `get()` updates node position to MRU upon access and returns stored value in O(1).",
                    "Lines 31-40: `put()` updates or inserts new node, and if capacity is exceeded, unlinks LRU node preceding dummy tail.",
                    "Complexity: Both operations guaranteed O(1) time complexity; O(capacity) space."
                ]
            }
        }
    }
}


def get_all_coding_problems() -> List[Dict[str, Any]]:
    summary = []
    for pid, prob in CODING_PROBLEMS.items():
        summary.append({
            "id": prob["id"],
            "title": prob["title"],
            "difficulty": prob["difficulty"],
            "category": prob["category"],
            "description": prob["description"],
            "examples": prob["examples"],
            "constraints": prob["constraints"],
            "starter_code": prob["starter_code"]
        })
    return summary


def get_coding_problem_details(problem_id: str) -> Optional[Dict[str, Any]]:
    return CODING_PROBLEMS.get(problem_id)


def get_coding_hint(problem_id: str, hint_level: int) -> Dict[str, Any]:
    problem = CODING_PROBLEMS.get(problem_id)
    if not problem:
        return {"error": "Problem not found"}
    
    hints = problem.get("hints", {})
    hint_data = hints.get(hint_level)
    if not hint_data:
        # Fallback to level 1 or maximum available
        max_level = max(hints.keys())
        hint_data = hints.get(max_level)
        hint_level = max_level

    return {
        "problem_id": problem_id,
        "hint_level": hint_level,
        "hint_type": hint_data.get("type", "Guidance"),
        "content": hint_data.get("content", ""),
        "code": hint_data.get("code", None),
        "breakdown": hint_data.get("breakdown", None),
        "next_hint_available": (hint_level < 4)
    }
