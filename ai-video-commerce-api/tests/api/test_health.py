def test_liveness_is_independent_from_database(client):
    response = client.get("/health/live")
    assert response.status_code == 200
    assert response.json()["data"]["status"] == "live"


def test_readiness_probes_isolated_database(client):
    response = client.get("/health/ready")
    assert response.status_code == 200
    assert response.json()["data"]["status"] == "ready"
