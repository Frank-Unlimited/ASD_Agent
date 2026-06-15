import requests
r = requests.post('http://localhost:8000/api/memory/search', json={'group_id': 'child_chenchen_001', 'query': '眼神接触', 'num_results': 5})
print(f'Status: {r.status_code}')
data = r.json()
print(f'Facts count: {len(data["facts"])}')
for i, f in enumerate(data['facts']):
    print(f'  [{i+1}] pending={f["pending"]} | {f["text"][:100]}')

# Also check queue status
r2 = requests.get('http://localhost:8000/healthcheck')
print(f'\nHealthcheck: {r2.json()}')

r3 = requests.get('http://localhost:8000/api/memory/queue/status')
print(f'Queue status: {r3.json()}')
