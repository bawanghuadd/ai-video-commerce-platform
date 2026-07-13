from app.models.script import Script
from app.schemas.script import ScriptUpdate
from app.services.script import ScriptService


def seed_product_and_analysis(client, headers, suffix="a"):
    product = client.post(
        "/api/products",
        headers=headers,
        json={"product_name": f"脚本商品{suffix}", "category": "测试", "price": 20, "stock": 2},
    ).json()["data"]
    analysis = client.post(
        "/api/content-analyses",
        headers=headers,
        json={"product_id": product["id"], "content_title": f"拆解{suffix}"},
    ).json()["data"]
    return product["id"], analysis["id"]


def script_payload(product_id, analysis_id):
    return {
        "product_id": product_id,
        "content_analysis_id": analysis_id,
        "title": "隔离脚本",
        "platform": "抖音",
        "status": "草稿",
        "scenes": [
            {"scene_number": 1, "visual_content": "镜头一"},
            {"scene_number": 2, "visual_content": "镜头二"},
        ],
    }


def test_script_and_scene_crud_is_atomic_and_ordered(client, auth_headers):
    headers = auth_headers["admin"]
    product_id, analysis_id = seed_product_and_analysis(client, headers)
    created = client.post(
        "/api/scripts", headers=headers, json=script_payload(product_id, analysis_id)
    )
    assert created.status_code == 201
    script_id = created.json()["data"]["id"]
    assert [scene["scene_number"] for scene in created.json()["data"]["scenes"]] == [1, 2]

    updated = client.put(
        f"/api/scripts/{script_id}",
        headers=headers,
        json={"scenes": [{"scene_number": 1, "visual_content": "替换镜头"}]},
    )
    assert updated.status_code == 200
    assert [scene["visual_content"] for scene in updated.json()["data"]["scenes"]] == ["替换镜头"]

    listed = client.get("/api/scripts", headers=headers)
    assert isinstance(listed.json()["data"], list)
    assert listed.json()["data"][0]["id"] == script_id


def test_script_rejects_mismatched_analysis(client, auth_headers):
    headers = auth_headers["admin"]
    product_a, _ = seed_product_and_analysis(client, headers, "a")
    _, analysis_b = seed_product_and_analysis(client, headers, "b")
    response = client.post(
        "/api/scripts", headers=headers, json=script_payload(product_a, analysis_b)
    )
    assert response.status_code == 422
    assert response.json()["detail"] == "内容拆解记录与所选商品不一致"


def test_scene_replacement_failure_rolls_back(db_session, monkeypatch):
    product_id = 1
    from app.models.product import Product

    product = Product(product_name="rollback", category="test", price=1, stock=1)
    db_session.add(product)
    db_session.commit()
    script = Script(product_id=product.id, title="rollback")
    from app.models.script import ScriptScene

    script.scenes.append(ScriptScene(scene_number=1, visual_content="original"))
    db_session.add(script)
    db_session.commit()

    service = ScriptService(db_session)
    original_flush = service.repository.flush

    def fail_final_flush():
        raise RuntimeError("simulated scene insert failure")

    monkeypatch.setattr(service.repository, "flush", fail_final_flush)
    try:
        service.update_script(
            script.id,
            ScriptUpdate(scenes=[{"scene_number": 1, "visual_content": "changed"}]),
        )
    except RuntimeError:
        pass
    monkeypatch.setattr(service.repository, "flush", original_flush)
    db_session.expire_all()
    restored = service.get_script(script.id)
    assert [scene.visual_content for scene in restored.scenes] == ["original"]
