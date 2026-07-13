def seed_script(client, headers):
    product = client.post(
        "/api/products",
        headers=headers,
        json={"product_name": "视频商品", "category": "测试", "price": 30, "stock": 3},
    ).json()["data"]
    script = client.post(
        "/api/scripts",
        headers=headers,
        json={"product_id": product["id"], "title": "视频脚本", "scenes": []},
    ).json()["data"]
    return product["id"], script["id"]


def test_video_task_crud_and_state_transition(client, auth_headers):
    headers = auth_headers["admin"]
    product_id, script_id = seed_script(client, headers)
    payload = {
        "product_id": product_id,
        "script_id": script_id,
        "title": "隔离视频任务",
        "platform": "抖音",
    }
    created = client.post("/api/video-tasks", headers=headers, json=payload)
    assert created.status_code == 201
    task_id = created.json()["data"]["id"]
    started = client.put(
        f"/api/video-tasks/{task_id}", headers=headers, json={"status": "制作中"}
    )
    assert started.status_code == 200
    invalid = client.put(
        f"/api/video-tasks/{task_id}", headers=headers, json={"status": "已发布"}
    )
    assert invalid.status_code == 422
    listed = client.get("/api/video-tasks?status=制作中", headers=headers)
    assert isinstance(listed.json()["data"], list)
    assert listed.json()["data"][0]["id"] == task_id
    deleted = client.delete(f"/api/video-tasks/{task_id}", headers=headers)
    assert deleted.status_code == 200


def test_video_task_rejects_missing_script(client, auth_headers):
    headers = auth_headers["admin"]
    product_id, _ = seed_script(client, headers)
    response = client.post(
        "/api/video-tasks",
        headers=headers,
        json={"product_id": product_id, "script_id": 999, "title": "missing"},
    )
    assert response.status_code == 404
