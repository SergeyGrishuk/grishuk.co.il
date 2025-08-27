#!/usr/bin/env python3


from fastapi import FastAPI
from fastapi.templating import Jinja2Templates

from database import SessionLocal


app = FastAPI()

templates = Jinja2Templates(directory="templates")


def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


@app.get("/")
def root():
    return {"msg": "It's alive!"}
