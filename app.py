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
import csv
import io
from flask import Response
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import (SimpleDocTemplate, Table,
                                TableStyle, Paragraph,
                                Spacer)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT

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
@login_required
def dashboard():
    """
    Fetches all trades for current user and calculates
    summary statistics to display on the dashboard.
    """
    from models import Trade

    # ── Fetch all trades for current user ─────────────────
    trades = Trade.query.filter_by(
        user_id=current_user.id
    ).order_by(Trade.trade_date.asc()).all()

    # ── Basic Counts ──────────────────────────────────────
    total_trades  = len(trades)

    # List of all profitable trades
    winning_trades = [t for t in trades if t.profit_loss and t.profit_loss > 0]

    # List of all losing trades
    losing_trades  = [t for t in trades if t.profit_loss and t.profit_loss < 0]

    total_wins   = len(winning_trades)
    total_losses = len(losing_trades)

    # ── Win Rate ──────────────────────────────────────────
    # Win Rate = (wins / total) * 100
    # Round to 2 decimal places
    win_rate = round((total_wins / total_trades) * 100, 2) if total_trades > 0 else 0

    # ── Total Profit & Loss ───────────────────────────────
    # Sum all P&L percentages
    total_pnl = round(sum(t.profit_loss for t in trades if t.profit_loss), 2)

    # ── Best and Worst Trade ──────────────────────────────
    best_trade  = max(trades, key=lambda t: t.profit_loss or 0) if trades else None
    worst_trade = min(trades, key=lambda t: t.profit_loss or 0) if trades else None

    # ── Average Risk:Reward ───────────────────────────────
    rr_values = [t.risk_reward for t in trades if t.risk_reward]
    avg_rr    = round(sum(rr_values) / len(rr_values), 2) if rr_values else 0

    # ── Recent 5 Trades ───────────────────────────────────
    # Reverse to get newest first for the recent trades table
    recent_trades = sorted(trades, key=lambda t: t.trade_date, reverse=True)[:5]

    # ── Chart Data — P&L Over Time ────────────────────────
    # We need two lists for the line chart:
    # labels = dates,  values = P&L percentages
    chart_labels = []
    chart_values = []
    cumulative   = 0  # running total P&L

    for trade in trades:  # already sorted by date asc
        chart_labels.append(trade.trade_date.strftime('%d %b'))
        cumulative += trade.profit_loss or 0
        chart_values.append(round(cumulative, 2))

    # ── Chart Data — Market Distribution ──────────────────
    # Count how many trades per market
    # Example: {'Crypto': 5, 'Forex': 3, 'Indian Stock Market': 7}
    market_counts = {}
    for trade in trades:
        market = trade.market_display
        market_counts[market] = market_counts.get(market, 0) + 1

    # ── Pass everything to the template ───────────────────
    return render_template(
        'dashboard.html',

        # Stats
        total_trades  = total_trades,
        total_wins    = total_wins,
        total_losses  = total_losses,
        win_rate      = win_rate,
        total_pnl     = total_pnl,
        avg_rr        = avg_rr,
        best_trade    = best_trade,
        worst_trade   = worst_trade,

        # Tables
        recent_trades = recent_trades,

        # Chart data (converted to lists for JavaScript)
        chart_labels  = chart_labels,
        chart_values  = chart_values,
        market_labels = list(market_counts.keys()),
        market_values = list(market_counts.values()),
    )

# ─────────────────────────────────────────────────────────
# EXPORT ROUTE 6: CSV Export
# ─────────────────────────────────────────────────────────
@app.route('/export/csv')
@login_required
def export_csv():
    """
    Generates a CSV file of all trades for the current user
    and sends it as a downloadable file.

    We use Python's built-in 'csv' module.
    io.StringIO() creates an in-memory text buffer —
    like a virtual text file that never touches the disk.
    """
    from models import Trade

    # Fetch all trades for current user
    trades = Trade.query.filter_by(
        user_id=current_user.id
    ).order_by(Trade.trade_date.desc()).all()

    # ── Create in-memory text buffer ──────────────────────
    output = io.StringIO()
    writer = csv.writer(output)

    # ── Write header row ──────────────────────────────────
    writer.writerow([
        'Date',
        'Market',
        'Trade Type',
        'Entry Price',
        'Exit Price',
        'Target',
        'Stop Loss',
        'Capital Used',
        'Profit/Loss %',
        'Risk:Reward',
        'Notes'
    ])

    # ── Write one row per trade ───────────────────────────
    for trade in trades:
        writer.writerow([
            trade.trade_date.strftime('%Y-%m-%d %H:%M'),
            trade.market_display,
            trade.trade_type,
            trade.buy_value,
            trade.sell_value,
            trade.target,
            trade.stop_loss,
            trade.capital,
            f"{trade.profit_loss}%" if trade.profit_loss else 'N/A',
            f"1:{trade.risk_reward}" if trade.risk_reward else 'N/A',
            trade.description or ''
        ])

    # ── Move cursor to start of buffer ────────────────────
    output.seek(0)

    # ── Create filename with current date ─────────────────
    filename = f"trades_{current_user.username}_{datetime.now().strftime('%Y%m%d')}.csv"

    # ── Send file as download response ────────────────────
    # 'text/csv' tells the browser this is a CSV file
    # 'Content-Disposition: attachment' forces download
    return Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={
            'Content-Disposition': f'attachment; filename={filename}'
        }
    )


# ─────────────────────────────────────────────────────────
# EXPORT ROUTE 7: PDF Export
# ─────────────────────────────────────────────────────────
@app.route('/export/pdf')
@login_required
def export_pdf():
    """
    Generates a formatted PDF report of all trades
    and sends it as a downloadable file.

    We use ReportLab to build the PDF.
    io.BytesIO() creates an in-memory binary buffer —
    like a virtual binary file that never touches the disk.
    """
    from models import Trade

    # Fetch all trades
    trades = Trade.query.filter_by(
        user_id=current_user.id
    ).order_by(Trade.trade_date.desc()).all()

    # ── Calculate summary stats for PDF header ─────────────
    total_trades   = len(trades)
    winning_trades = [t for t in trades if t.profit_loss and t.profit_loss > 0]
    total_wins     = len(winning_trades)
    win_rate       = round((total_wins / total_trades) * 100, 2) if total_trades > 0 else 0
    total_pnl      = round(sum(t.profit_loss for t in trades if t.profit_loss), 2)

    # ── Create in-memory binary buffer ────────────────────
    buffer = io.BytesIO()

    # ── Set up PDF document (landscape A4 for wide table) ─
    doc = SimpleDocTemplate(
        buffer,
        pagesize=landscape(A4),
        rightMargin=1*cm,
        leftMargin=1*cm,
        topMargin=1.5*cm,
        bottomMargin=1.5*cm
    )

    # ── Define styles ──────────────────────────────────────
    styles = getSampleStyleSheet()

    # Custom title style
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Title'],
        fontSize=18,
        textColor=colors.HexColor('#00d4aa'),
        spaceAfter=6,
        alignment=TA_CENTER
    )

    # Custom subtitle style
    subtitle_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.HexColor('#718096'),
        spaceAfter=4,
        alignment=TA_CENTER
    )

    # Custom normal style
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=8,
        textColor=colors.HexColor('#e0e0e0'),
        alignment=TA_LEFT
    )

    # ── Build PDF content list ─────────────────────────────
    # ReportLab works by building a list of "flowables"
    # (elements that flow down the page)
    content = []

    # ── Title ─────────────────────────────────────────────
    content.append(Paragraph("📈 Trader's Personal Journal", title_style))
    content.append(Paragraph(
        f"Trade Report for {current_user.username} — "
        f"Generated on {datetime.now().strftime('%d %B %Y')}",
        subtitle_style
    ))
    content.append(Spacer(1, 0.4*cm))

    # ── Summary Stats Row ─────────────────────────────────
    summary_data = [
        ['Total Trades', 'Winning Trades',
         'Win Rate', 'Total P&L'],
        [
            str(total_trades),
            str(total_wins),
            f"{win_rate}%",
            f"{'+' if total_pnl >= 0 else ''}{total_pnl}%"
        ]
    ]

    summary_table = Table(
        summary_data,
        colWidths=[6*cm, 6*cm, 6*cm, 6*cm]
    )

    summary_table.setStyle(TableStyle([
        # Header row
        ('BACKGROUND',  (0,0), (-1,0), colors.HexColor('#1a1d27')),
        ('TEXTCOLOR',   (0,0), (-1,0), colors.HexColor('#a0aec0')),
        ('FONTNAME',    (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE',    (0,0), (-1,0), 9),
        ('ALIGN',       (0,0), (-1,-1), 'CENTER'),
        ('VALIGN',      (0,0), (-1,-1), 'MIDDLE'),
        ('ROWBACKGROUNDS', (0,1), (-1,-1),
            [colors.HexColor('#0f1117')]),
        ('TEXTCOLOR',   (0,1), (-1,-1), colors.HexColor('#ffffff')),
        ('FONTNAME',    (0,1), (-1,-1), 'Helvetica-Bold'),
        ('FONTSIZE',    (0,1), (-1,-1), 14),
        ('TOPPADDING',  (0,0), (-1,-1), 8),
        ('BOTTOMPADDING',(0,0), (-1,-1), 8),
        ('GRID',        (0,0), (-1,-1), 0.5,
            colors.HexColor('#2d3748')),
        ('ROUNDEDCORNERS', [4]),
    ]))

    content.append(summary_table)
    content.append(Spacer(1, 0.6*cm))

    # ── Trades Table ──────────────────────────────────────
    if trades:
        # Table header
        table_data = [[
            'Date', 'Market', 'Type',
            'Entry', 'Exit', 'Capital',
            'P&L %', 'R:R', 'Notes'
        ]]

        # Table rows
        for trade in trades:
            # Truncate long notes to fit in cell
            notes = (trade.description or '')[:40]
            if len(trade.description or '') > 40:
                notes += '...'

            pnl_text = f"{trade.profit_loss}%" if trade.profit_loss else 'N/A'
            rr_text  = f"1:{trade.risk_reward}" if trade.risk_reward else 'N/A'

            table_data.append([
                trade.trade_date.strftime('%d %b %Y'),
                trade.market_display,
                trade.trade_type,
                f"Rs.{trade.buy_value}",
                f"Rs.{trade.sell_value}",
                f"Rs.{trade.capital}",
                pnl_text,
                rr_text,
                notes
            ])

        # Column widths (must add up to page width)
        col_widths = [
            2.8*cm,  # Date
            3.5*cm,  # Market
            2.0*cm,  # Type
            2.8*cm,  # Entry
            2.8*cm,  # Exit
            2.8*cm,  # Capital
            2.0*cm,  # P&L
            1.8*cm,  # R:R
            5.5*cm,  # Notes
        ]

        trades_table = Table(
            table_data,
            colWidths=col_widths,
            repeatRows=1  # Repeat header on each page
        )

        # Build row colors based on profit/loss
        row_styles = [
            # Header styles
            ('BACKGROUND',   (0,0), (-1,0), colors.HexColor('#00d4aa')),
            ('TEXTCOLOR',    (0,0), (-1,0), colors.HexColor('#0f1117')),
            ('FONTNAME',     (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE',     (0,0), (-1,0), 8),
            ('ALIGN',        (0,0), (-1,0), 'CENTER'),
            ('TOPPADDING',   (0,0), (-1,-1), 6),
            ('BOTTOMPADDING',(0,0), (-1,-1), 6),
            ('LEFTPADDING',  (0,0), (-1,-1), 6),
            ('FONTSIZE',     (0,1), (-1,-1), 7.5),
            ('GRID',         (0,0), (-1,-1), 0.3,
                colors.HexColor('#2d3748')),
            ('VALIGN',       (0,0), (-1,-1), 'MIDDLE'),
        ]

        # Color each data row based on profit or loss
        for i, trade in enumerate(trades, start=1):
            if trade.profit_loss and trade.profit_loss > 0:
                # Profit row — subtle green
                row_styles.append((
                    'BACKGROUND',
                    (0,i), (-1,i),
                    colors.HexColor('#0d2b1e')
                ))
                row_styles.append((
                    'TEXTCOLOR',
                    (6,i), (6,i),
                    colors.HexColor('#00d4aa')
                ))
            else:
                # Loss row — subtle red
                row_styles.append((
                    'BACKGROUND',
                    (0,i), (-1,i),
                    colors.HexColor('#2b0d0d')
                ))
                row_styles.append((
                    'TEXTCOLOR',
                    (6,i), (6,i),
                    colors.HexColor('#fc4f4f')
                ))

            # Normal text color for other columns
            row_styles.append((
                'TEXTCOLOR',
                (0,i), (5,i),
                colors.HexColor('#e0e0e0')
            ))
            row_styles.append((
                'TEXTCOLOR',
                (7,i), (8,i),
                colors.HexColor('#e0e0e0')
            ))

        trades_table.setStyle(TableStyle(row_styles))
        content.append(trades_table)

    else:
        content.append(Paragraph("No trades found.", normal_style))

    # ── Footer note ───────────────────────────────────────
    content.append(Spacer(1, 0.5*cm))
    content.append(Paragraph(
        f"© {datetime.now().year} Trader's Personal Journal — "
        f"Confidential Report",
        subtitle_style
    ))

    # ── Build PDF ─────────────────────────────────────────
    doc.build(content)

    # ── Move buffer cursor to start ───────────────────────
    buffer.seek(0)

    # ── Create filename ───────────────────────────────────
    filename = (f"trades_{current_user.username}_"
                f"{datetime.now().strftime('%Y%m%d')}.pdf")

    # ── Send PDF as download ──────────────────────────────
    return Response(
        buffer.getvalue(),
        mimetype='application/pdf',
        headers={
            'Content-Disposition': f'attachment; filename={filename}'
        }
    )


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
