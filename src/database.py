import sqlite3
import os
from datetime import datetime
import pandas as pd
from dotenv import load_dotenv

# Load environment variables for Brainova
load_dotenv()

# Default path if env var not set - Updated to reflect Brainova branding
DB_PATH = os.getenv("BRAINOVA_DB_PATH", "data/brainova_habits.db")

def get_db_connection():
    """Create a database connection to the Brainova SQLite database."""
    # Ensure data directory exists
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Return rows as dictionaries
    return conn

def init_db():
    """Initialize the Brainova database with core tracking and gamification tables."""
    conn = get_db_connection()
    c = conn.cursor()
    
    # Brainova Habits Table
    # Stores the primary habits/rituals for the user
    c.execute('''
        CREATE TABLE IF NOT EXISTS habits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT,
            frequency_type TEXT DEFAULT 'daily',
            frequency_value TEXT,
            target_value INTEGER DEFAULT 1,
            target_unit TEXT DEFAULT 'times',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_active BOOLEAN DEFAULT 1
        )
    ''')
    
    # Brainova Logs Table
    # Tracks the completion of habits and brain-building activities
    c.execute('''
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            habit_id INTEGER,
            date DATE,
            value INTEGER DEFAULT 1,
            status TEXT DEFAULT 'Completed',
            notes TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (habit_id) REFERENCES habits (id)
        )
    ''')
    
    # Brainova Reminders Table
    c.execute('''
        CREATE TABLE IF NOT EXISTS reminders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            text TEXT NOT NULL,
            priority TEXT DEFAULT 'medium',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_completed BOOLEAN DEFAULT 0
        )
    ''')

    # Brainova Projects Table
    # For long-term goals or study modules in the Brainova ecosystem
    c.execute('''
        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            text TEXT NOT NULL,
            description TEXT,
            priority TEXT DEFAULT 'medium',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_completed BOOLEAN DEFAULT 0
        )
    ''')

    # Brainova Gamification: User Progress Table
    # Tracks the XP and Leveling system core to the Brainova experience
    c.execute('''
        CREATE TABLE IF NOT EXISTS user_progress (
            id INTEGER PRIMARY KEY CHECK (id = 1),
            total_xp INTEGER DEFAULT 0,
            current_level INTEGER DEFAULT 1,
            last_login DATE
        )
    ''')
    
    # Initialize Brainova user progress if not exists
    c.execute('INSERT OR IGNORE INTO user_progress (id, total_xp, current_level) VALUES (1, 0, 1)')
    
    conn.commit()
    conn.close()
    return True

def run_query(query, params=(), return_df=False):
    """Execute a query against the Brainova database."""
    conn = get_db_connection()
    try:
        if return_df:
            return pd.read_sql_query(query, conn, params=params)
        
        c = conn.cursor()
        c.execute(query, params)
        if query.strip().upper().startswith(("INSERT", "UPDATE", "DELETE")):
            conn.commit()
            return c.lastrowid
        else:
            return c.fetchall()
    except Exception as e:
        print(f"Brainova Database Error: {e}")
        return None
    finally:
        conn.close()