import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'app'))

from app import app as flask_app


@pytest.fixture
def client():
    flask_app.config["TESTING"] = True
    with flask_app.test_client() as client:
        yield client


def test_home_returns_200(client):
    res = client.get("/")
    assert res.status_code == 200
    data = res.get_json()
    assert data["service"] == "migration-arc-app"
    assert data["status"] == "running"


def test_health_endpoint(client):
    res = client.get("/health")
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "healthy"
    assert "timestamp" in data


def test_info_endpoint(client):
    res = client.get("/info")
    assert res.status_code == 200
    data = res.get_json()
    assert "hostname" in data
    assert "python_version" in data
    assert data["app_version"] == "1.0.0"


def test_ping_endpoint(client):
    res = client.get("/ping")
    assert res.status_code == 200
    assert res.get_json()["pong"] is True


def test_custom_metrics_endpoint(client):
    res = client.get("/metrics/custom")
    assert res.status_code == 200
    data = res.get_json()
    assert "requests_total" in data
    assert "environment" in data
