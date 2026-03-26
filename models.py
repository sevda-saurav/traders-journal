# models.py
# ─────────────────────────────────────────────────────────
# This file defines our database TABLES as Python classes.
# Each class = one table. Each attribute = one column.
# Flask-SQLAlchemy translates these classes into SQL for us.
# ─────────────────────────────────────────────────────────

from extensions import db
from flask_login import UserMixin
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash


class User(UserMixin, db.Model):
    """
    Represents the 'user' table in our database.
    
    UserMixin is a helper from flask-login. It automatically adds
    4 required properties to our User class:
      - is_authenticated → True if user is logged in
      - is_active        → True (we don't ban users for now)
      - is_anonymous     → False for real users
      - get_id()         → Returns the user's ID as a string
    """

    # Table name in the database (optional, SQLAlchemy auto-names it)
    __tablename__ = 'users'

    # ── Columns ───────────────────────────────────────────
    # primary_key=True → this is the unique ID for each user (auto-increments)
    id = db.Column(db.Integer, primary_key=True)

    # nullable=False → this field CANNOT be empty
    # unique=True → no two users can have the same username
    username = db.Column(db.String(80), nullable=False, unique=True)

    email = db.Column(db.String(120), nullable=False, unique=True)

    # We store the HASH, not the real password
    password_hash = db.Column(db.String(256), nullable=False)

    # default=datetime.utcnow → automatically sets when user is created
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    trades = db.relationship('Trade', backref='owner', lazy=True)
    # ── Password Methods ───────────────────────────────────
    def set_password(self, password):
        """
        Takes a plain text password, hashes it, and stores the hash.
        Example: user.set_password("mypassword123")
        """
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """
        Takes a plain text password and checks if it matches the stored hash.
        Returns True if correct, False if wrong.
        Example: user.check_password("mypassword123") → True or False
        """
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        """This is just for debugging — shows useful info when you print a User."""
        return f'<User {self.username}>'
    
class Trade(db.Model):
    """
    Represents the 'trades' table in our database.
    Each row = one trade entry by a user.
    """

    __tablename__ = 'trades'

    # ── Primary Key ────────────────────────────────────────
    id = db.Column(db.Integer, primary_key=True)

    # ── Foreign Key ────────────────────────────────────────
    # Links each trade to the user who created it.
    # ForeignKey('users.id') → references the id column in users table.
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    # ── Market Info ────────────────────────────────────────
    # Which market: Stock, Crypto, Forex, Commodity, Metal, Other
    market_name = db.Column(db.String(100), nullable=False)

    # If user selects "Other", they type a custom market name here
    custom_market = db.Column(db.String(100), nullable=True)

    # ── Trade Details ──────────────────────────────────────
    trade_date  = db.Column(db.DateTime, nullable=False)

    # Long = buying expecting price to go UP
    # Short = selling expecting price to go DOWN
    trade_type  = db.Column(db.String(10), nullable=False)   # 'Long' or 'Short'

    buy_value   = db.Column(db.Float, nullable=False)   # Entry price
    sell_value  = db.Column(db.Float, nullable=False)   # Exit price
    target      = db.Column(db.Float, nullable=False)   # Target price
    stop_loss   = db.Column(db.Float, nullable=False)   # Stop loss price
    capital     = db.Column(db.Float, nullable=False)   # Amount of money used

    # ── Auto-Calculated Fields ─────────────────────────────
    # These are calculated by Python, not entered by the user
    profit_loss = db.Column(db.Float, nullable=True)    # + means profit, - means loss
    risk_reward = db.Column(db.Float, nullable=True)    # e.g. 1:2 stored as 2.0

    # ── Extra Info ─────────────────────────────────────────
    description = db.Column(db.Text, nullable=True)     # Notes / analysis
    screenshot  = db.Column(db.String(255), nullable=True)  # File path of image

    created_at  = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at  = db.Column(db.DateTime, default=datetime.utcnow,
                            onupdate=datetime.utcnow)

    # ── Calculation Methods ────────────────────────────────
    def calculate_profit_loss(self):
        """
        Calculates profit or loss based on trade type.

        For LONG trade (you buy low, sell high):
            P&L = (sell_value - buy_value) / buy_value * 100
            Positive = profit, Negative = loss

        For SHORT trade (you sell high, buy back low):
            P&L = (buy_value - sell_value) / buy_value * 100
            Positive = profit, Negative = loss

        Result is stored as a PERCENTAGE.
        Example: 5.25 means 5.25% profit
        """
        if self.trade_type == 'Long':
            pnl = ((self.sell_value - self.buy_value) / self.buy_value) * 100
        else:  # Short
            pnl = ((self.buy_value - self.sell_value) / self.buy_value) * 100

        self.profit_loss = round(pnl, 2)
        return self.profit_loss

    def calculate_risk_reward(self):
        """
        Calculates Risk-to-Reward Ratio.

        Risk   = how much you could LOSE (entry to stop loss)
        Reward = how much you could GAIN (entry to target)

        Formula:
            Risk   = |entry - stop_loss|
            Reward = |target - entry|
            R:R    = Reward / Risk

        Example: Risk=50, Reward=150 → R:R = 3.0 (means 1:3)
        Stored as: 3.0 (we display it as "1 : 3.0")
        """
        risk   = abs(self.buy_value - self.stop_loss)
        reward = abs(self.target - self.buy_value)

        if risk == 0:
            self.risk_reward = 0
        else:
            self.risk_reward = round(reward / risk, 2)

        return self.risk_reward

    @property
    def market_display(self):
        """Returns the market name to display — custom if 'Other'."""
        if self.market_name == 'Other' and self.custom_market:
            return self.custom_market
        return self.market_name

    @property
    def is_profit(self):
        """Returns True if this trade was profitable."""
        return self.profit_loss is not None and self.profit_loss > 0

    def __repr__(self):
        return f'<Trade {self.id} - {self.market_name} - {self.trade_type}>'