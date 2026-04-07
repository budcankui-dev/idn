"""
Chat Session CRUD API 使用指南

基础 URL: http://localhost:6000
"""

# ============================================================
# 1. 创建会话 (POST)
# ============================================================
POST /session/submit
Content-Type: application/json

{
  "session_id": "sess_123",
  "business": "intent_parsing",
  "prompt": "用户的提示词",
  "history": [
    {
      "user": "用户问题1",
      "assistant": "助手回答1"
    }
  ],
  "state": {
    "current_intent": "booking",
    "status": "processing"
  },
  "params": {
    "temperature": 0.7,
    "max_tokens": 2000
  },
  "dag": {
    "nodes": ["step1", "step2"],
    "edges": [["step1", "step2"]]
  }
}

# 成功响应 (201):
{
  "id": 1,
  "session_id": "sess_123"
}


# ============================================================
# 2. 获取会话 (GET)
# ============================================================
GET /session/{session_id}

# 例如: GET /session/sess_123

# 成功响应 (200):
{
  "id": 1,
  "session_id": "sess_123",
  "business": "intent_parsing",
  "prompt": "用户的提示词",
  "history": [...],
  "state": {...},
  "params": {...},
  "dag": {...},
  "created_at": "2026-03-31T21:34:27.714000",
  "updated_at": "2026-03-31T21:34:27.714000"
}


# ============================================================
# 3. 更新会话 (PUT)
# ============================================================
PUT /session/{session_id}
Content-Type: application/json

{
  "prompt": "更新的提示词",
  "state": {
    "current_intent": "booking",
    "status": "completed"
  }
}

# 例如: PUT /session/sess_123

# 成功响应 (200):
{
  "id": 1,
  "session_id": "sess_123",
  ...
}


# ============================================================
# 4. 删除会话 (DELETE)
# ============================================================
DELETE /session/{session_id}

# 例如: DELETE /session/sess_123

# 成功响应 (200):
{
  "message": "Session deleted successfully"
}


# ============================================================
# cURL 命令示例
# ============================================================

# 创建会话
curl -X POST http://localhost:6000/session/submit \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "test_sess_1",
    "business": "test",
    "state": {"status": "new"},
    "params": {"test": true},
    "dag": {"nodes": []}
  }'

# 获取会话
curl -X GET http://localhost:6000/session/test_sess_1

# 更新会话
curl -X PUT http://localhost:6000/session/test_sess_1 \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "updated prompt",
    "state": {"status": "processing"}
  }'

# 删除会话
curl -X DELETE http://localhost:6000/session/test_sess_1


# ============================================================
# Python requests 示例
# ============================================================

import requests

BASE_URL = "http://localhost:6000"

# 创建会话
response = requests.post(
    f"{BASE_URL}/session/submit",
    json={
        "session_id": "test_sess_1",
        "business": "intent",
        "state": {"status": "new"},
        "params": {"test": True},
        "dag": {"nodes": []}
    }
)
print(response.json())

# 获取会话
response = requests.get(f"{BASE_URL}/session/test_sess_1")
print(response.json())

# 更新会话
response = requests.put(
    f"{BASE_URL}/session/test_sess_1",
    json={"state": {"status": "updated"}}
)
print(response.json())

# 删除会话
response = requests.delete(f"{BASE_URL}/session/test_sess_1")
print(response.json())


# ============================================================
# JavaScript fetch 示例
# ============================================================

const BASE_URL = "http://localhost:6000";

// 创建会话
fetch(`${BASE_URL}/session/submit`, {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    session_id: "test_sess_1",
    business: "intent",
    state: { status: "new" },
    params: { test: true },
    dag: { nodes: [] }
  })
})
.then(r => r.json())
.then(data => console.log(data));

// 获取会话
fetch(`${BASE_URL}/session/test_sess_1`)
  .then(r => r.json())
  .then(data => console.log(data));

// 更新会话
fetch(`${BASE_URL}/session/test_sess_1`, {
  method: "PUT",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({ state: { status: "updated" } })
})
.then(r => r.json())
.then(data => console.log(data));

// 删除会话
fetch(`${BASE_URL}/session/test_sess_1`, { method: "DELETE" })
  .then(r => r.json())
  .then(data => console.log(data));
