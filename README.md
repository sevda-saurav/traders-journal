# 📈 Trader's Personal Journal

A full-stack web application for traders to log, track,
and analyze their trades.

## 🚀 Features

- Secure Login & Signup with password hashing
- Add, Edit, Delete trade entries
- Auto-calculated Profit/Loss and Risk:Reward Ratio
- Screenshot upload for trade charts
- Analytics Dashboard with summary stats
- Export trades as CSV or PDF

## 🛠️ Tech Stack

- **Backend:** Python, Flask, Flask-SQLAlchemy, Flask-Login
- **Database:** SQLite
- **Frontend:** HTML, CSS, JavaScript

## ⚙️ How to Run Locally

# 1. Clone the repository

git clone https://github.com/sevda-saurav/traders-journal.git
cd traders-journal

# 2. Create virtual environment

python -m venv venv
venv\Scripts\activate # Windows
source venv/bin/activate # Mac/Linux

# 3. Install dependencies

pip install -r requirements.txt

# 4. Run the app

python app.py

# 5. Open in browser

http://127.0.0.1:5000

## 📁 Project Structure

trader_journal/
├── app.py ← Main Flask application
├── models.py ← Database models
├── config.py ← App configuration
├── requirements.txt ← Dependencies
├── static/ ← CSS, JS, Images
└── templates/ ← HTML templates

## 👨‍💻 Author

Your Name — github.com/sevda-saurav
