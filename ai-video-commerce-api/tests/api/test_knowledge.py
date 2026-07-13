def test_knowledge_crud_filters_and_atomic_usage(client, auth_headers):
    headers = auth_headers["admin"]
    payload = {
        "title": "隔离知识",
        "category": "运营经验",
        "content": "知识正文",
        "tags": ["测试", "测试", " API "],
        "status": "草稿",
        "is_featured": True,
    }
    created = client.post("/api/knowledge-items", headers=headers, json=payload)
    assert created.status_code == 201
    knowledge_id = created.json()["data"]["id"]
    assert created.json()["data"]["tags"] == ["测试", "API"]

    for expected in (1, 2):
        used = client.post(f"/api/knowledge-items/{knowledge_id}/use", headers=headers)
        assert used.status_code == 200
        assert used.json()["data"]["usage_count"] == expected

    listed = client.get(
        "/api/knowledge-items?category=运营经验&status=草稿&is_featured=true",
        headers=headers,
    )
    assert isinstance(listed.json()["data"], list)
    assert listed.json()["data"][0]["id"] == knowledge_id

    updated = client.put(
        f"/api/knowledge-items/{knowledge_id}",
        headers=headers,
        json={"status": "已发布"},
    )
    assert updated.status_code == 200
    deleted = client.delete(f"/api/knowledge-items/{knowledge_id}", headers=headers)
    assert deleted.status_code == 200


def test_knowledge_missing_and_invalid_status(client, auth_headers):
    headers = auth_headers["admin"]
    missing = client.post("/api/knowledge-items/999/use", headers=headers)
    assert missing.status_code == 404
    invalid = client.post(
        "/api/knowledge-items",
        headers=headers,
        json={"title": "invalid", "category": "test", "content": "body", "status": "未知"},
    )
    assert invalid.status_code == 422
