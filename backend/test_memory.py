"""Test memory_service write and search endpoints."""
import time
import requests

BASE = "http://localhost:8000"

print("=== Testing HEALTHCHECK ===")
r = requests.get(f"{BASE}/healthcheck")
print(f"Status: {r.status_code}")
print(f"Response: {r.json()}")

print("\n=== Testing WRITE ===")
write_payload = {
    "group_id": "child_chenchen_001",
    "content": "辰辰在积木游戏中表现出3次主动眼神接触，互动积极性提升",
    "reference_time": "2026-06-15T10:30:00+08:00"
}
r = requests.post(f"{BASE}/api/memory/write", json=write_payload)
print(f"Status: {r.status_code}")
print(f"Response: {r.json()}")

print("\n=== Waiting 8 seconds for Graphiti processing ===")
time.sleep(8)

print("\n=== Testing SEARCH ===")
search_payload = {
    "group_id": "child_chenchen_001",
    "query": "眼神接触",
    "num_results": 5
}
r = requests.post(f"{BASE}/api/memory/search", json=search_payload)
print(f"Status: {r.status_code}")
print(f"Response: {r.json()}")

facts = r.json().get("facts", [])
print(f"\n=== Result: {len(facts)} facts found ===")
for i, f in enumerate(facts):
    print(f"  [{i+1}] pending={f.get('pending')} | {f.get('text', '')[:80]}")
