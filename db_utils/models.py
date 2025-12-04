

from db_utils.database import Base
from sqlalchemy import Column, Integer, String, Text, Table, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func


project_tags = Table("project_tags", Base.metadata,
    Column("project_id", Integer, ForeignKey("projects.id"), primary_key=True),
    Column("tag_id", Integer, ForeignKey("tags.id"), primary_key=True))

post_tags = Table("post_tags", Base.metadata,
    Column("post_id", Integer, ForeignKey("posts.id"), primary_key=True),
    Column("tag_id", Integer, ForeignKey("tags.id"), primary_key=True))


class Tag(Base):
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True)
    name = Column(String(64), unique=True, index=True, nullable=False)

    def __str__(self):
        return self.name


class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True)
    title = Column(String(128), index=True)
    description = Column(Text)
    github_link = Column(String(256), nullable=True)

    tags = relationship("Tag", secondary=project_tags, back_populates="projects")


class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True)
    title = Column(String(256), nullable=False)
    meta_title = Column(String(80), nullable=True)
    slug = Column(String, index=True, nullable=False)
    summary = Column(Text, nullable=False)
    post_content = Column(Text, nullable=False)
    publish_date = Column(DateTime(timezone=True), server_default=func.now())

    tags = relationship("Tag", secondary=post_tags, back_populates="posts")


Tag.projects = relationship("Project", secondary=project_tags, back_populates="tags")
Tag.posts = relationship("Post", secondary=post_tags, back_populates="tags")
