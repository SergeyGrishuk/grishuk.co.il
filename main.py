#!/usr/bin/env python3


from fastapi import FastAPI, Request, Depends
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from starlette.middleware.base import BaseHTTPMiddleware
from markdown2 import markdown

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

def markdown_to_html(text):
    return markdown(text)

templates.env.filters["markdown"] = markdown_to_html

def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


@app.get("/")
def root(request: Request, db: Session = Depends(get_db)):
    projects = db.query(models.Project).order_by(models.Project.id.desc()).all()
    posts = db.query(models.Post).order_by(models.Post.id.desc()).all()

    return templates.TemplateResponse("home.html", {
        "request": request,
        "projects": projects,
        "posts": posts
    })


@app.get("/examples/{page_name}")
def show_example(request: Request, page_name: str):
    return templates.TemplateResponse(f"examples/{page_name}", {"request": request})
