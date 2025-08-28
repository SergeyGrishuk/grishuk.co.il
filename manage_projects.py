#!/usr/bin/env python3


from sys import stderr
from dotenv import load_dotenv

load_dotenv(".env")

from argparse import ArgumentParser, Namespace
from database import SessionLocal, engine
from models import Project, Tag


def parse_arguments() -> Namespace:
    parser = ArgumentParser()

    parser.add_argument("-a", "--add-project", action="store_true", help="Add a new project")
    parser.add_argument("-d", "--delete-project", action="store_true", help="Delete a project")

    return parser.parse_args()


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


def delete_project():
    """Interactively removes a project from the database by its title."""

    print("\n--- Remove a Project ---")

    db = SessionLocal()

    try:
        projects = db.query(Project).order_by(Project.title).all()

        if not projects:
            print("No projects in the db")

            return
        
        print("Projects: ")

        for project in projects:
            print(f"- {project.title}")
        
        title_to_remove = input("Enter the title of the prohect to remove: ")

        project = db.query(Project).filter_by(title=title_to_remove).first()

        if not project:
            print(f"Project `{title_to_remove}' does not exist in the db")

            return

        db.delete(project)
        db.commit()
    finally:
        db.close()


if __name__ == "__main__":
    args = parse_arguments()

    if args.add_project:
        add_project()
    elif args.delete_project:
        delete_project()
