import requests

BASE = 'http://127.0.0.1:8000'

def run():
    print("Testing server endpoints...")
    # 1. UI Check
    r = requests.get(f'{BASE}/')
    assert r.status_code == 200, f'UI failed: {r.status_code}'
    print('[PASS] 1. Frontend UI served successfully')

    # 2. Stats Check
    r = requests.get(f'{BASE}/api/stats')
    assert r.status_code == 200
    stats = r.json()
    print('[PASS] 2. Stats API OK:', stats)

    # 3. Auth Check
    r = requests.post(f'{BASE}/api/auth/login', json={'email': 'candidate@prep.ai', 'password': 'Candidate@123'})
    assert r.status_code == 200
    token = r.json()['access_token']
    headers = {'Authorization': f'Bearer {token}'}
    print('[PASS] 3. Login API OK, JWT Token acquired')

    # 4. Chat Check (Ambiguity & Socratic Mentor)
    r = requests.post(f'{BASE}/api/chat', json={'message': 'which is best?', 'mode': 'mentor', 'level': 'intermediate', 'use_rag': True}, headers=headers)
    assert r.status_code == 200
    assert r.json()['is_ambiguous'] == True
    print('[PASS] 4. NLP Ambiguity Detection OK:', r.json()['clarification_question'])

    # 5. Chat Check (Technical + RAG)
    r = requests.post(f'{BASE}/api/chat', json={'message': 'Explain Python GIL and multithreading', 'mode': 'mentor', 'level': 'intermediate', 'use_rag': True}, headers=headers)
    assert r.status_code == 200
    print('[PASS] 5. Socratic Mentor Chat + RAG OK. Sources retrieved:', len(r.json()['rag_sources']))

    # 6. Interview Flow
    r = requests.post(f'{BASE}/api/interview/start', json={'domain': 'Python', 'interview_type': 'technical', 'difficulty': 'intermediate'}, headers=headers)
    assert r.status_code == 200
    session_id = r.json()['session_id']
    print('[PASS] 6. Mock Interview Started. Session ID:', session_id)

    # 7. Request Hint
    r = requests.post(f'{BASE}/api/interview/hint', json={'session_id': session_id, 'hint_level': 1}, headers=headers)
    assert r.status_code == 200
    print('[PASS] 7. Hint Level 1 Retrieved:', r.json()['hint'][:60] + '...')

    # 8. Submit Answer & Evaluation
    r = requests.post(f'{BASE}/api/interview/evaluate', json={'session_id': session_id, 'answer': 'Python uses reference counting in CPython to manage memory. When reference count drops to zero, the object is immediately deallocated. To solve circular references, Python uses a generational garbage collector with generations 0, 1, and 2.'}, headers=headers)
    assert r.status_code == 200
    eval_res = r.json()
    print('[PASS] 8. Answer Evaluation OK! Overall Turn Score:', eval_res['overall_turn_score'], 'Correctness:', eval_res['score_correctness'])

    # 9. Coding Lab
    r = requests.get(f'{BASE}/api/coding/problems')
    assert r.status_code == 200
    print('[PASS] 9. Coding Problems Bank OK. Count:', len(r.json()))

    r = requests.post(f'{BASE}/api/coding/hint', json={'problem_id': 'two-sum', 'hint_level': 4})
    assert r.status_code == 200
    print('[PASS] 10. Coding Progressive Hint Level 4 OK')

    # 11. Vector Search
    r = requests.post(f'{BASE}/api/documents/search', json={'query': 'B-Tree indexing and SQL', 'top_k': 2})
    assert r.status_code == 200
    print('[PASS] 11. Vector Semantic Search OK. Matches found:', len(r.json()['results']))

    print('\n=============================================')
    print('ALL VERIFICATION TESTS COMPLETED SUCCESSFULLY!')
    print('=============================================')

if __name__ == '__main__':
    run()
