def test_liveness(client):
    response = client.get("/health/live")
    assert response.status_code == 200
    assert response.get_json()["status"] == "alive"


def test_readiness(client):
    response = client.get("/health/ready")
    assert response.status_code == 200
    assert response.get_json()["database"] == "connected"


def test_index(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.get_json()["status"] == "running"
