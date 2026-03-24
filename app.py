# app.py
# ─────────────────────────────────────────────────────────
# This is the ENTRY POINT of our Flask application.
# It creates the app, connects all the pieces together,
# and defines the first route (URL).
# ─────────────────────────────────────────────────────────

from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import Config

# ── Step 1: Create the Flask app ──────────────────────────
# __name__ tells Flask where to look for templates and static files.
app = Flask(__name__)

# ── Step 2: Load our config settings ─────────────────────
app.config.from_object(Config)

# ── Step 3: Set up the database ───────────────────────────
# db is our database connection object.
# We'll use this throughout the app to read/write data.
db = SQLAlchemy(app)

# ── Step 4: Set up the login manager ──────────────────────
# LoginManager handles "who is logged in" for us.
login_manager = LoginManager(app)

# This tells Flask: if someone tries to access a page that
# requires login, redirect them to the 'login' page.
login_manager.login_view = 'login'

# A friendly message shown when redirected to login.
login_manager.login_message = 'Please log in to access this page.'
login_manager.login_message_category = 'info'

# ────────────────────────────────────────────
# This tells Flask-Login HOW to load a user from the database.
# It receives the user's ID (stored in their session cookie)
# and returns the matching User object.
# We import User here to avoid circular import issues.
@login_manager.user_loader
def load_user(user_id):
    from models import User          # ← We'll create models.py in Step 2
    return User.query.get(int(user_id))


# ── Step 5: Define our first route ────────────────────────
# A "route" connects a URL to a Python function.
# When someone visits the home page ('/'), this function runs.
@app.route('/')
def index():
    """Home page — the landing page of our app."""
    return render_template('index.html')


# ── Step 6: Run the app ───────────────────────────────────
# This block only runs when you execute 'python app.py' directly.
# debug=True means Flask will auto-reload when you save changes
# and show detailed error messages — very helpful during development!
if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Creates database tables (safe to run multiple times)
    app.run(debug=True)