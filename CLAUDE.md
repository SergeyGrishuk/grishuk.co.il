# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

SSR blog and portfolio site for [grishuk.co.il](https://grishuk.co.il). FastAPI serves Jinja2 templates directly — no frontend framework.

## Commands

```sh
# Install dependencies
pip install -r requirements.txt

# Run dev server
uvicorn main:app --reload

# Run production server
gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app

# Database migrations
alembic upgrade head                    # apply all migrations
alembic revision --autogenerate -m "description"  # create new migration

# Content management (interactive CLI, requires DB connection)
python site_utils/manage_content.py --post --add
python site_utils/manage_content.py --post --modify
python site_utils/manage_content.py --post --delete

# Sitemap generation
python site_utils/sitemap_generator.py https://grishuk.co.il
```

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

## Environment

Requires a `.env` file with:
```
DATABASE_URL=postgresql://user:pass@localhost/dbname
```

Python 3.9+, PostgreSQL.
