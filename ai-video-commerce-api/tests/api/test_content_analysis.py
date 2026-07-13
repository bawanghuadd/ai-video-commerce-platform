def create_product(client, headers):
    response = client.post(
        "/api/products",
        headers=headers,
        json={
            "product_name": "内容关联商品",
            "category": "测试",
            "price": 10,
            "stock": 1,
        },
    )
    return response.json()["data"]["id"]


def test_content_analysis_crud_and_filters(client, auth_headers):
    headers = auth_headers["admin"]
    product_id = create_product(client, headers)
    payload = {
        "product_id": product_id,
        "platform": "抖音",
        "content_title": "隔离拆解",
        "status": "待拆解",
    }
    created = client.post("/api/content-analyses", headers=headers, json=payload)
    assert created.status_code == 201
    analysis_id = created.json()["data"]["id"]

    listed = client.get(
        f"/api/content-analyses?product_id={product_id}&status=待拆解",
        headers=headers,
    )
    assert listed.status_code == 200
    assert isinstance(listed.json()["data"], list)
    assert listed.json()["data"][0]["id"] == analysis_id

    updated = client.put(
        f"/api/content-analyses/{analysis_id}",
        headers=headers,
        json={"status": "已拆解"},
    )
    assert updated.status_code == 200
    assert updated.json()["data"]["status"] == "已拆解"

    deleted = client.delete(f"/api/content-analyses/{analysis_id}", headers=headers)
    assert deleted.status_code == 200


def test_content_analysis_rejects_invalid_reference_and_status(client, auth_headers):
    headers = auth_headers["admin"]
    missing_product = client.post(
        "/api/content-analyses",
        headers=headers,
        json={"product_id": 999, "content_title": "无效关联"},
    )
    assert missing_product.status_code == 404

    product_id = create_product(client, headers)
    invalid_status = client.post(
        "/api/content-analyses",
        headers=headers,
        json={"product_id": product_id, "content_title": "无效状态", "status": "未知"},
    )
    assert invalid_status.status_code == 422
