"""Tests for slug generation utilities."""
from admin.routes import slugify, ensure_unique_slug
from db_utils.models import Post


class TestSlugify:
    def test_basic_text(self):
        assert slugify("Hello World") == "hello-world"

    def test_special_characters_removed(self):
        assert slugify("What's New?") == "whats-new"

    def test_underscores_become_dashes(self):
        assert slugify("hello_world") == "hello-world"

    def test_multiple_spaces_collapsed(self):
        assert slugify("hello   world") == "hello-world"

    def test_uppercase_lowered(self):
        assert slugify("HELLO") == "hello"

    def test_empty_string(self):
        assert slugify("") == ""

    def test_numbers_preserved(self):
        assert slugify("Python 3.9") == "python-39"

    def test_mixed_special_chars(self):
        assert slugify("Hello & World! #1") == "hello--world-1"


class TestEnsureUniqueSlug:
    def test_unique_slug_returned_as_is(self, db):
        assert ensure_unique_slug(db, "my-post") == "my-post"

    def test_duplicate_slug_gets_suffix(self, db):
        post = Post(title="T", slug="my-post", summary="S", post_content="C")
        db.add(post)
        db.commit()

        assert ensure_unique_slug(db, "my-post") == "my-post-2"

    def test_multiple_duplicates_increment(self, db):
        for slug in ["my-post", "my-post-2"]:
            db.add(Post(title="T", slug=slug, summary="S", post_content="C"))
        db.commit()

        assert ensure_unique_slug(db, "my-post") == "my-post-3"

    def test_exclude_post_id_allows_same_slug(self, db):
        post = Post(title="T", slug="my-post", summary="S", post_content="C")
        db.add(post)
        db.commit()
        db.refresh(post)

        assert ensure_unique_slug(db, "my-post", exclude_post_id=post.id) == "my-post"
