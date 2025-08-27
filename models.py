#!/usr/vin/env python3


from database import Base
from sqlalchemy import Column, Integer, String, Text

class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True)
    title = Column(String(128), index=True)
    description = Column(Text)
    github_link = Column(String(256), nullable=True)
