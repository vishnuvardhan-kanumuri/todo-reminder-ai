def test_health_endpoint(client):
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json()["status"] == "ok"
    assert res.json()["ai_enabled"] is False


def test_create_and_list_task(client):
    res = client.post("/api/tasks", json={"title": "Read a book"})
    assert res.status_code == 201
    task = res.json()
    assert task["title"] == "Read a book"
    assert task["status"] == "pending"

    res = client.get("/api/tasks")
    assert res.status_code == 200
    assert len(res.json()) == 1


def test_get_missing_task_404(client):
    res = client.get("/api/tasks/999")
    assert res.status_code == 404


def test_update_task(client):
    task = client.post("/api/tasks", json={"title": "Draft"}).json()
    res = client.patch(f"/api/tasks/{task['id']}", json={"priority": "high"})
    assert res.status_code == 200
    assert res.json()["priority"] == "high"


def test_complete_and_delete_task(client):
    task = client.post("/api/tasks", json={"title": "One-off"}).json()

    res = client.post(f"/api/tasks/{task['id']}/complete")
    assert res.status_code == 200
    assert res.json()["status"] == "completed"

    res = client.delete(f"/api/tasks/{task['id']}")
    assert res.status_code == 204

    res = client.get(f"/api/tasks/{task['id']}")
    assert res.status_code == 404


def test_snooze_task(client):
    task = client.post("/api/tasks", json={"title": "Call bank"}).json()
    res = client.post(f"/api/tasks/{task['id']}/snooze", json={"until": "2026-08-01T00:00:00Z"})
    assert res.status_code == 200
    assert res.json()["snooze_count"] == 1


def test_category_crud(client):
    res = client.post("/api/categories", json={"name": "Work", "color": "#ff0000"})
    assert res.status_code == 201
    category = res.json()

    res = client.get("/api/categories")
    assert len(res.json()) == 1

    res = client.delete(f"/api/categories/{category['id']}")
    assert res.status_code == 204

    res = client.get("/api/categories")
    assert len(res.json()) == 0


def test_parse_endpoint_503_without_api_key(client):
    res = client.post("/api/tasks/parse", json={"text": "buy milk tomorrow"})
    assert res.status_code == 503


def test_categorize_endpoint_503_without_api_key(client):
    task = client.post("/api/tasks", json={"title": "Something"}).json()
    res = client.post(f"/api/tasks/{task['id']}/categorize")
    assert res.status_code == 503


def test_task_with_category_and_tags(client):
    category = client.post("/api/categories", json={"name": "Errands"}).json()
    res = client.post(
        "/api/tasks",
        json={
            "title": "Grocery run",
            "category_id": category["id"],
            "tags": ["urgent", "outdoors"],
        },
    )
    assert res.status_code == 201
    task = res.json()
    assert task["category_id"] == category["id"]
    assert task["tags"] == ["urgent", "outdoors"]
