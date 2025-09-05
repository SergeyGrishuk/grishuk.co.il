#!/usr/bin/env python3


import mistune

from pathlib import Path
from fastapi import FastAPI, Request, Depends, HTTPException
from mistune.renderers.html import HTMLRenderer
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException
from sqlalchemy.orm import Session

import db_utils.models as models
from db_utils.database import SessionLocal


class SchemeFixMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if "x-forwarded-proto" in request.headers:
            request.scope["scheme"] = request.headers["x-forwarded-proto"]

        response = await call_next(request)

        return response


app = FastAPI()

app.add_middleware(SchemeFixMiddleware)
app.mount("/static", StaticFiles(directory="static"), name="static")


templates = Jinja2Templates(directory="templates")


BASE_DIR = Path(__file__).resolve().parent
TEMPLATE_DIR = BASE_DIR / "templates"


class CustomRenderer(HTMLRenderer):
    """
    Custom renderer to add target="_blank" and rel="noopener noreferrer" to external links.
    """

    def link(self, text, url, title=None):
        html = super().link(text, url, title)

        if url.startswith(('http://', 'https://', '//')):
            return html.replace('<a href=', '<a target="_blank" rel="noopener noreferrer" href=', 1)
        
        return html


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


@app.exception_handler(StarletteHTTPException)
async def not_found_exception_handler(request: Request, exc: StarletteHTTPException):
    if exc.status_code == 404:
        return templates.TemplateResponse("404.html", {"request": request}, status_code=404)
    
    return HTMLResponse(content=str(exc.detail), status_code=exc.status_code)


@app.get("/", response_class=HTMLResponse, name="root")
def root(request: Request, db: Session = Depends(get_db)):
    projects = db.query(models.Project).order_by(models.Project.id.desc()).all()
    posts = db.query(models.Post).order_by(models.Post.id.desc()).all()

    return templates.TemplateResponse("home.html", {
        "request": request,
        "projects": projects,
        "posts": posts
    })


@app.get("/posts/{post_html_page}", response_class=HTMLResponse, name="show_post")
def show_post(request: Request, post_html_page: str, db: Session = Depends(get_db)):
    try:
        post_id = int(post_html_page.split(".")[0])
    except ValueError:
        raise HTTPException(status_code=404, detail="Post not found")

    post = db.query(models.Post).filter(models.Post.id == post_id).first()

    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    html_content = markdown_processor(post.post_content)

    return templates.TemplateResponse("post.html", {"request": request, "post": post, "html_content": html_content})


@app.get("/examples/{page_name}", response_class=HTMLResponse, name="show_example")
def show_example(request: Request, page_name: str):
    template_path = TEMPLATE_DIR / "examples" / page_name

    if not template_path.resolve().is_relative_to(TEMPLATE_DIR.resolve()):
        raise HTTPException(status_code=403, detail="Permission Denied")
    
    if not template_path.is_file():
        raise HTTPException(status_code=404, detail=f"Page {page_name} not found")

    return templates.TemplateResponse(f"examples/{page_name}", {"request": request})
