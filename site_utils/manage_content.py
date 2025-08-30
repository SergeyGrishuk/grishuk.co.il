#!/usr/bin/env python3

from os.path import join
from sys import stderr, path
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(".env")

from argparse import ArgumentParser, Namespace

# Set up project root path
project_root = Path(__file__).resolve().parent
path.append(str(project_root))

from db_utils.database import SessionLocal
from db_utils.models import Project, Post, Tag


def parse_arguments() -> Namespace:
    """Configures and parses command-line arguments."""
    parser = ArgumentParser(description="Manage website content (projects and posts).")

    # Group for selecting the type of content
    type_group = parser.add_mutually_exclusive_group(required=True)
    type_group.add_argument("--project", action="store_true", help="Work with projects.")
    type_group.add_argument("--post", action="store_true", help="Work with posts.")

    # Group for selecting the action
    action_group = parser.add_mutually_exclusive_group(required=True)
    action_group.add_argument("--add", action="store_true", help="Add a new item.")
    action_group.add_argument("--delete", action="store_true", help="Delete an existing item.")

    return parser.parse_args()


def add_item(model_class, item_name: str) -> None:
    """Interactively adds a new item (project or post) to the database."""
    print(f"--- Add a New {item_name.capitalize()} ---")

    title = input(f"Enter {item_name} title: ")
    tags_input = input("Enter tags (comma-separated): ")

    item_data = {
        "title": title,
    }

    # Collect model-specific fields
    if model_class == Project:
        description_file = input("Enter description markdown file name: ")
        with open(join("markdown_content", description_file)) as f:
            item_data["description"] = f.read()
        item_data["github_link"] = input("Enter GitHub link: ")
    elif model_class == Post:
        item_data["summary"] = input("Enter post summary: ")
        # publish_date is handled by the database default

    db = SessionLocal()
    try:
        new_item = model_class(**item_data)
        
        # Process and associate tags
        tag_names = [tag.strip() for tag in tags_input.split(",") if tag.strip()]
        for tag_name in tag_names:
            tag = db.query(Tag).filter_by(name=tag_name).first()
            if not tag:
                tag = Tag(name=tag_name)
                db.add(tag)
            new_item.tags.append(tag)

        db.add(new_item)
        db.commit()
        print(f"\nSuccessfully added new {item_name}: {title}")

    except Exception as e:
        db.rollback()
        print(f"\nAn error occurred: {e}", file=stderr)
        print("Database transaction has been rolled back.", file=stderr)
    finally:
        db.close()


def delete_item(model_class, item_name: str) -> None:
    """Interactively deletes an item (project or post) from the database."""
    print(f"\n--- Delete a {item_name.capitalize()} ---")

    db = SessionLocal()
    try:
        items = db.query(model_class).order_by(model_class.title).all()

        if not items:
            print(f"No {item_name}s found in the database.")
            return

        print(f"Existing {item_name}s:")
        for item in items:
            print(f"- {item.title}")

        title_to_delete = input(f"\nEnter the exact title of the {item_name} to delete: ")
        item_to_delete = db.query(model_class).filter_by(title=title_to_delete).first()

        if not item_to_delete:
            print(f"\nError: {item_name.capitalize()} '{title_to_delete}' not found.")
            return

        confirm = input(f"Are you sure you want to delete '{item_to_delete.title}'? [y/N] ")
        if confirm.lower() == "y":
            db.delete(item_to_delete)
            db.commit()
            print(f"Successfully deleted '{title_to_delete}'.")
        else:
            print("Deletion canceled.")

    except Exception as e:
        print(f"\nAn error occurred: {e}", file=stderr)
    finally:
        db.close()


if __name__ == "__main__":
    args = parse_arguments()

    # Determine which model and name to use
    if args.project:
        model, name = Project, "project"
    elif args.post:
        model, name = Post, "post"
    
    # Determine which action to perform
    if args.add:
        add_item(model, name)
    elif args.delete:
        delete_item(model, name)
