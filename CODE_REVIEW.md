# Code Review - grishuk.co.il

**Date:** January 19, 2026  
**Branch:** `cursor/code-review-4f87`  
**Reviewer:** Automated Code Review

---

## Summary

This is a FastAPI-based personal portfolio/blog website with PostgreSQL database backend. The codebase is generally well-structured, but there are several security concerns, code quality issues, and best practice improvements to consider.

---

## Critical Issues

### 1. Missing Database URL Validation (`db_utils/database.py`)

```12:14:db_utils/database.py
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
```

**Issue:** If `DATABASE_URL` is `None`, `create_engine(None)` will raise an unclear error at module import time.

**Recommendation:**
```python
DATABASE_URL = getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is required")
```

### 2. Deprecated SQLAlchemy Import (`db_utils/database.py`)

```7:7:db_utils/database.py
from sqlalchemy.ext.declarative import declarative_base
```

**Issue:** `declarative_base` from `sqlalchemy.ext.declarative` is deprecated in SQLAlchemy 2.0.

**Recommendation:**
```python
from sqlalchemy.orm import declarative_base
```

---

## Security Issues

### 3. Path Traversal Protection - Needs Extension Validation (`main.py`)

```120:130:main.py
@app.get("/examples/{page_name}", response_class=HTMLResponse, name="show_example")
def show_example(request: Request, page_name: str):
    template_path = TEMPLATE_DIR / "examples" / page_name

    if not template_path.resolve().is_relative_to(TEMPLATE_DIR.resolve()):
        raise HTTPException(status_code=403, detail="Permission Denied")
    
    if not template_path.is_file():
        raise HTTPException(status_code=404, detail=f"Page {page_name} not found")

    return templates.TemplateResponse(f"examples/{page_name}", {"request": request})
```

**Issue:** While path traversal is protected, there's no validation that only `.html` files are served. An attacker could potentially request non-HTML files if they exist in the examples directory.

**Recommendation:** Add file extension validation:
```python
if not page_name.endswith('.html'):
    raise HTTPException(status_code=400, detail="Invalid file type")
```

### 4. No Rate Limiting

**Issue:** No rate limiting is implemented on any endpoints, making the application vulnerable to brute force attacks and DoS.

**Recommendation:** Consider adding rate limiting middleware such as `slowapi` or implementing it at the nginx/reverse proxy level.

### 5. Security Headers Missing

**Issue:** No security headers are set (CSP, X-Frame-Options, X-Content-Type-Options, etc.).

**Recommendation:** Add security headers middleware:
```python
from starlette.middleware import Middleware
from starlette.middleware.httpsredirect import HTTPSRedirectMiddleware

@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    return response
```

---

## Code Quality Issues

### 6. Inconsistent Link Handling in CustomRenderer (`main.py`)

```48:54:main.py
    def link(self, text, url, title=None):
        html = super().link(text, url, title)

        if url.startswith(("http://", "https://", "//")):
            return html.replace("<a href=", '<a target="_blank" rel="noopener noreferrer" href=', 1)
        
        return html.replace("<a href=", '<a target="_blank" href=', 1)
```

**Issue:** Internal links (those not starting with http/https) also get `target="_blank"`, which opens them in a new tab. This is typically undesirable for internal navigation.

**Recommendation:**
```python
def link(self, text, url, title=None):
    html = super().link(text, url, title)
    if url.startswith(("http://", "https://", "//")):
        return html.replace("<a href=", '<a target="_blank" rel="noopener noreferrer" href=', 1)
    return html  # Keep internal links in same tab
```

### 7. Bug in Image Method (`main.py`)

```57:60:main.py
    def image(self, text, url, title = None):
        html = super().image(text, url, title = None)

        return html.replace('<img src="', '<img class="center-image" src="', 1)
```

**Issue:** `title = None` is passed to `super().image()` instead of the actual `title` parameter. This discards any title the user provides.

**Fix:**
```python
def image(self, text, url, title=None):
    html = super().image(text, url, title)  # Pass actual title
    return html.replace('<img src="', '<img class="center-image" src="', 1)
```

### 8. Commented-Out Code (`main.py`, `manage_content.py`, `home.html`)

Multiple files contain significant amounts of commented-out code related to "projects" functionality:
- `main.py` lines 89, 94-95
- `manage_content.py` lines 39, 63-69, 212-215
- `home.html` lines 68-86

**Recommendation:** Remove commented-out code and rely on version control to track historical code. If the feature is planned for the future, create a feature branch or document it properly.

### 9. Hardcoded Strings in Templates

**Issue:** Multiple hardcoded strings like "Sergey Grishuk" appear across templates.

**Recommendation:** Consider using configuration or template context for site-wide values to make maintenance easier.

### 10. No Input Sanitization in `post.html`

```8:8:templates/post.html
    <meta name="description" content="{{ post.summary }}">
```

**Issue:** The summary is directly interpolated into an HTML attribute without explicit escaping. While Jinja2 auto-escapes in content, meta tag context may need careful handling.

**Recommendation:** Ensure summary doesn't contain characters that could break the HTML attribute (quotes, etc.) or use `| e` filter explicitly.

---

## Database/ORM Issues

### 11. Missing String Length for Slug Column (`db_utils/models.py`)

```45:45:db_utils/models.py
    slug = Column(String, index=True, nullable=False)
```

**Issue:** The `slug` column has no length limit, which could cause issues with some databases and indexing.

**Recommendation:**
```python
slug = Column(String(512), index=True, nullable=False, unique=True)
```

Also consider adding a `unique=True` constraint since slugs should be unique.

### 12. Missing Cascade Deletes

**Issue:** When deleting a Post or Project, the relationships in the junction tables (`post_tags`, `project_tags`) may not be properly cleaned up.

**Recommendation:** Add cascade rules:
```python
tags = relationship("Tag", secondary=post_tags, back_populates="posts", 
                    passive_deletes=True)
```

---

## Minor Issues

### 13. Inconsistent Error Handling in `manage_content.py`

```143:146:site_utils/manage_content.py
    except Exception as e:
        print(f"\nAn error occurred: {e}", file=stderr)
    finally:
        db.close()
```

**Issue:** `delete_item` doesn't call `db.rollback()` in the exception handler, unlike `add_item` and `modify_item`.

### 14. Home Page Link Inconsistency (`home.html`)

```18:18:templates/home.html
        <a href="/#case-studies" role="button" class="contrast">View My Work</a>
```

**Issue:** The "View My Work" button links to `#case-studies` which is commented out in the template.

**Fix:** Update the link to point to `#posts`:
```html
<a href="/#posts" role="button" class="contrast">View My Work</a>
```

### 15. Missing `__init__.py` in `site_utils`

**Issue:** The `site_utils` directory doesn't have an `__init__.py` file, which could cause import issues depending on Python version and import method.

### 16. Unused Import in `requirements.txt`

```7:7:requirements.txt
markdown2==2.5.4
```

**Issue:** `markdown2` is listed in requirements but the code uses `mistune` for markdown processing.

**Recommendation:** Remove `markdown2` from requirements.txt if not used.

### 17. Missing 404 Page Title (`templates/404.html`)

**Issue:** The 404 template doesn't set a `{% block title %}`, so it inherits an empty title.

**Fix:** Add a title block:
```html
{% block title %}
    <title>404 - Page Not Found | Sergey Grishuk</title>
{% endblock %}
```

---

## Performance Recommendations

### 18. Database Query Optimization

Consider adding `joinedload` for tags to avoid N+1 queries:

```python
from sqlalchemy.orm import joinedload

posts = db.query(models.Post).options(
    joinedload(models.Post.tags)
).order_by(models.Post.id.desc()).all()
```

### 19. Consider Connection Pooling Configuration

The current database setup uses default connection pooling. For production, consider explicitly configuring pool settings.

---

## Positive Observations

1. **Good path traversal protection** in the examples endpoint
2. **Proper use of `rel="noopener noreferrer"`** for external links
3. **Clean separation** of database models, utilities, and routes
4. **Environment variables** used for sensitive configuration
5. **Proper exception handling** with database rollbacks in most places
6. **SEO-friendly** with meta descriptions and sitemap generation

---

## Action Items Summary

| Priority | Issue | File |
|----------|-------|------|
| High | Fix DATABASE_URL validation | `db_utils/database.py` |
| High | Fix image method title bug | `main.py` |
| High | Fix "View My Work" broken link | `templates/home.html` |
| Medium | Add file extension validation | `main.py` |
| Medium | Fix deprecated import | `db_utils/database.py` |
| Medium | Fix internal link handling | `main.py` |
| Low | Remove commented code | Multiple files |
| Low | Add 404 page title | `templates/404.html` |
| Low | Remove unused markdown2 | `requirements.txt` |
| Low | Add unique constraint to slug | `db_utils/models.py` |

---

*This review was generated for the purpose of improving code quality and security.*
