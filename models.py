from app import db
from flask_login import UserMixin
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash


class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id            = db.Column(db.Integer, primary_key=True)
    username      = db.Column(db.String(80), nullable=False, unique=True)
    email         = db.Column(db.String(120), nullable=False, unique=True)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at    = db.Column(db.DateTime, default=datetime.utcnow)
    trades        = db.relationship('Trade', backref='owner', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'


class Trade(db.Model):
    __tablename__ = 'trades'

    id            = db.Column(db.Integer, primary_key=True)
    user_id       = db.Column(db.Integer, db.ForeignKey('users.id'),
                              nullable=False)
    market_name   = db.Column(db.String(100), nullable=False)
    custom_market = db.Column(db.String(100), nullable=True)
    trade_date    = db.Column(db.DateTime, nullable=False)
    trade_type    = db.Column(db.String(10), nullable=False)
    buy_value     = db.Column(db.Float, nullable=False)
    sell_value    = db.Column(db.Float, nullable=False)
    target        = db.Column(db.Float, nullable=False)
    stop_loss     = db.Column(db.Float, nullable=False)
    capital       = db.Column(db.Float, nullable=False)
    profit_loss   = db.Column(db.Float, nullable=True)
    risk_reward   = db.Column(db.Float, nullable=True)
    description   = db.Column(db.Text, nullable=True)
    screenshot    = db.Column(db.String(255), nullable=True)
    created_at    = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at    = db.Column(db.DateTime, default=datetime.utcnow,
                              onupdate=datetime.utcnow)

    def calculate_profit_loss(self):
        if self.trade_type == 'Long':
            pnl = ((self.sell_value - self.buy_value) / self.buy_value) * 100
        else:
            pnl = ((self.buy_value - self.sell_value) / self.buy_value) * 100
        self.profit_loss = round(pnl, 2)
        return self.profit_loss

    def calculate_risk_reward(self):
        risk   = abs(self.buy_value - self.stop_loss)
        reward = abs(self.target - self.buy_value)
        if risk == 0:
            self.risk_reward = 0
        else:
            self.risk_reward = round(reward / risk, 2)
        return self.risk_reward

    @property
    def market_display(self):
        if self.market_name == 'Other' and self.custom_market:
            return self.custom_market
        return self.market_name

    @property
    def is_profit(self):
        return self.profit_loss is not None and self.profit_loss > 0

    def __repr__(self):
        return f'<Trade {self.id} - {self.market_name}>'


# ─────────────────────────────────────────────────────────
# FEEDBACK MODEL — New in Step 6
# ─────────────────────────────────────────────────────────
class Feedback(db.Model):
    """
    Stores user feedback submissions.
    Linked to User so we know who submitted it.
    """
    __tablename__ = 'feedback'

    id         = db.Column(db.Integer, primary_key=True)

    # Optional link to user — nullable so even
    # guests could submit feedback in future
    user_id    = db.Column(db.Integer,
                           db.ForeignKey('users.id'),
                           nullable=True)

    name       = db.Column(db.String(100), nullable=False)
    email      = db.Column(db.String(120), nullable=False)

    # Category: Bug Report, Suggestion, General, Compliment
    category   = db.Column(db.String(50), nullable=False)

    # Rating 1-5
    rating     = db.Column(db.Integer, nullable=False, default=5)

    message    = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Feedback {self.id} - {self.category}>'