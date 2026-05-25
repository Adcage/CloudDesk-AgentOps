def test_success_response_envelope(client):
    resp = client.get("/api/v1/health")
    body = resp.json()

    assert body["code"] == 0
    assert body["message"] == "OK"
    assert "data" in body
    assert "request_id" in body
