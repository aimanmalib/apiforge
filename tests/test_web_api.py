"""Tests for web dashboard API endpoints."""


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
        assert data["provider"] == "openai"
        assert data["default"] == "gpt-4o-mini"

    def test_list_models_follows_config(self, monkeypatch):
        from fastapi.testclient import TestClient
        from web.app import app

        monkeypatch.setenv("APIFORGE_PROVIDER", "openrouter")
        monkeypatch.setenv("APIFORGE_MODEL", "some/model")
        resp = TestClient(app).get("/api/models")
        assert resp.json()["provider"] == "openrouter"
        assert resp.json()["default"] == "some/model"


class TestWebStatic:
    def test_stylesheet_is_served(self):
        from fastapi.testclient import TestClient
        from web.app import app

        resp = TestClient(app).get("/static/style.css")
        assert resp.status_code == 200
        assert "text/css" in resp.headers["content-type"]


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
