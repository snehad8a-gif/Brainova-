# Brainova

Brainova is a gamified, AI-powered study habit tracking app built with Streamlit. It helps students build consistent academic habits, track their progress, and stay motivated through smart suggestions and visual analytics.

---

## Features

Reminders — Set and manage sticky reminders for one-off tasks like submitting assignments or reviewing lecture notes, with color-coded priority levels (high, medium, low).

Daily Focus — See all your study habits scheduled for today and mark them as done as you go.

Smart Suggestions — AI-driven recommendations that help you stay on track and improve your study routines over time.

Analytics — Visualize your habit streaks, completion rates, and overall academic progress through clean charts and dashboards.

Settings — Edit or delete habits, manage your data, and customize the app to your preferences.

---

## Tech Stack

- Streamlit for the web UI
- Pandas for data management
- Custom Python modules handling the database, analytics, ML logic, and UI components

---

## Project Structure

app.py               # Main app
requirements.txt     # Dependencies
config/              # Config files
src/
  analytics.py       # Charts and analytics
  data_manager.py    # Data loading and saving
  database.py        # Database helpers
  ml_logic.py        # AI/ML logic
  ui_components.py   # Custom UI elements
  utils.py           # Utility functions
---

## Getting Started

1. Clone the repository and navigate into it
2. Run pip install -r requirements.txt
3. Start the app with streamlit run app.py

---

## About the AI Features

Brainova uses lightweight ML logic to generate motivational messages and habit suggestions based on your activity. Everything runs locally — no data is sent anywhere.
