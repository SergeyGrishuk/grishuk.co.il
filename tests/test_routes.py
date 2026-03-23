"""Tests for public-facing routes."""
from db_utils.models import Post


class TestHomePage:
    def test_home_returns_200(self, client):
        resp = client.get("/")
        assert resp.status_code == 200

    def test_home_lists_posts(self, client, sample_post):
        resp = client.get("/")
        assert resp.status_code == 200
        assert "Test Post" in resp.text


class TestPostPage:
    def test_existing_post_returns_200(self, client, sample_post):
        resp = client.get("/posts/test-post")
        assert resp.status_code == 200
        assert "Test Post" in resp.text

    def test_post_renders_markdown(self, client, sample_post):
        resp = client.get("/posts/test-post")
        assert "<strong>bold</strong>" in resp.text

    def test_missing_post_returns_404(self, client):
        resp = client.get("/posts/nonexistent-slug")
        assert resp.status_code == 404

    def test_post_with_meta_title(self, client, db):
        post = Post(
            title="Long Title",
            meta_title="Short",
            slug="meta-test",
            summary="S",
            post_content="Content",
        )
        db.add(post)
        db.commit()
        resp = client.get("/posts/meta-test")
        assert resp.status_code == 200


class TestRobotsTxt:
    def test_robots_txt_returns_200(self, client):
        resp = client.get("/robots.txt")
        assert resp.status_code == 200
        assert "User-agent: *" in resp.text
        assert "Disallow: /admin" in resp.text


class TestExamplesPage:
    def test_existing_example_returns_200(self, client):
        resp = client.get("/examples/cpu_and_memory.html")
        assert resp.status_code == 200

    def test_missing_example_returns_404(self, client):
        resp = client.get("/examples/nonexistent.html")
        assert resp.status_code == 404


class TestRSSFeed:
    def test_feed_returns_200_with_xml(self, client):
        resp = client.get("/feed.xml")
        assert resp.status_code == 200
        assert "application/rss+xml" in resp.headers["content-type"]
        assert '<?xml version="1.0"' in resp.text

    def test_feed_contains_post(self, client, sample_post):
        # Clear RSS cache so the new post appears
        from main import _rss_cache
        _rss_cache["xml"] = None
        _rss_cache["timestamp"] = 0.0

        resp = client.get("/feed.xml")
        assert resp.status_code == 200
        assert "Test Post" in resp.text
        assert "/posts/test-post" in resp.text
        assert "A test summary" in resp.text

    def test_feed_is_valid_rss2(self, client):
        import xml.etree.ElementTree as ET
        resp = client.get("/feed.xml")
        root = ET.fromstring(resp.text)
        assert root.tag == "rss"
        assert root.attrib["version"] == "2.0"
        channel = root.find("channel")
        assert channel is not None
        assert channel.find("title").text == "grishuk.co.il"


class Test404Handler:
    def test_unknown_route_returns_404(self, client):
        resp = client.get("/this-does-not-exist")
        assert resp.status_code == 404
