#!/usr/bin/env python3


import os

import mistune

from pathlib import Path
from fastapi import FastAPI, Request, Depends, HTTPException
from mistune.renderers.html import HTMLRenderer
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.sessions import SessionMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from sqlalchemy.orm import Session

import db_utils.models as models
from db_utils.database import SessionLocal
from admin.auth import RequireLoginException, limiter, router as auth_router
from admin.routes import router as admin_router


class SchemeFixMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if "x-forwarded-proto" in request.headers:
            request.scope["scheme"] = request.headers["x-forwarded-proto"]

        response = await call_next(request)

        return response


app = FastAPI()

# Session middleware for admin panel
session_secret = os.getenv("SESSION_SECRET_KEY", "dev-secret-change-me")
https_only = os.getenv("HTTPS_ONLY", "false").lower() == "true"

app.add_middleware(
    SessionMiddleware,
    secret_key=session_secret,
    session_cookie="admin_session",
    max_age=3600,
    same_site="strict",
    https_only=https_only,
)
app.add_middleware(SchemeFixMiddleware)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Rate limiter
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

templates = Jinja2Templates(directory="templates")
app.state.templates = templates


BASE_DIR = Path(__file__).resolve().parent
TEMPLATE_DIR = BASE_DIR / "templates"


class CustomRenderer(HTMLRenderer):
    """
    Custom renderer to add target="_blank" and rel="noopener noreferrer" to external links.
    """

    def link(self, text, url, title=None):
        html = super().link(text, url, title)

        if url.startswith(("http://", "https://", "//")):
            return html.replace("<a href=", '<a target="_blank" rel="noopener noreferrer" href=', 1)

        return html.replace("<a href=", '<a target="_blank" href=', 1)


    def image(self, text, url, title = None):
        html = super().image(text, url, title = None)

        return html.replace('<img src="', '<img class="center-image" src="', 1)


markdown_processor = mistune.create_markdown(
    renderer=CustomRenderer()
)

templates.env.filters["markdown"] = markdown_processor


def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


@app.exception_handler(RequireLoginException)
async def require_login_handler(request: Request, exc: RequireLoginException):
    from starlette.responses import RedirectResponse
    return RedirectResponse(url="/admin/login", status_code=303)


@app.exception_handler(StarletteHTTPException)
async def not_found_exception_handler(request: Request, exc: StarletteHTTPException):
    if exc.status_code == 404:
        return templates.TemplateResponse("404.html", {"request": request}, status_code=404)

    return HTMLResponse(content=str(exc.detail), status_code=exc.status_code)


# Include admin routers
app.include_router(auth_router)
app.include_router(admin_router)


@app.get("/", response_class=HTMLResponse, name="root")
def root(request: Request, db: Session = Depends(get_db)):
    # projects = db.query(models.Project).order_by(models.Project.id.desc()).all()
    posts = db.query(models.Post).order_by(models.Post.id.desc()).all()

    return templates.TemplateResponse("home.html", {
        "request": request,
        # "projects": projects,
        "posts": posts
    })


@app.get("/posts/{post_slug}", response_class=HTMLResponse, name="show_post")
def show_post(request: Request, post_slug: str, db: Session = Depends(get_db)):
    post = db.query(models.Post).filter(models.Post.slug == post_slug).first()

    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    meta_title = post.meta_title or post.title
    html_content = markdown_processor(str(post.post_content))

    return templates.TemplateResponse(
        "post.html",
        {
            "request": request,
            "post": post,
            "html_content": html_content,
            "meta_title": meta_title
        }
    )


@app.get("/examples/{page_name}", response_class=HTMLResponse, name="show_example")
def show_example(request: Request, page_name: str):
    template_path = TEMPLATE_DIR / "examples" / page_name

    if not template_path.resolve().is_relative_to(TEMPLATE_DIR.resolve()):
        raise HTTPException(status_code=403, detail="Permission Denied")

    if not template_path.is_file():
        raise HTTPException(status_code=404, detail=f"Page {page_name} not found")

    return templates.TemplateResponse(f"examples/{page_name}", {"request": request})
