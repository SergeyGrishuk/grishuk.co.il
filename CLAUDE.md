# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

SSR blog and portfolio site for [grishuk.co.il](https://grishuk.co.il).

## Architecture

**Entry point:** `main.py` — defines the FastAPI app, middleware, routes, and a custom `mistune` Markdown renderer (`CustomRenderer`) that adds `target="_blank"` and `rel="noopener noreferrer"` to links. The Markdown processor is registered as a Jinja2 filter (`markdown`).

**Database layer (`db_utils/`):**
- `database.py` — SQLAlchemy engine and `SessionLocal` factory. Reads `DATABASE_URL` from environment.
- `models.py` — Three models: `Post`, `Project` (currently unused/dropped), `Tag`. Posts and projects relate to tags via many-to-many join tables (`post_tags`, `project_tags`).

**Alembic (`alembic/`):** `env.py` loads `DATABASE_URL` from `.env` via `dotenv`. The `sqlalchemy.url` in `alembic.ini` is overridden at runtime.

**Routes:**
- `GET /` — home page listing all posts
- `GET /posts/{post_slug}` — single post page, renders Markdown `post_content` to HTML
- `GET /examples/{page_name}` — serves static HTML example pages from `templates/examples/`

**Templates (`templates/`):** Jinja2 templates extending `base.html`. Post content is stored as Markdown in the DB and rendered at request time.

**Content pipeline:** Post body text is stored as raw Markdown in the `posts.post_content` column. Source Markdown files live in `markdown_content/` and are read by `manage_content.py` during the interactive add flow.

## Admin Panel

Web-based admin at `/admin/` for managing posts and tags. Protected by bcrypt auth, session cookies, CSRF tokens, and rate limiting.

**Admin routes (`admin/`):**
- `admin/auth.py` — login/logout, CSRF helpers, `require_admin` dependency, slowapi rate limiter
- `admin/routes.py` — CRUD for posts and tags, slug generation, tag sync

**Key routes:**
- `GET /admin/` — dashboard (list posts)
- `GET/POST /admin/posts/new` — create post
- `GET/POST /admin/posts/{id}/edit` — edit post
- `POST /admin/posts/{id}/delete` — delete post
- `GET /admin/tags` — manage tags
- `POST /admin/tags/{id}/rename` — rename tag
- `POST /admin/tags/{id}/delete` — delete tag
- `POST /admin/tags/cleanup` — remove orphaned tags

```sh
# Create admin user (interactive, requires DB connection)
uv run python site_utils/create_admin.py
```

## Environment

Requires a `.env` file with:
```
DATABASE_URL=postgresql://user:pass@localhost/dbname
SESSION_SECRET_KEY=<random 64-char hex>
HTTPS_ONLY=true
```

Python 3.9+, PostgreSQL.
