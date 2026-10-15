
import os
import urllib.request
import json


def test_tasks_api_integration():
    base_url = os.environ.get(
        "API_BASE_URL",
        "http://localhost:5002"
    )

    with urllib.request.urlopen(
        f"{base_url}/tasks",
        timeout=10
    ) as response:
        assert response.status == 200

        data = json.load(response)

    assert isinstance(data, list)
