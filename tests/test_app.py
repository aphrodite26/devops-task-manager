from app import app


def test_health():
    client = app.test_client()

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json["status"] == "healthy"
    
    
def test_get_tasks():
    client = app.test_client()
    response = client.get("/tasks")

    assert response.status_code == 200
    assert isinstance(response.json, list)
    assert len(response.json) == 3


def test_home():
    client = app.test_client()
    response = client.get("/")

    assert response.status_code == 200
    assert response.json["application"] == "DevOps Task Manager"
    assert response.json["status"] == "running"