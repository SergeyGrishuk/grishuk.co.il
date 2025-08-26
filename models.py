#!/usr/vin/env python3


from .database import Base
from sqlalchemy import Column, Integer, String, TextField

class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True)
    title = Column(String, index=True)
    description = Column(TextField)
    github_link = Column(String, nullable=True)
