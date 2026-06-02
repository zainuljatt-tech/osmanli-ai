import httpx, json

BASE = "http://localhost:8000/api/v1"

# Login
r = httpx.post(f"{BASE}/auth/login", json={"email": "demo@test.com", "password": "password123"})
token = r.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}

# Create chat
r = httpx.post(f"{BASE}/chat", json={}, headers=headers)
chat_id = r.json()["id"]
print(f"Chat created: {chat_id}")

# Send message
r = httpx.post(
    f"{BASE}/chat/{chat_id}/messages",
    json={"content": "Hello! Who are you?"},
    headers=headers,
    timeout=15,
)
print(f"Status: {r.status_code}")

# Parse streaming response
for line in r.text.split("\n"):
    line = line.strip()
    if not line:
        continue
    try:
        data = json.loads(line)
        if data.get("type") == "content":
            print(f"\nAI Response:\n{data['content'][:200]}")
        elif data.get("type") == "status":
            print(f"[{data['content']}]")
    except json.JSONDecodeError:
        pass
