# Custom FastAPI Blog & Portfolio Engine

This repository contains the source code for [grishuk.co.il](https://grishuk.co.il).
This project implements a Server-Side Rendered (SSR) blog and portfolio system using **FastAPI** and **SQLAlchemy**. It avoids heavy frontend frameworks in favor of raw performance and simplicity, serving Jinja2 templates directly from the backend.

## Technical Overview

* **Framework:** FastAPI (mounted with Gunicorn/Uvicorn for production).
* **Database:** PostgreSQL with SQLAlchemy ORM and Alembic for migrations.
* **Rendering:** Server-side Jinja2 templating.
* **Content:** Markdown-based content ingestion via `mistune` with custom renderers for security hardening (e.g., `noopener` injection).
* **Management:** Custom CLI (`site_utils/manage_content.py`) for maintaining posts and projects without a GUI admin interface.

## Project Structure

```text
.
├── main.py                 # App entry point, middleware, and routing
├── db_utils/               # Database models and session logic
├── site_utils/             # CLI tools for content management
├── templates/              # Jinja2 HTML templates
└── static/                 # Assets
```

## Setup & Running

Requires Python 3.9+ and a PostgreSQL instance.

1. Install dependencies:

```sh
pip install -r requirements.txt
```

2. Environment: Create a `.env` file:

```yaml
DATABASE_URL=postgresql://user:pass@localhost/dbname
```

3. Migrations:

```sh
alembic upgrade head
```

4. Run:

```
# Development
uvicorn main:app --reload

# Production
gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app
```

## CLI Usage

The project includes a utility script to manage database content from local Markdown files.

```sh
# Add a new post
python site_utils/manage_content.py --post --add

# Modify an existing project
python site_utils/manage_content.py --post --modify
```
