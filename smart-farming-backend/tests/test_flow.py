def _register_and_login(client, email="farmer@example.com", password="testpass123"):
    client.post("/auth/register", json={"name": "Test Farmer", "email": email, "password": password})
    resp = client.post("/auth/login", data={"username": email, "password": password})
    assert resp.status_code == 200
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_full_flow(client):
    headers = _register_and_login(client)

    # create farm
    resp = client.post("/farms", json={"name": "Green Valley", "location": "Punjab"}, headers=headers)
    assert resp.status_code == 201
    farm_id = resp.json()["id"]

    # create device
    resp = client.post(
        f"/farms/{farm_id}/devices", json={"name": "Node A", "type": "esp32"}, headers=headers
    )
    assert resp.status_code == 201
    device = resp.json()
    api_key = device["api_key"]

    # simulate sensor ingest (no auth header, uses api_key instead)
    resp = client.post(
        "/sensors/ingest",
        json={"api_key": api_key, "sensor_type": "moisture", "value": 25.0, "unit": "%"},
    )
    assert resp.status_code == 201

    # low moisture (< 30) should have created an alert
    resp = client.get(f"/alerts?farm_id={farm_id}", headers=headers)
    assert resp.status_code == 200
    alerts = resp.json()
    assert len(alerts) == 1
    assert alerts[0]["type"] == "moisture_threshold"

    # latest readings
    resp = client.get(f"/sensors/{device['id']}/latest", headers=headers)
    assert resp.status_code == 200
    assert resp.json()[0]["sensor_type"] == "moisture"
