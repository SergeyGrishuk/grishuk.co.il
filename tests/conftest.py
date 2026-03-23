import os

# Set DATABASE_URL before any app imports so db_utils.database picks it up
os.environ.setdefault("DATABASE_URL", "sqlite:///")
os.environ.setdefault("SESSION_SECRET_KEY", "test-secret-key-not-for-production")

import pytest
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from httpx import ASGITransport, AsyncClient

from db_utils.database import Base
import db_utils.database as db_mod
from db_utils.models import Post, Tag, AdminUser

import bcrypt


# In-memory SQLite engine shared across a test session
engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

# Enable foreign keys for SQLite
@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(autouse=True)
def setup_database():
    """Create all tables before each test, drop after."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def db():
    """Provide a transactional database session for tests."""
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


def _override_get_db():
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture()
def client():
    """Synchronous-style test client using httpx."""
    from main import app, get_db
    from admin.auth import get_db as auth_get_db, limiter
    from admin.routes import get_db as routes_get_db

    app.dependency_overrides[get_db] = _override_get_db
    app.dependency_overrides[auth_get_db] = _override_get_db
    app.dependency_overrides[routes_get_db] = _override_get_db

    # Reset rate limiter storage so tests don't interfere with each other
    limiter.reset()

    from starlette.testclient import TestClient
    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()


@pytest.fixture()
def sample_post(db):
    """Insert a sample post and return it."""
    post = Post(
        title="Test Post",
        slug="test-post",
        summary="A test summary",
        post_content="# Hello\n\nThis is **bold** text.",
    )
    db.add(post)
    db.commit()
    db.refresh(post)
    return post


@pytest.fixture()
def sample_tag(db):
    """Insert a sample tag and return it."""
    tag = Tag(name="python")
    db.add(tag)
    db.commit()
    db.refresh(tag)
    return tag


@pytest.fixture()
def admin_user(db):
    """Insert an admin user with password 'testpass123'."""
    pw_hash = bcrypt.hashpw(b"testpass123", bcrypt.gensalt()).decode()
    user = AdminUser(username="admin", password_hash=pw_hash)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture()
def admin_client(client, admin_user):
    """A test client already logged in as admin."""
    # Get login page to obtain CSRF token
    resp = client.get("/admin/login")
    assert resp.status_code == 200

    # Extract CSRF token from session
    csrf_token = client.cookies.get("admin_session")

    # Login via form submission
    resp = client.post(
        "/admin/login",
        data={
            "username": "admin",
            "password": "testpass123",
            "csrf_token": _get_csrf_from_response(resp),
        },
        follow_redirects=False,
    )
    assert resp.status_code == 303
    return client


def _get_csrf_from_response(response):
    """Extract CSRF token from a form response."""
    import re
    match = re.search(r'name="csrf_token"\s+value="([^"]+)"', response.text)
    if match:
        return match.group(1)
    # Try hidden input variant
    match = re.search(r'value="([^"]+)"\s+name="csrf_token"', response.text)
    if match:
        return match.group(1)
    raise ValueError("CSRF token not found in response")
