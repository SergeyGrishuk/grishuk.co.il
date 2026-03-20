import re
from datetime import datetime

from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from sqlalchemy import func

from db_utils.database import SessionLocal
from db_utils.models import Post, Tag, post_tags
from admin.auth import require_admin, verify_csrf_token, generate_csrf_token


router = APIRouter(prefix="/admin")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def slugify(text: str) -> str:
    text = text.lower()
    text = re.sub(r'[\s_]+', '-', text)
    text = re.sub(r'[^a-z0-9-]', '', text)
    return text


def ensure_unique_slug(db: Session, slug: str, exclude_post_id: int = None) -> str:
    candidate = slug
    counter = 2
    while True:
        query = db.query(Post).filter(Post.slug == candidate)
        if exclude_post_id is not None:
            query = query.filter(Post.id != exclude_post_id)
        if not query.first():
            return candidate
        candidate = f"{slug}-{counter}"
        counter += 1


def sync_tags(db: Session, post: Post, tags_input: str):
    tag_names = [t.strip() for t in tags_input.split(",") if t.strip()]
    tags = []
    for name in tag_names:
        tag = db.query(Tag).filter(Tag.name == name).first()
        if not tag:
            tag = Tag(name=name)
            db.add(tag)
            db.flush()
        tags.append(tag)
    post.tags = tags


# --- Dashboard ---

@router.get("/")
def admin_dashboard(
    request: Request,
    username: str = Depends(require_admin),
    db: Session = Depends(get_db),
):
    templates = request.app.state.templates
    posts = db.query(Post).order_by(Post.id.desc()).all()
    csrf_token = generate_csrf_token(request)
    return templates.TemplateResponse("admin/dashboard.html", {
        "request": request,
        "username": username,
        "posts": posts,
        "csrf_token": csrf_token,
    })


# --- Posts ---

@router.get("/posts/new")
def admin_new_post(
    request: Request,
    username: str = Depends(require_admin),
):
    templates = request.app.state.templates
    csrf_token = generate_csrf_token(request)
    return templates.TemplateResponse("admin/post_form.html", {
        "request": request,
        "username": username,
        "post": None,
        "csrf_token": csrf_token,
    })


@router.post("/posts/new")
async def admin_create_post(
    request: Request,
    username: str = Depends(require_admin),
    _csrf: None = Depends(verify_csrf_token),
    db: Session = Depends(get_db),
    title: str = Form(...),
    meta_title: str = Form(""),
    slug: str = Form(""),
    summary: str = Form(...),
    tags_input: str = Form(""),
    post_content: str = Form(...),
    publish_date: str = Form(""),
):
    if not slug.strip():
        slug = slugify(meta_title or title)
    slug = ensure_unique_slug(db, slug)

    post = Post(
        title=title,
        meta_title=meta_title.strip() or None,
        slug=slug,
        summary=summary,
        post_content=post_content,
    )
    if publish_date.strip():
        post.publish_date = datetime.fromisoformat(publish_date)

    sync_tags(db, post, tags_input)

    db.add(post)
    db.commit()

    return RedirectResponse(url="/admin/", status_code=303)


@router.get("/posts/{post_id}/edit")
def admin_edit_post(
    request: Request,
    post_id: int,
    username: str = Depends(require_admin),
    db: Session = Depends(get_db),
):
    templates = request.app.state.templates
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        return RedirectResponse(url="/admin/", status_code=303)

    csrf_token = generate_csrf_token(request)
    return templates.TemplateResponse("admin/post_form.html", {
        "request": request,
        "username": username,
        "post": post,
        "csrf_token": csrf_token,
    })


@router.post("/posts/{post_id}/edit")
async def admin_update_post(
    request: Request,
    post_id: int,
    username: str = Depends(require_admin),
    _csrf: None = Depends(verify_csrf_token),
    db: Session = Depends(get_db),
    title: str = Form(...),
    meta_title: str = Form(""),
    slug: str = Form(""),
    summary: str = Form(...),
    tags_input: str = Form(""),
    post_content: str = Form(...),
    publish_date: str = Form(""),
):
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        return RedirectResponse(url="/admin/", status_code=303)

    post.title = title
    post.meta_title = meta_title.strip() or None

    if slug.strip() and slug != post.slug:
        post.slug = ensure_unique_slug(db, slug, exclude_post_id=post.id)

    post.summary = summary
    post.post_content = post_content
    if publish_date.strip():
        post.publish_date = datetime.fromisoformat(publish_date)

    sync_tags(db, post, tags_input)

    db.commit()

    return RedirectResponse(url="/admin/", status_code=303)


@router.post("/posts/{post_id}/delete")
async def admin_delete_post(
    request: Request,
    post_id: int,
    username: str = Depends(require_admin),
    _csrf: None = Depends(verify_csrf_token),
    db: Session = Depends(get_db),
):
    post = db.query(Post).filter(Post.id == post_id).first()
    if post:
        db.delete(post)
        db.commit()

    return RedirectResponse(url="/admin/", status_code=303)


# --- Tags ---

@router.get("/tags")
def admin_tags(
    request: Request,
    username: str = Depends(require_admin),
    db: Session = Depends(get_db),
):
    templates = request.app.state.templates
    tags = (
        db.query(Tag, func.count(post_tags.c.post_id).label("post_count"))
        .outerjoin(post_tags, Tag.id == post_tags.c.tag_id)
        .group_by(Tag.id)
        .order_by(Tag.name)
        .all()
    )
    csrf_token = generate_csrf_token(request)
    return templates.TemplateResponse("admin/tags.html", {
        "request": request,
        "username": username,
        "tags": tags,
        "csrf_token": csrf_token,
    })


@router.post("/tags/{tag_id}/rename")
async def admin_rename_tag(
    request: Request,
    tag_id: int,
    username: str = Depends(require_admin),
    _csrf: None = Depends(verify_csrf_token),
    db: Session = Depends(get_db),
    name: str = Form(...),
):
    tag = db.query(Tag).filter(Tag.id == tag_id).first()
    if tag and name.strip():
        tag.name = name.strip()
        db.commit()

    return RedirectResponse(url="/admin/tags", status_code=303)


@router.post("/tags/{tag_id}/delete")
async def admin_delete_tag(
    request: Request,
    tag_id: int,
    username: str = Depends(require_admin),
    _csrf: None = Depends(verify_csrf_token),
    db: Session = Depends(get_db),
):
    tag = db.query(Tag).filter(Tag.id == tag_id).first()
    if tag:
        db.delete(tag)
        db.commit()

    return RedirectResponse(url="/admin/tags", status_code=303)


@router.post("/tags/cleanup")
async def admin_cleanup_tags(
    request: Request,
    username: str = Depends(require_admin),
    _csrf: None = Depends(verify_csrf_token),
    db: Session = Depends(get_db),
):
    orphaned = (
        db.query(Tag)
        .outerjoin(post_tags, Tag.id == post_tags.c.tag_id)
        .group_by(Tag.id)
        .having(func.count(post_tags.c.post_id) == 0)
        .all()
    )
    for tag in orphaned:
        db.delete(tag)
    db.commit()

    return RedirectResponse(url="/admin/tags", status_code=303)
