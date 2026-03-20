import secrets

from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import RedirectResponse
import bcrypt
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy.orm import Session

from db_utils.database import SessionLocal
from db_utils.models import AdminUser


class RequireLoginException(Exception):
    pass


limiter = Limiter(key_func=get_remote_address)

router = APIRouter(prefix="/admin")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def require_admin(request: Request) -> str:
    username = request.session.get("admin_user")
    if not username:
        raise RequireLoginException()
    return username


def generate_csrf_token(request: Request) -> str:
    token = request.session.get("csrf_token")
    if not token:
        token = secrets.token_hex(32)
        request.session["csrf_token"] = token
    return token


async def verify_csrf_token(request: Request, csrf_token: str = Form(...)):
    session_token = request.session.get("csrf_token", "")
    if not secrets.compare_digest(session_token, csrf_token):
        raise RequireLoginException()


@router.get("/login")
def admin_login(request: Request):
    templates = request.app.state.templates
    csrf_token = generate_csrf_token(request)
    return templates.TemplateResponse("admin/login.html", {
        "request": request,
        "csrf_token": csrf_token,
        "error": None,
    })


@router.post("/login")
@limiter.limit("5/minute")
def admin_login_post(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    csrf_token: str = Form(...),
    db: Session = Depends(get_db),
):
    templates = request.app.state.templates

    # Verify CSRF
    session_token = request.session.get("csrf_token", "")
    if not secrets.compare_digest(session_token, csrf_token):
        new_csrf = generate_csrf_token(request)
        return templates.TemplateResponse("admin/login.html", {
            "request": request,
            "csrf_token": new_csrf,
            "error": "Invalid request. Please try again.",
        })

    user = db.query(AdminUser).filter(AdminUser.username == username).first()
    if not user or not bcrypt.checkpw(password.encode(), user.password_hash.encode()):
        new_csrf = generate_csrf_token(request)
        return templates.TemplateResponse("admin/login.html", {
            "request": request,
            "csrf_token": new_csrf,
            "error": "Invalid username or password.",
        })

    # Successful login — set session and rotate CSRF token
    request.session["admin_user"] = user.username
    request.session["csrf_token"] = secrets.token_hex(32)

    return RedirectResponse(url="/admin/", status_code=303)


@router.get("/logout")
def admin_logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/admin/login", status_code=303)
