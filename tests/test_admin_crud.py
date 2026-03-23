"""Tests for admin CRUD operations on posts and tags."""
import re

from db_utils.models import Post, Tag


def _get_csrf(response):
    match = re.search(r'name="csrf_token"\s+value="([^"]+)"', response.text)
    if match:
        return match.group(1)
    match = re.search(r'value="([^"]+)"\s+name="csrf_token"', response.text)
    if match:
        return match.group(1)
    raise ValueError("CSRF token not found")


class TestAdminPosts:
    def test_new_post_form_loads(self, admin_client):
        resp = admin_client.get("/admin/posts/new")
        assert resp.status_code == 200
        assert "csrf_token" in resp.text

    def test_create_post(self, admin_client, db):
        resp = admin_client.get("/admin/posts/new")
        csrf = _get_csrf(resp)

        resp = admin_client.post(
            "/admin/posts/new",
            data={
                "title": "New Post",
                "meta_title": "",
                "slug": "",
                "summary": "A summary",
                "tags_input": "python,testing",
                "post_content": "# Content\nBody text",
                "publish_date": "",
                "csrf_token": csrf,
            },
            follow_redirects=False,
        )
        assert resp.status_code == 303

        post = db.query(Post).filter(Post.slug == "new-post").first()
        assert post is not None
        assert post.title == "New Post"
        assert len(post.tags) == 2

    def test_create_post_with_custom_slug(self, admin_client, db):
        resp = admin_client.get("/admin/posts/new")
        csrf = _get_csrf(resp)

        admin_client.post(
            "/admin/posts/new",
            data={
                "title": "My Post",
                "meta_title": "",
                "slug": "custom-slug",
                "summary": "S",
                "tags_input": "",
                "post_content": "C",
                "publish_date": "",
                "csrf_token": csrf,
            },
            follow_redirects=False,
        )

        post = db.query(Post).filter(Post.slug == "custom-slug").first()
        assert post is not None

    def test_edit_post_form_loads(self, admin_client, sample_post):
        resp = admin_client.get(f"/admin/posts/{sample_post.id}/edit")
        assert resp.status_code == 200
        assert "Test Post" in resp.text

    def test_edit_post_form_nonexistent_redirects(self, admin_client):
        resp = admin_client.get("/admin/posts/9999/edit", follow_redirects=False)
        assert resp.status_code == 303

    def test_update_post(self, admin_client, sample_post, db):
        resp = admin_client.get(f"/admin/posts/{sample_post.id}/edit")
        csrf = _get_csrf(resp)

        resp = admin_client.post(
            f"/admin/posts/{sample_post.id}/edit",
            data={
                "title": "Updated Title",
                "meta_title": "Meta",
                "slug": "test-post",
                "summary": "Updated summary",
                "tags_input": "",
                "post_content": "Updated content",
                "publish_date": "",
                "csrf_token": csrf,
            },
            follow_redirects=False,
        )
        assert resp.status_code == 303

        db.refresh(sample_post)
        assert sample_post.title == "Updated Title"

    def test_delete_post(self, admin_client, sample_post, db):
        resp = admin_client.get("/admin/")
        csrf = _get_csrf(resp)

        resp = admin_client.post(
            f"/admin/posts/{sample_post.id}/delete",
            data={"csrf_token": csrf},
            follow_redirects=False,
        )
        assert resp.status_code == 303

        assert db.query(Post).filter(Post.id == sample_post.id).first() is None


class TestAdminTags:
    def test_tags_page_loads(self, admin_client):
        resp = admin_client.get("/admin/tags")
        assert resp.status_code == 200

    def test_rename_tag(self, admin_client, sample_tag, db):
        resp = admin_client.get("/admin/tags")
        csrf = _get_csrf(resp)

        resp = admin_client.post(
            f"/admin/tags/{sample_tag.id}/rename",
            data={"name": "renamed-tag", "csrf_token": csrf},
            follow_redirects=False,
        )
        assert resp.status_code == 303

        db.refresh(sample_tag)
        assert sample_tag.name == "renamed-tag"

    def test_delete_tag(self, admin_client, sample_tag, db):
        resp = admin_client.get("/admin/tags")
        csrf = _get_csrf(resp)

        resp = admin_client.post(
            f"/admin/tags/{sample_tag.id}/delete",
            data={"csrf_token": csrf},
            follow_redirects=False,
        )
        assert resp.status_code == 303

        assert db.query(Tag).filter(Tag.id == sample_tag.id).first() is None

    def test_cleanup_removes_orphaned_tags(self, admin_client, sample_tag, db):
        # sample_tag has no posts, so it's orphaned
        resp = admin_client.get("/admin/tags")
        csrf = _get_csrf(resp)

        resp = admin_client.post(
            "/admin/tags/cleanup",
            data={"csrf_token": csrf},
            follow_redirects=False,
        )
        assert resp.status_code == 303

        assert db.query(Tag).filter(Tag.id == sample_tag.id).first() is None
