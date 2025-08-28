#!/usr/bin/env python3


from sys import stderr
from dotenv import load_dotenv

load_dotenv(".env")

from database import SessionLocal, engine
from models import Project, Tag


def add_project() -> None:
    """Interactively adds a new project and its tags to the database."""
    print("--- Add a New Project ---")
    title = input("Enter project title: ")
    description = input("Enter project description (use \\n for new lines): ").replace('\\n', '\n')
    github_link = input("Enter GitHub link: ")
    tags_input = input("Enter tags (comma-separated): ")

    db = SessionLocal()

    try:
        new_project = Project(
            title = title,
            description = description,
            github_link = github_link
        )

        tags = [tag.strip() for tag in tags_input.split(",") if tag.strip()]

        for tag_name in tags:
            tag = db.query(Tag).filter_by(name=tag_name).first()

            if not tag:
                tag = Tag(name=tag_name)
                db.add(tag)

            new_project.tags.append(tag)

        db.add(new_project)
        db.commit()

        print(f"Added new project: {title}")

    except Exception as e:
        db.rollback()

        print("An error occured, rolling back the db", file=stderr)
    finally:
        db.close()


if __name__ == "__main__":
    add_project()
