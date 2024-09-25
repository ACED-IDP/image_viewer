def test_health_check(client):
    response = client.get("/_health")
    assert response.status_code == 200
    assert response.json() == {"status": "OK"}


def test_openapi_endpoint(client):
    response = client.get("/openapi.json")
    assert response.status_code == 200
    assert "openapi" in response.json()


def test_swagger_ui(client):
    response = client.get("/docs")
    assert response.status_code == 200
    assert "swagger-ui" in response.text.lower()
