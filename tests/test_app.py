
from unittest.mock import MagicMock, patch
from app import app


def test_health():
    client = app.test_client()

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json == {"status": "healthy"}


def test_home():
    client = app.test_client()

    response = client.get("/")

    assert response.status_code == 200
    assert response.get_json() == {
        "application": "DevOps Task Manager",
        "status": "running",
        "version": "2.1"
    }


@patch("app.get_db_connection")
def test_get_tasks(mock_connection):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()

    mock_connection.return_value.__enter__.return_value = mock_conn
    mock_conn.cursor.return_value.__enter__.return_value = mock_cursor

    mock_cursor.fetchall.return_value = [
        {"id": 1, "title": "Configure Docker", "completed": True},
        {"id": 2, "title": "Write automated tests", "completed": False},
        {"id": 3, "title": "Set up CI/CD pipeline", "completed": False}
    ]

    client = app.test_client()
    response = client.get("/tasks")

    assert response.status_code == 200
    assert len(response.json) == 3
    assert response.json[0]["title"] == "Configure Docker"
    assert response.json[0]["completed"] is True
