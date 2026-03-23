"""Tests for SQLAlchemy models."""
from db_utils.models import Post, Tag, AdminUser


class TestPostModel:
    def test_create_post(self, db):
        post = Post(title="Title", slug="title", summary="S", post_content="C")
        db.add(post)
        db.commit()
        db.refresh(post)

        assert post.id is not None
        assert post.title == "Title"
        assert post.slug == "title"

    def test_post_tag_relationship(self, db):
        tag = Tag(name="test-tag")
        post = Post(title="T", slug="s", summary="S", post_content="C", tags=[tag])
        db.add(post)
        db.commit()
        db.refresh(post)

        assert len(post.tags) == 1
        assert post.tags[0].name == "test-tag"

    def test_post_multiple_tags(self, db):
        tags = [Tag(name="a"), Tag(name="b"), Tag(name="c")]
        post = Post(title="T", slug="s", summary="S", post_content="C", tags=tags)
        db.add(post)
        db.commit()
        db.refresh(post)

        assert len(post.tags) == 3

    def test_post_optional_meta_title(self, db):
        post = Post(title="T", slug="s", summary="S", post_content="C", meta_title=None)
        db.add(post)
        db.commit()
        db.refresh(post)

        assert post.meta_title is None


class TestTagModel:
    def test_create_tag(self, db):
        tag = Tag(name="python")
        db.add(tag)
        db.commit()
        db.refresh(tag)

        assert tag.id is not None
        assert tag.name == "python"
        assert str(tag) == "python"

    def test_tag_posts_relationship(self, db):
        tag = Tag(name="test")
        post = Post(title="T", slug="s", summary="S", post_content="C", tags=[tag])
        db.add(post)
        db.commit()
        db.refresh(tag)

        assert len(tag.posts) == 1


class TestAdminUserModel:
    def test_create_admin_user(self, db):
        user = AdminUser(username="admin", password_hash="hashed_pw")
        db.add(user)
        db.commit()
        db.refresh(user)

        assert user.id is not None
        assert user.username == "admin"
