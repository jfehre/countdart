from fastapi.testclient import TestClient

from countdart.main import create_app

client = TestClient(create_app())

api_url = "/api/v1"


def test_create_dartboard():
    """Test create dartboard"""
    response = client.post(
        f"{api_url}/dartboards",
        json={"name": "Test Dartboard", "active": True},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Dartboard"
    assert "id" in data
    return data["id"]


def test_read_dartboard():
    """Test read dartboard"""
    id = test_create_dartboard()
    response = client.get(f"{api_url}/dartboards/{id}")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Dartboard"
    assert data["id"] == id


def test_update_dartboard():
    """Test update dartboard"""
    id = test_create_dartboard()
    response = client.patch(
        f"{api_url}/dartboards/{id}",
        json={"name": "Updated Test Dartboard"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Test Dartboard"
    assert data["id"] == id


def test_delete_dartboard():
    """Test delete dartboard"""
    id = test_create_dartboard()
    response = client.delete(f"{api_url}/dartboards/{id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == id


def test_create_cam():
    """Test create cam"""
    response = client.post(
        f"{api_url}/cams",
        json={"name": "Test Cam", "active": False},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Cam"
    assert data["active"] is False
    assert "id" in data
    return data["id"]


def test_read_cam():
    """Test read cam"""
    id = test_create_cam()
    response = client.get(f"{api_url}/cams/{id}")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Cam"
    assert data["active"] is False
    assert data["id"] == id


def test_update_cam():
    """Test update cam"""
    id = test_create_cam()
    response = client.patch(
        f"{api_url}/cams/{id}",
        json={"name": "Updated Test Cam", "active": True},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Test Cam"
    assert data["active"] is True
    assert data["id"] == id


def test_delete_cam():
    """Test delete cam"""
    id = test_create_cam()
    response = client.delete(f"{api_url}/cams/{id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == id
