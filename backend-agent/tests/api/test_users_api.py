def test_create_user_api_success(client):
    resp = client.post(
        "/api/v1/users",
        json={"username": "bob", "email": "bob@example.com"},
    )

    assert resp.status_code == 201
    body = resp.json()
    assert body["code"] == 0
    assert body["data"]["username"] == "bob"


def test_get_user_api_success(client):
    created = client.post(
        "/api/v1/users",
        json={"username": "alice", "email": "alice@example.com"},
    )
    user_id = created.json()["data"]["id"]

    resp = client.get(f"/api/v1/users/{user_id}")
    assert resp.status_code == 200
    assert resp.json()["data"]["email"] == "alice@example.com"


def test_create_user_duplicate_returns_business_error(client):
    payload = {"username": "bob", "email": "bob@example.com"}

    first = client.post("/api/v1/users", json=payload)
    second = client.post("/api/v1/users", json=payload)

    assert first.status_code == 201
    assert second.status_code == 400
    body = second.json()
    assert body["code"] == 4002
    assert body["request_id"] is not None


def test_get_user_not_found_returns_business_error(client):
    resp = client.get("/api/v1/users/999")

    assert resp.status_code == 400
    body = resp.json()
    assert body["code"] == 4004
    assert body["message"] == "user not found"


def test_create_user_invalid_payload_returns_unified_422(client):
    resp = client.post(
        "/api/v1/users",
        json={"username": "a", "email": "not-an-email"},
    )

    assert resp.status_code == 422
    body = resp.json()
    assert body["code"] == 4220
    assert body["message"] == "Validation Error"
    assert isinstance(body["data"]["errors"], list)
