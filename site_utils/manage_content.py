#!/usr/bin/env python3

from os.path import join
from sys import stderr, path
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(".env")

from argparse import ArgumentParser, Namespace

# Set up project root path
project_root = Path(__file__).resolve().parents[1]
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
    action_group.add_argument("-a", "--add", action="store_true", help="Add a new item.")
    action_group.add_argument("-d", "--delete", action="store_true", help="Delete an existing item.")
    action_group.add_argument("-m", "--modify", action="store_true", help="Modify an existing item.")

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
        meta_title = input("Enter meta title: [None] ")

        if len(meta_title.strip()) > 0:
            item_data["meta_title"] = meta_title
        else:
            item_data["meta_title"] = None

        item_data["summary"] = input("Enter post summary: ")
        
        post_file = input("Enter post content markdown file name: ")

        with open(join("markdown_content", post_file)) as f:
            item_data["post_content"] = f.read()
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


def modify_item(model_class, item_name: str) -> None:
    """Interactively modifies an existing item (project or post)."""
    print(f"\n--- Modify a {item_name.capitalize()} ---")
    db = SessionLocal()

    try:
        items = db.query(model_class).order_by(model_class.id).all()
        if not items:
            print(f"No {item_name}s found to modify.")
            return

        # List items by number for easy selection
        print("Select an item to modify:")
        for i, item in enumerate(items, 1):
            print(f"  [{i}] {item.title}")

        # Get user's choice
        choice_str = input(f"\nEnter the number of the {item_name} to modify (or 0 to cancel): ")
        choice = int(choice_str)

        if choice == 0 or choice > len(items):
            print("Modification canceled or invalid choice.")
            return

        item_to_modify = items[choice - 1]

        print(f"\nEditing '{item_to_modify.title}'. Press Enter to keep the current value.")

        # --- Fields common to both Post and Project ---
        new_title = input(f"Enter new title [{item_to_modify.title}]: ")
        if new_title.strip():
            item_to_modify.title = new_title

        # --- Fields specific to Post ---
        if model_class == Post:
            current_meta_title = item_to_modify.meta_title or 'None'
            new_meta_title = input(f"Enter new meta title [{current_meta_title}]: ")
            if new_meta_title.strip():
                item_to_modify.meta_title = new_meta_title

            current_summary = item_to_modify.summary
            new_summary = input(f"Enter new summary [{current_summary[:60]}...]: ")
            if new_summary.strip():
                item_to_modify.summary = new_summary

        # You could add similar logic here for Project fields
        # ...

        db.commit()
        print(f"\nSuccessfully updated '{item_to_modify.title}'.")

    except (ValueError, IndexError):
        print("\nInvalid input. Please enter a number from the list.")
    except Exception as e:
        db.rollback()
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
    elif args.modify:
        modify_item(model, name)

