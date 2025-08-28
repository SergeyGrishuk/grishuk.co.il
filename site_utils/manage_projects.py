#!/usr/bin/env python3


from os.path import join
from sys import stderr, path
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(".env")

from argparse import ArgumentParser, Namespace

project_root = Path(__file__).resolve().parents[1]
path.append(str(project_root))

from db_utils.database import SessionLocal
from db_utils.models import Project, Tag


def parse_arguments() -> Namespace:
    parser = ArgumentParser()

    parser.add_argument("-a", "--add-project", action="store_true", help="Add a new project")
    parser.add_argument("-d", "--delete-project", action="store_true", help="Delete a project")

    return parser.parse_args()


def add_project() -> None:
    """Interactively adds a new project and its tags to the database."""

    print("--- Add a New Project ---")
    
    title = input("Enter project title: ")
    #description = input("Enter project description (use \\n for new lines): ").replace('\\n', '\n')
    description_markdown_file = input("Enter description markdown file name: ")
    github_link = input("Enter GitHub link: ")
    tags_input = input("Enter tags (comma-separated): ")

    with open(join("markdown_content", description_markdown_file)) as f:
        description = f.read()

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
        
        title_to_remove = input("Enter the title of the project to remove: ")

        project = db.query(Project).filter_by(title=title_to_remove).first()

        if not project:
            print(f"Project `{title_to_remove}' does not exist in the db")

            return

        confirm = input(f"Are you sure you want to delete {project.title}? [y/N] ")

        if confirm.lower() == "y":
            db.delete(project)
            db.commit()
        else:
            print("Deletion canceled")
    finally:
        db.close()


if __name__ == "__main__":
    args = parse_arguments()

    if args.add_project:
        add_project()
    elif args.delete_project:
        delete_project()
