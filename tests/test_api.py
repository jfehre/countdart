import os

import pytest
from fastapi import FastAPI
from starlette.testclient import TestClient

# set environment before importing settings
os.environ.setdefault("MONGO_DB_DATABASE", "pytest")

from countdart.api import router  # noqa: E402
from countdart.database.db import client, database  # noqa: E402
from countdart.settings import settings  # noqa: E402

api_url = "/api/v1"


def setup_module():
    """runs at the beginning"""
    pass


def teardown_module():
    client.drop_database(database)


@pytest.fixture
def app():
    settings.MONGO_DB_DATABASE = "pytest"

    app = FastAPI(
        title="Count Dart",
        openapi_url=f"{settings.API_V1_STR}/openapi.json",
        docs_url=f"{settings.API_V1_STR}/docs",
        redoc_url=f"{settings.API_V1_STR}/redoc",
    )

    app.include_router(router)
    return app


@pytest.fixture
def test_client(app):
    """Create testclient"""
    return TestClient(app=app)


def test_create_dartboard(test_client):
    """Test create dartboard"""
    response = test_client.post(
        f"{api_url}/dartboards",
        json={"name": "Test Dartboard", "active": True},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Dartboard"
    assert "id" in data
    return data["id"]


def test_read_dartboard(test_client):
    """Test read dartboard"""
    id = test_create_dartboard(test_client)
    response = test_client.get(f"{api_url}/dartboards/{id}")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Dartboard"
    assert data["id"] == id


def test_update_dartboard(test_client):
    """Test update dartboard"""
    id = test_create_dartboard(test_client)
    response = test_client.patch(
        f"{api_url}/dartboards/{id}",
        json={"name": "Updated Test Dartboard"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Test Dartboard"
    assert data["id"] == id


def test_delete_dartboard(test_client):
    """Test delete dartboard"""
    id = test_create_dartboard(test_client)
    response = test_client.delete(f"{api_url}/dartboards/{id}")
    assert response.status_code == 200


def test_create_cam(test_client):
    """Test create cam"""
    response = test_client.post(
        f"{api_url}/cams",
        json={"card_name": "Test Cam", "active": False, "hardware_id": 0},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["card_name"] == "Test Cam"
    assert data["active"] is False
    assert "id" in data
    return data["id"]


def test_read_cam(test_client):
    """Test read cam"""
    id = test_create_cam(test_client)
    response = test_client.get(f"{api_url}/cams/{id}")
    assert response.status_code == 200
    data = response.json()
    assert data["card_name"] == "Test Cam"
    assert data["active"] is False
    assert data["id"] == id


def test_update_cam(test_client):
    """Test update cam"""
    id = test_create_cam(test_client)
    response = test_client.patch(
        f"{api_url}/cams/{id}",
        json={"card_name": "Updated Test Cam", "active": True},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["card_name"] == "Updated Test Cam"
    assert data["active"] is True
    assert data["id"] == id


def test_delete_cam(test_client):
    """Test delete cam"""
    id = test_create_cam(test_client)
    response = test_client.delete(f"{api_url}/cams/{id}")
    assert response.status_code == 200
