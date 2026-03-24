# config.py
# ─────────────────────────────────────────────────────────
# This file holds all the settings/configuration for our app.
# Keeping settings in one place is a best practice — if you
# need to change something, you only change it here.
# ─────────────────────────────────────────────────────────

import os

class Config:
    # SECRET_KEY is used by Flask to securely sign session cookies.
    # Think of it as a password that only your server knows.
    # In a real app, this should come from an environment variable,
    # but for learning purposes, a hardcoded string is fine.
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'trader-journal-secret-key-2024'

    # This tells SQLAlchemy where to find (or create) the SQLite database file.
    # 'instance/journal.db' means a file called journal.db inside the instance/ folder.
    SQLALCHEMY_DATABASE_URI = 'sqlite:///journal.db'

    # This disables a Flask-SQLAlchemy feature we don't need.
    # It just suppresses an annoying warning message.
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # This is the folder where we'll save uploaded trade screenshots.
    UPLOAD_FOLDER = os.path.join('static', 'uploads')

    # Only allow these file types to be uploaded (basic security).
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}