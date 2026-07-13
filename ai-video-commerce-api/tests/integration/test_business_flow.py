def assert_success(response, status_code):
    assert response.status_code == status_code, response.text
    body = response.json()
    assert body["code"] == status_code
    assert "data" in body
    return body["data"]


def test_complete_business_chain_in_isolated_database(client, users):
    login = client.post(
        "/api/auth/login",
        json={"username": users["admin"].username, "password": "isolated-strong-password"},
    )
    auth_data = assert_success(login, 200)
    headers = {"Authorization": f"Bearer {auth_data['access_token']}"}
    profile = assert_success(client.get("/api/auth/me", headers=headers), 200)
    assert profile["role"] == "admin"

    product = assert_success(
        client.post(
            "/api/products",
            headers=headers,
            json={"product_name": "业务链商品", "category": "测试", "price": 88, "stock": 8},
        ),
        201,
    )
    analysis = assert_success(
        client.post(
            "/api/content-analyses",
            headers=headers,
            json={
                "product_id": product["id"],
                "platform": "抖音",
                "content_title": "业务链拆解",
                "status": "待拆解",
            },
        ),
        201,
    )
    script = assert_success(
        client.post(
            "/api/scripts",
            headers=headers,
            json={
                "product_id": product["id"],
                "content_analysis_id": analysis["id"],
                "title": "业务链脚本",
                "scenes": [{"scene_number": 1, "visual_content": "业务链镜头"}],
            },
        ),
        201,
    )
    task = assert_success(
        client.post(
            "/api/video-tasks",
            headers=headers,
            json={
                "product_id": product["id"],
                "script_id": script["id"],
                "title": "业务链视频",
            },
        ),
        201,
    )
    knowledge = assert_success(
        client.post(
            "/api/knowledge-items",
            headers=headers,
            json={
                "product_id": product["id"],
                "title": "业务链知识",
                "category": "运营经验",
                "content": "业务链正文",
            },
        ),
        201,
    )
    settings = assert_success(
        client.put(
            "/api/system-settings",
            headers=headers,
            json={"platform_name": "业务链隔离平台"},
        ),
        200,
    )
    assert settings["platform_name"] == "业务链隔离平台"

    assert_success(
        client.put(
            f"/api/products/{product['id']}", headers=headers, json={"stock": 7}
        ),
        200,
    )
    assert_success(
        client.put(
            f"/api/content-analyses/{analysis['id']}",
            headers=headers,
            json={"status": "拆解中"},
        ),
        200,
    )
    assert_success(
        client.put(
            f"/api/scripts/{script['id']}", headers=headers, json={"status": "待审核"}
        ),
        200,
    )
    assert_success(
        client.put(
            f"/api/video-tasks/{task['id']}", headers=headers, json={"status": "制作中"}
        ),
        200,
    )
    used = assert_success(
        client.post(f"/api/knowledge-items/{knowledge['id']}/use", headers=headers),
        200,
    )
    assert used["usage_count"] == 1

    assert_success(client.delete(f"/api/video-tasks/{task['id']}", headers=headers), 200)
    assert_success(client.delete(f"/api/scripts/{script['id']}", headers=headers), 200)
    assert_success(
        client.delete(f"/api/content-analyses/{analysis['id']}", headers=headers), 200
    )
    assert_success(
        client.delete(f"/api/knowledge-items/{knowledge['id']}", headers=headers), 200
    )
    assert_success(client.delete(f"/api/products/{product['id']}", headers=headers), 200)

    missing = client.delete(f"/api/products/{product['id']}", headers=headers)
    assert missing.status_code == 404
