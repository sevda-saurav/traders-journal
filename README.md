# 📈 Trader's Personal Journal

<div align="center">
![Python](https://img.shields.io/badge/Python-3.8+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-3.0+-000000?style=for-the-badge&logo=flask&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-003B57?style=for-the-badge&logo=sqlite&logoColor=white)
![HTML5](https://img.shields.io/badge/HTML5-E34F26?style=for-the-badge&logo=html5&logoColor=white)
![CSS3](https://img.shields.io/badge/CSS3-1572B6?style=for-the-badge&logo=css3&logoColor=white)
![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black)
 
**A full-stack web application for traders to log, track, and analyze their trades.**
 
[Features](#-features) • [Demo](#-screenshots) • [Installation](#-installation) • [Usage](#-usage) • [Tech Stack](#-tech-stack) • [Project Structure](#-project-structure)
 
</div>
---
 
## 📌 Overview
 
**Trader's Personal Journal** is a secure, full-stack web application built with Python and Flask. It allows traders to maintain a detailed digital journal of their trades — tracking entries, exits, profit/loss, risk-to-reward ratios, and performance analytics — all in one place.
 
Whether you trade **Indian Stock Market, Crypto, Forex, Commodities, or Metals**, this app helps you stay disciplined, learn from your trades, and improve over time.
 
---
 
## ✨ Features
 
### 🔐 Authentication & Security
- Secure **Signup and Login** system
- **Password hashing** using Werkzeug — plain text passwords never stored
- **Session management** with Flask-Login
- **Route protection** — private pages inaccessible without login
- **Ownership verification** — users can only access their own trades
### 📝 Trade Management (CRUD)
- **Add** new trade entries with complete details
- **Edit** existing trades with pre-filled forms
- **Delete** trades with confirmation prompt
- **View** all trades in a sortable, color-coded table
- Supports markets: Indian Stock Market, Crypto, Forex, Commodity, Metal, and Custom
### 📊 Trade Entry Fields
| Field | Description |
|-------|-------------|
| Market Name | Select from preset markets or enter custom |
| Date & Time | Precise timestamp for each trade |
| Trade Type | Long (Buy) or Short (Sell) |
| Entry Price | Price at which trade was opened |
| Exit Price | Price at which trade was closed |
| Target Price | Planned profit target |
| Stop Loss | Risk management level |
| Capital Used | Amount of money invested |
| Profit/Loss % | **Auto-calculated** from entry/exit |
| Risk:Reward Ratio | **Auto-calculated** from entry/target/SL |
| Notes | Personal analysis and observations |
| Screenshot | Upload chart images for reference |
 
### 📈 Analytics Dashboard
- **Summary Cards** — Total Trades, Wins, Losses, Win Rate, Total P&L, Avg R:R
- **Best & Worst Trade** highlights
- **Cumulative P&L Line Chart** — performance trend over time
- **Market Distribution Doughnut Chart** — which markets you trade most
- **Recent Trades Table** — quick glance at latest 5 trades
- All charts built with **Chart.js** — interactive and responsive
### 📤 Export Feature
- **Export as CSV** — open in Excel or Google Sheets
- **Export as PDF** — formatted report with color-coded profit/loss rows
- Filename includes username and date automatically
- PDF includes summary stats header + full trades table
### 💬 Feedback System
- Dedicated feedback form with category selection
- **Star rating** system (1–5 stars) — pure CSS, no JavaScript
- Name and email pre-filled from user account
- Feedback stored in database for future review
### 📱 Responsive Design
- **Mobile-friendly** with hamburger navigation menu
- Dark trader-themed UI with teal accent colors
- Active navigation link highlighting
- Auto-dismissing flash notifications
---
 
## 🛠️ Tech Stack
 
### Backend
| Technology | Purpose |
|-----------|---------|
| **Python 3.8+** | Core programming language |
| **Flask** | Lightweight web framework |
| **Flask-SQLAlchemy** | ORM for database operations |
| **Flask-Login** | User session management |
| **Werkzeug** | Password hashing + file utilities |
| **ReportLab** | PDF generation |
| **SQLite** | Lightweight file-based database |
 
### Frontend
| Technology | Purpose |
|-----------|---------|
| **HTML5** | Page structure and forms |
| **CSS3** | Custom dark-theme styling |
| **JavaScript (Vanilla)** | Form interactivity + live calculations |
| **Chart.js** | Interactive analytics charts |
| **Jinja2** | Server-side HTML templating |
 
---
 
## 📁 Project Structure
 
```
trader_journal/
│
├── app.py                      # Main Flask application & all routes
├── models.py                   # Database models (User, Trade, Feedback)
├── config.py                   # App configuration & settings
├── requirements.txt            # Python dependencies
│
├── instance/
│   └── journal.db              # SQLite database (auto-created)
│
├── static/
│   ├── css/
│   │   └── style.css           # All custom styles
│   ├── js/
│   │   └── main.js             # All custom JavaScript
│   └── uploads/                # User-uploaded trade screenshots
│
└── templates/
    ├── base.html               # Shared layout (navbar + footer)
    ├── index.html              # Landing / home page
    ├── dashboard.html          # Analytics dashboard
    ├── feedback.html           # Feedback form
    ├── auth/
    │   ├── login.html          # Login page
    │   └── signup.html         # Signup page
    └── trades/
        ├── add_trade.html      # Add new trade form
        ├── edit_trade.html     # Edit existing trade form
        └── view_trades.html    # All trades table
```
 
---
 
## ⚙️ Installation
 
### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)
- Git
### Step 1 — Clone the Repository
 
```bash
git clone https://github.com/YOUR_USERNAME/traders-journal.git
cd traders-journal
```
 
### Step 2 — Create Virtual Environment
 
```bash
# Create virtual environment
python -m venv venv
 
# Activate — Windows
venv\Scripts\activate
 
# Activate — Mac/Linux
source venv/bin/activate
```
 
> You should see `(venv)` at the start of your terminal line.
 
### Step 3 — Install Dependencies
 
```bash
pip install -r requirements.txt
```
 
### Step 4 — Run the Application
 
```bash
python app.py
```
 
### Step 5 — Open in Browser
 
```
http://127.0.0.1:5000
```
 
---
 
## 🚀 Usage
 
### Getting Started
1. Visit the home page and click **Sign Up**
2. Create your account with username, email and password
3. Log in with your credentials
4. Click **➕ Add Trade** to log your first trade
5. View your **Dashboard** to see performance analytics
6. Export your journal anytime as **CSV** or **PDF**
### Adding a Trade
1. Select your **Market** (Stock, Crypto, Forex, etc.)
2. Enter **Date & Time** of the trade
3. Choose **Trade Type** — Long or Short
4. Fill in **Entry Price, Exit Price, Target, Stop Loss, Capital**
5. Watch **P&L % and R:R** calculate live as you type
6. Add **Notes** for your analysis
7. Optionally upload a **Chart Screenshot**
8. Click **Save Trade**
### Exporting Trades
- Go to **My Trades** or **Dashboard**
- Click **📄 Export CSV** for Excel-compatible file
- Click **📑 Export PDF** for a formatted printable report
---
 
## 🗄️ Database Models
 
### User
```
id            → Primary Key
username      → Unique username
email         → Unique email address
password_hash → Hashed password (never plain text)
created_at    → Account creation timestamp
```
 
### Trade
```
id            → Primary Key
user_id       → Foreign Key → Users table
market_name   → Market category
custom_market → Custom market name (if Other)
trade_date    → Date and time of trade
trade_type    → Long or Short
buy_value     → Entry price
sell_value    → Exit price
target        → Target price
stop_loss     → Stop loss price
capital       → Capital used
profit_loss   → Auto-calculated P&L percentage
risk_reward   → Auto-calculated Risk:Reward ratio
description   → Notes and analysis
screenshot    → Uploaded chart image filename
created_at    → Record creation timestamp
updated_at    → Last update timestamp
```
 
### Feedback
```
id            → Primary Key
user_id       → Foreign Key → Users table
name          → Submitter name
email         → Submitter email
category      → Bug Report / Suggestion / General / Compliment
rating        → Star rating (1–5)
message       → Feedback message
created_at    → Submission timestamp
```
 
---
 
## 🔒 Security Features
 
- ✅ Passwords hashed with **PBKDF2-SHA256** via Werkzeug
- ✅ Session cookies **cryptographically signed** with SECRET_KEY
- ✅ All trade routes protected with `@login_required`
- ✅ **Ownership verification** on every edit and delete operation
- ✅ File uploads validated for **allowed extensions only**
- ✅ Filenames **sanitized** with `secure_filename()` before saving
- ✅ **DELETE operations use POST** — not GET — to prevent CSRF via links
- ✅ Database queries use **SQLAlchemy ORM** — no raw SQL, no SQL injection
---
 
## 📐 Key Calculations
 
### Profit & Loss
```
Long Trade:   P&L % = ((Exit - Entry) / Entry) × 100
Short Trade:  P&L % = ((Entry - Exit) / Entry) × 100
```
 
### Risk : Reward Ratio
```
Risk   = |Entry Price - Stop Loss|
Reward = |Target Price - Entry Price|
R:R    = Reward / Risk
Display: "1 : {R:R}"   e.g. "1 : 2.5"
```
 
---
 
## 🧪 Running in Development
 
```bash
# Debug mode is ON by default in app.py
# Auto-reloads on file save
# Detailed error pages in browser
 
python app.py
```
 
> ⚠️ **Note:** Never use `debug=True` in production deployment.
 
---
 
## 🌐 Deployment
 
### Deploy on Render (Free)
 
1. Push your code to GitHub
2. Go to [render.com](https://render.com) and sign up
3. Click **New Web Service** → Connect your GitHub repo
4. Set the following:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn app:app`
5. Add environment variable: `SECRET_KEY` → your secret string
6. Click **Deploy**
```bash
# Install gunicorn for production
pip install gunicorn
pip freeze > requirements.txt
```
 
---
 
## 🔮 Future Enhancements
 
- [ ] **Trade Tags** — Strategy, Breakout, Mistake, Reversal
- [ ] **Emotion Tracking** — Fear, Confidence, Greed, Neutral
- [ ] **Trade Rating** — Personal rating (1–5 stars) per trade
- [ ] **Advanced Filters** — Filter by market, date range, profit/loss
- [ ] **Weekly/Monthly Reports** — Automated performance summaries
- [ ] **Flask-Migrate** — Database migrations without data loss
- [ ] **Two-Factor Authentication** — Enhanced account security
- [ ] **Dark/Light Mode Toggle** — User preference
- [ ] **Mobile App** — React Native frontend
---
 
## 📚 What I Learned Building This
 
- Full-stack web development with **Python and Flask**
- **MVC architecture** — separating models, views, and controllers
- **Database design** — models, relationships, foreign keys
- **User authentication** — sessions, hashing, route protection
- **File handling** — secure uploads, validation, storage
- **Data visualization** — Chart.js with server-side data
- **Version control** — Git workflow, meaningful commits
- **Security best practices** — never trust user input
---
 
## 🤝 Contributing
 
Contributions, issues, and feature requests are welcome!
 
1. Fork the repository
2. Create a feature branch: `git checkout -b feature/new-feature`
3. Commit your changes: `git commit -m "Add new feature"`
4. Push to branch: `git push origin feature/new-feature`
5. Open a **Pull Request**
---
 
## 📄 License
 
This project is licensed under the **MIT License** — free to use, modify, and distribute.
 
---
 
## 👨‍💻 Author
 
**Saurav Sevda**
- GitHub: [@sevda-saurav](https://github.com/sevda-saurav)
- LinkedIn: [Saurav Sevda](https://www.linkedin.com/in/saurav-sevda-2288a4244/)
---
 
## 🙏 Acknowledgements
 
- [Flask Documentation](https://flask.palletsprojects.com/)
- [Flask-Login](https://flask-login.readthedocs.io/)
- [Chart.js](https://www.chartjs.org/)
- [ReportLab](https://www.reportlab.com/)
- [SQLAlchemy](https://www.sqlalchemy.org/)
---
 
<div align="center">
**⭐ If this project helped you, please give it a star on GitHub! ⭐**
 
*Built with ❤️ using Python + Flask | Track smarter, trade better.*
 
</div>
