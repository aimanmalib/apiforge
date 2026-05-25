"""Tests for web dashboard API endpoints."""
import pytest

class TestWebHealth:
    def test_health_endpoint(self):
        from fastapi.testclient import TestClient
        from web.app import app
        client = TestClient(app)
        resp = client.get("/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "ok"
        assert data["service"] == "apiforge"

class TestWebModels:
    def test_list_models(self):
        from fastapi.testclient import TestClient
        from web.app import app
        client = TestClient(app)
        resp = client.get("/api/models")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["models"]) > 0
        assert data["default"] == "mimo-v2.5-pro"

class TestWebFrameworks:
    def test_list_frameworks(self):
        from fastapi.testclient import TestClient
        from web.app import app
        client = TestClient(app)
        resp = client.get("/api/frameworks")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["frameworks"]) > 0

class TestWebTokens:
    def test_token_stats(self):
        from fastapi.testclient import TestClient
        from web.app import app
        client = TestClient(app)
        resp = client.get("/api/tokens")
        assert resp.status_code == 200

    def test_daily_estimates(self):
        from fastapi.testclient import TestClient
        from web.app import app
        client = TestClient(app)
        resp = client.get("/api/tokens/daily")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total_daily"] > 0

class TestWebJobs:
    def test_list_jobs_empty(self):
        from fastapi.testclient import TestClient
        from web.app import app
        client = TestClient(app)
        resp = client.get("/api/jobs")
        assert resp.status_code == 200

    def test_job_not_found(self):
        from fastapi.testclient import TestClient
        from web.app import app
        client = TestClient(app)
        resp = client.get("/api/jobs/nonexistent")
        assert resp.status_code == 404

class TestWebIndex:
    def test_index_page(self):
        from fastapi.testclient import TestClient
        from web.app import app
        client = TestClient(app)
        resp = client.get("/")
        assert resp.status_code == 200
