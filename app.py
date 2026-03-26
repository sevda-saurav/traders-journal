# app.py
# ─────────────────────────────────────────────────────────
# Updated with authentication routes:
#   GET  /          → Home page
#   GET  /signup    → Show signup form
#   POST /signup    → Process signup form
#   GET  /login     → Show login form
#   POST /login     → Process login form
#   GET  /logout    → Log the user out
#   GET  /dashboard → Protected page (login required)
# ─────────────────────────────────────────────────────────
import os
from flask import Flask, render_template, request, redirect, url_for, flash
from extensions import db
from flask_login import (
    LoginManager,
    login_user,       # logs a user in (creates session)
    logout_user,      # logs a user out (clears session)
    login_required,   # decorator → redirects to login if not logged in
    current_user      # gives us the currently logged-in user object
)
from config import Config
from werkzeug.utils import secure_filename
from datetime import datetime

# ── App Setup ─────────────────────────────────────────────
app = Flask(__name__)
app.config.from_object(Config)

# ── Database Setup ────────────────────────────────────────
db.init_app(app)

# ── Login Manager Setup ───────────────────────────────────
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access this page.'
login_manager.login_message_category = 'info'

# ── Helper Function ───────────────────────────────────────
def allowed_file(filename):
    """
    Checks if uploaded file has an allowed extension.
    Example: 'chart.png' → True  |  'virus.exe' → False
    """
    return (
        '.' in filename and
        filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']
    )

@login_manager.user_loader
def load_user(user_id):
    """Tell Flask-Login how to find a user by their ID."""
    from models import User
    return User.query.get(int(user_id))


# ─────────────────────────────────────────────────────────
# ROUTE 1: Home Page
# ─────────────────────────────────────────────────────────
@app.route('/')
def index():
    """
    Home/landing page.
    If user is already logged in, redirect them to dashboard.
    """
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template('index.html')


# ─────────────────────────────────────────────────────────
# ROUTE 2: Signup
# ─────────────────────────────────────────────────────────
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    """
    GET  → Show the empty signup form
    POST → Read form data, validate, create user, redirect to login
    """

    # If already logged in, no need to sign up again
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        # ── Read form data ─────────────────────────────
        # request.form is a dictionary of all submitted field values
        # .strip() removes accidental spaces before/after the text
        username = request.form.get('username', '').strip()
        email    = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        confirm  = request.form.get('confirm_password', '')

        # ── Validation ────────────────────────────────
        # We check for problems BEFORE touching the database.
        # flash(message, category) stores a one-time message.
        # Categories: 'danger', 'success', 'info', 'warning'

        if not username or not email or not password or not confirm:
            flash('All fields are required.', 'danger')
            return render_template('auth/signup.html')

        if len(username) < 3:
            flash('Username must be at least 3 characters.', 'danger')
            return render_template('auth/signup.html')

        if len(password) < 6:
            flash('Password must be at least 6 characters.', 'danger')
            return render_template('auth/signup.html')

        if password != confirm:
            flash('Passwords do not match.', 'danger')
            return render_template('auth/signup.html')

        # ── Check for duplicates ──────────────────────
        from models import User

        # Query the database — does a user with this email already exist?
        existing_email = User.query.filter_by(email=email).first()
        if existing_email:
            flash('An account with this email already exists.', 'danger')
            return render_template('auth/signup.html')

        existing_username = User.query.filter_by(username=username).first()
        if existing_username:
            flash('This username is already taken.', 'danger')
            return render_template('auth/signup.html')

        # ── Create the new user ───────────────────────
        new_user = User(username=username, email=email)
        new_user.set_password(password)  # hashes the password

        # Add to database
        db.session.add(new_user)    # stage the new record
        db.session.commit()         # actually save to database

        flash('Account created successfully! Please log in.', 'success')
        return redirect(url_for('login'))

    # GET request — just show the empty form
    return render_template('auth/signup.html')


# ─────────────────────────────────────────────────────────
# ROUTE 3: Login
# ─────────────────────────────────────────────────────────
@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    GET  → Show the empty login form
    POST → Read form data, check credentials, create session
    """

    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        email    = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')

        # ── Basic validation ──────────────────────────
        if not email or not password:
            flash('Please enter both email and password.', 'danger')
            return render_template('auth/login.html')

        # ── Find user in database ─────────────────────
        from models import User
        user = User.query.filter_by(email=email).first()

        # ── Check credentials ─────────────────────────
        # We check BOTH in one if statement intentionally.
        # This avoids telling hackers "email not found" vs "wrong password"
        # — we just say "invalid credentials" for both cases.
        if not user or not user.check_password(password):
            flash('Invalid email or password. Please try again.', 'danger')
            return render_template('auth/login.html')

        # ── Log the user in ───────────────────────────
        # login_user() creates a session — Flask-Login handles the cookie.
        # remember=True → stay logged in even after browser closes
        login_user(user, remember=True)

        flash(f'Welcome back, {user.username}! 👋', 'success')

        # ── Redirect to next page ─────────────────────
        # If user tried to visit a protected page before logging in,
        # Flask-Login saved that URL as 'next' — send them there.
        next_page = request.args.get('next')
        return redirect(next_page) if next_page else redirect(url_for('dashboard'))

    return render_template('auth/login.html')


# ─────────────────────────────────────────────────────────
# ROUTE 4: Logout
# ─────────────────────────────────────────────────────────
@app.route('/logout')
@login_required   # Can't log out if you're not logged in!
def logout():
    """Clears the user's session and redirects to home."""
    logout_user()
    flash('You have been logged out. See you soon! 👋', 'info')
    return redirect(url_for('index'))


# ─────────────────────────────────────────────────────────
# ROUTE 5: Dashboard (Protected Page)
# ─────────────────────────────────────────────────────────
@app.route('/dashboard')
@login_required   # ← This decorator protects the route
def dashboard():
    """
    Main dashboard — only accessible when logged in.
    @login_required automatically redirects to /login if not authenticated.
    We'll build the full dashboard in Step 4.
    For now, just a simple welcome page.
    """
    return render_template('dashboard.html')


# ─────────────────────────────────────────────────────────
# View All Trades
# ─────────────────────────────────────────────────────────
@app.route('/trades')
@login_required
def view_trades():
    """
    Fetches all trades belonging to the logged-in user
    and displays them in a list/table.
    """
    from models import Trade

    # Filter trades by the current user's ID
    # Order by newest first (descending trade_date)
    trades = Trade.query.filter_by(
        user_id=current_user.id
    ).order_by(Trade.trade_date.desc()).all()

    return render_template('trades/view_trades.html', trades=trades)


# ─────────────────────────────────────────────────────────
# Add Trade
# ─────────────────────────────────────────────────────────
@app.route('/trade/add', methods=['GET', 'POST'])
@login_required
def add_trade():
    """
    GET  → Show the empty add trade form
    POST → Read form data, validate, save trade to database
    """
    if request.method == 'POST':
        from models import Trade

        # ── Read all form fields ───────────────────────
        market_name   = request.form.get('market_name', '')
        custom_market = request.form.get('custom_market', '').strip()
        trade_date_str= request.form.get('trade_date', '')
        trade_type    = request.form.get('trade_type', '')
        description   = request.form.get('description', '').strip()

        # ── Read numeric fields safely ─────────────────
        try:
            buy_value  = float(request.form.get('buy_value', 0))
            sell_value = float(request.form.get('sell_value', 0))
            target     = float(request.form.get('target', 0))
            stop_loss  = float(request.form.get('stop_loss', 0))
            capital    = float(request.form.get('capital', 0))
        except ValueError:
            flash('Please enter valid numbers for price fields.', 'danger')
            return render_template('trades/add_trade.html')

        # ── Validation ────────────────────────────────
        if not market_name or not trade_date_str or not trade_type:
            flash('Please fill in all required fields.', 'danger')
            return render_template('trades/add_trade.html')

        if market_name == 'Other' and not custom_market:
            flash('Please specify the market name.', 'danger')
            return render_template('trades/add_trade.html')

        if buy_value <= 0 or sell_value <= 0 or capital <= 0:
            flash('Price and capital values must be greater than 0.', 'danger')
            return render_template('trades/add_trade.html')

        # ── Parse date string to Python datetime ──────
        try:
            trade_date = datetime.strptime(trade_date_str, '%Y-%m-%dT%H:%M')
        except ValueError:
            flash('Invalid date format.', 'danger')
            return render_template('trades/add_trade.html')

        # ── Handle screenshot upload ───────────────────
        screenshot_filename = None
        screenshot_file = request.files.get('screenshot')

        if screenshot_file and screenshot_file.filename != '':
            if allowed_file(screenshot_file.filename):
                # secure_filename() cleans the filename
                # e.g. "../../etc/passwd" → "etc_passwd" (security!)
                filename = secure_filename(screenshot_file.filename)

                # Add timestamp to avoid name conflicts
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename  = f"{timestamp}_{filename}"

                # Save the file
                save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                screenshot_file.save(save_path)
                screenshot_filename = filename
            else:
                flash('Invalid file type. Use PNG, JPG, GIF or WEBP.', 'danger')
                return render_template('trades/add_trade.html')

        # ── Create Trade object ────────────────────────
        trade = Trade(
            user_id      = current_user.id,
            market_name  = market_name,
            custom_market= custom_market,
            trade_date   = trade_date,
            trade_type   = trade_type,
            buy_value    = buy_value,
            sell_value   = sell_value,
            target       = target,
            stop_loss    = stop_loss,
            capital      = capital,
            description  = description,
            screenshot   = screenshot_filename
        )

        # ── Auto-calculate P&L and R:R ────────────────
        trade.calculate_profit_loss()
        trade.calculate_risk_reward()

        # ── Save to database ──────────────────────────
        db.session.add(trade)
        db.session.commit()

        flash('Trade logged successfully! 📈', 'success')
        return redirect(url_for('view_trades'))

    return render_template('trades/add_trade.html')


# ─────────────────────────────────────────────────────────
# Edit Trade
# ─────────────────────────────────────────────────────────
@app.route('/trade/edit/<int:trade_id>', methods=['GET', 'POST'])
@login_required
def edit_trade(trade_id):
    """
    <int:trade_id> → Flask captures the ID from the URL
    Example: /trade/edit/5 → trade_id = 5

    GET  → Show the form pre-filled with existing trade data
    POST → Read updated form data, save changes to database
    """
    from models import Trade

    # Fetch the trade — 404 if not found
    trade = Trade.query.get_or_404(trade_id)

    # Security check: make sure this trade belongs to current user
    # Without this, any logged-in user could edit someone else's trades!
    if trade.user_id != current_user.id:
        flash('You do not have permission to edit this trade.', 'danger')
        return redirect(url_for('view_trades'))

    if request.method == 'POST':
        # ── Update fields ─────────────────────────────
        trade.market_name   = request.form.get('market_name', '')
        trade.custom_market = request.form.get('custom_market', '').strip()
        trade.trade_type    = request.form.get('trade_type', '')
        trade.description   = request.form.get('description', '').strip()

        try:
            trade.buy_value  = float(request.form.get('buy_value', 0))
            trade.sell_value = float(request.form.get('sell_value', 0))
            trade.target     = float(request.form.get('target', 0))
            trade.stop_loss  = float(request.form.get('stop_loss', 0))
            trade.capital    = float(request.form.get('capital', 0))
        except ValueError:
            flash('Please enter valid numbers for price fields.', 'danger')
            return render_template('trades/edit_trade.html', trade=trade)

        trade_date_str = request.form.get('trade_date', '')
        try:
            trade.trade_date = datetime.strptime(trade_date_str, '%Y-%m-%dT%H:%M')
        except ValueError:
            flash('Invalid date format.', 'danger')
            return render_template('trades/edit_trade.html', trade=trade)

        # ── Handle new screenshot upload ───────────────
        screenshot_file = request.files.get('screenshot')
        if screenshot_file and screenshot_file.filename != '':
            if allowed_file(screenshot_file.filename):
                # Delete old screenshot if it exists
                if trade.screenshot:
                    old_path = os.path.join(app.config['UPLOAD_FOLDER'],
                                            trade.screenshot)
                    if os.path.exists(old_path):
                        os.remove(old_path)

                filename  = secure_filename(screenshot_file.filename)
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename  = f"{timestamp}_{filename}"
                save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                screenshot_file.save(save_path)
                trade.screenshot = filename
            else:
                flash('Invalid file type.', 'danger')
                return render_template('trades/edit_trade.html', trade=trade)

        # ── Recalculate P&L and R:R ───────────────────
        trade.calculate_profit_loss()
        trade.calculate_risk_reward()
        trade.updated_at = datetime.utcnow()

        db.session.commit()
        flash('Trade updated successfully! ✅', 'success')
        return redirect(url_for('view_trades'))

    return render_template('trades/edit_trade.html', trade=trade)


# ─────────────────────────────────────────────────────────
# Delete Trade
# ─────────────────────────────────────────────────────────
@app.route('/trade/delete/<int:trade_id>', methods=['POST'])
@login_required
def delete_trade(trade_id):
    """
    We use POST (not GET) for delete — important security practice.
    Never delete data with a GET request (search engines crawl GET links!).
    """
    from models import Trade

    trade = Trade.query.get_or_404(trade_id)

    # Security check
    if trade.user_id != current_user.id:
        flash('You do not have permission to delete this trade.', 'danger')
        return redirect(url_for('view_trades'))

    # Delete screenshot file if it exists
    if trade.screenshot:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], trade.screenshot)
        if os.path.exists(file_path):
            os.remove(file_path)

    db.session.delete(trade)
    db.session.commit()

    flash('Trade deleted successfully.', 'info')
    return redirect(url_for('view_trades'))


# ─────────────────────────────────────────────────────────
# Run
# ─────────────────────────────────────────────────────────
if __name__ == '__main__':
    with app.app_context():
        from models import User, Trade
        db.create_all()
    app.run(debug=True)
