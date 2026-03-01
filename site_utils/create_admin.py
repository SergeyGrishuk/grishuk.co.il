#!/usr/bin/env python3

import getpass
from sys import path, stderr
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(".env")

project_root = Path(__file__).resolve().parents[1]
path.append(str(project_root))

import bcrypt

from db_utils.database import SessionLocal
from db_utils.models import AdminUser


def main():
    print("--- Create Admin User ---")

    username = input("Username: ").strip()
    if not username:
        print("Error: username cannot be empty.", file=stderr)
        return

    password = getpass.getpass("Password: ")
    password_confirm = getpass.getpass("Confirm password: ")

    if password != password_confirm:
        print("Error: passwords do not match.", file=stderr)
        return

    if len(password) < 8:
        print("Error: password must be at least 8 characters.", file=stderr)
        return

    db = SessionLocal()
    try:
        existing = db.query(AdminUser).filter(AdminUser.username == username).first()
        new_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

        if existing:
            existing.password_hash = new_hash
            db.commit()
            print(f"Password updated for admin user '{username}'.")
        else:
            user = AdminUser(username=username, password_hash=new_hash)
            db.add(user)
            db.commit()
            print(f"Admin user '{username}' created successfully.")
    except Exception as e:
        db.rollback()
        print(f"Error: {e}", file=stderr)
    finally:
        db.close()


if __name__ == "__main__":
    main()
