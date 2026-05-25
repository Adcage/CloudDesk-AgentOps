def test_request_id_and_process_time_headers_exist(client):
    resp = client.get("/api/v1/health")

    assert "X-Request-ID" in resp.headers
    assert "X-Process-Time" in resp.headers
    assert resp.json()["request_id"] == resp.headers["X-Request-ID"]
