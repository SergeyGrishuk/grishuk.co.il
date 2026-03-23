"""Tests for admin authentication."""
import re


def _get_csrf(response):
    match = re.search(r'name="csrf_token"\s+value="([^"]+)"', response.text)
    if match:
        return match.group(1)
    match = re.search(r'value="([^"]+)"\s+name="csrf_token"', response.text)
    if match:
        return match.group(1)
    raise ValueError("CSRF token not found")


class TestLogin:
    def test_login_page_returns_200(self, client):
        resp = client.get("/admin/login")
        assert resp.status_code == 200
        assert "csrf_token" in resp.text

    def test_successful_login_redirects(self, client, admin_user):
        resp = client.get("/admin/login")
        csrf = _get_csrf(resp)

        resp = client.post(
            "/admin/login",
            data={"username": "admin", "password": "testpass123", "csrf_token": csrf},
            follow_redirects=False,
        )
        assert resp.status_code == 303
        assert resp.headers["location"] == "/admin/"

    def test_wrong_password_shows_error(self, client, admin_user):
        resp = client.get("/admin/login")
        csrf = _get_csrf(resp)

        resp = client.post(
            "/admin/login",
            data={"username": "admin", "password": "wrong", "csrf_token": csrf},
        )
        assert resp.status_code == 200
        assert "Invalid username or password" in resp.text

    def test_wrong_username_shows_error(self, client, admin_user):
        resp = client.get("/admin/login")
        csrf = _get_csrf(resp)

        resp = client.post(
            "/admin/login",
            data={"username": "nobody", "password": "testpass123", "csrf_token": csrf},
        )
        assert resp.status_code == 200
        assert "Invalid username or password" in resp.text

    def test_invalid_csrf_shows_error(self, client, admin_user):
        resp = client.post(
            "/admin/login",
            data={"username": "admin", "password": "testpass123", "csrf_token": "bad-token"},
        )
        assert resp.status_code == 200
        assert "Invalid request" in resp.text


class TestLogout:
    def test_logout_redirects_to_login(self, admin_client):
        resp = admin_client.get("/admin/logout", follow_redirects=False)
        assert resp.status_code == 303
        assert "login" in resp.headers["location"]


class TestRequireAdmin:
    def test_dashboard_redirects_when_not_logged_in(self, client):
        resp = client.get("/admin/", follow_redirects=False)
        assert resp.status_code == 303
        assert "login" in resp.headers["location"]

    def test_dashboard_accessible_when_logged_in(self, admin_client):
        resp = admin_client.get("/admin/")
        assert resp.status_code == 200
