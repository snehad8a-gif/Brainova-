import streamlit as st
import pandas as pd
from datetime import datetime
import json
from src.database import run_query, init_db
from src.gamification import calculate_xp_gain, get_level_info, BADGES

# --- BRAINOVA GAMIFICATION DB ---
def init_gamification_db():
    """Ensure user_progress table exists for Brainova."""
    # 1. Create table with minimal schema if it doesn't exist
    query = """
        CREATE TABLE IF NOT EXISTS user_progress (
            id INTEGER PRIMARY KEY,
            total_xp INTEGER DEFAULT 0
        )
    """
    run_query(query)
    
    # 2. Check schema using PRAGMA (Robust Migration)
    res = run_query("PRAGMA table_info(user_progress)")
    existing_columns = [row['name'] for row in res] if res else []
    
    if "unlocked_badges" not in existing_columns:
        try:
            run_query("ALTER TABLE user_progress ADD COLUMN unlocked_badges TEXT DEFAULT '[]'")
        except Exception as e:
            st.error(f"Brainova Migration failed: {e}")

    # 3. Ensure default user row exists
    check = run_query("SELECT id FROM user_progress WHERE id = 1")
    if not check:
        run_query("INSERT INTO user_progress (id, total_xp, unlocked_badges) VALUES (1, 0, '[]')")

# Initialize Brainova DBs
init_db()
init_gamification_db()

def get_user_progress():
    """Fetch current Brainova user progress."""
    res = run_query("SELECT total_xp, unlocked_badges FROM user_progress WHERE id = 1")
    if res:
        # Note: res[0] is the row, res[0][0] is XP, res[0][1] is JSON
        xp, badges_json = res[0]
        return {"total_xp": xp, "unlocked_badges": json.loads(badges_json)}
    return {"total_xp": 0, "unlocked_badges": []}

def update_user_progress(xp_delta, new_badges=None):
    """Add XP and save new Brainova badges."""
    curr = get_user_progress()
    new_xp = curr['total_xp'] + xp_delta
    badges = curr['unlocked_badges']
    
    if new_badges:
        for b in new_badges:
            if b not in badges:
                badges.append(b)
    
    run_query(
        "UPDATE user_progress SET total_xp = ?, unlocked_badges = ? WHERE id = 1",
        (new_xp, json.dumps(badges))
    )
    return new_xp, badges

# --- BRAINOVA HABIT TRACKING ---

def load_habits(active_only=True):
    """Load all Brainova habits from SQLite."""
    query = "SELECT * FROM habits"
    if active_only:
        query += " WHERE is_active = 1"
    query += " ORDER BY created_at DESC"
    
    df = run_query(query, return_df=True)
    if df.empty:
        return pd.DataFrame(columns=['id', 'name', 'category', 'frequency_type', 'frequency_value', 'target_value', 'target_unit', 'created_at', 'is_active'])
    return df

def log_habit_completion(habit_id, date, status="Completed", notes="", value=1):
    """
    Log a Brainova habit completion and process rewards.
    """
    # Check for existing log
    check_query = "SELECT id FROM logs WHERE habit_id = ? AND date = ?"
    existing = run_query(check_query, (habit_id, str(date)))
    
    if existing:
        return False, {}
        
    query = """
        INSERT INTO logs (habit_id, date, status, notes, value)
        VALUES (?, ?, ?, ?, ?)
    """
    try:
        run_query(query, (habit_id, str(date), status, notes, value))
        
        # --- BRAINOVA REWARD LOGIC ---
        h_res = run_query("SELECT * FROM habits WHERE id = ?", (habit_id,), return_df=True)
        if not h_res.empty:
            habit = h_res.iloc[0]
            l_res = run_query("SELECT * FROM logs WHERE habit_id = ?", (habit_id,), return_df=True)
            
            # Local import to prevent circular dependencies
            from src.analytics import calculate_streaks
            current_streak = calculate_streaks(habit, l_res)
            prev_streak = max(0, current_streak - 1)
            
            xp = calculate_xp_gain(current_streak, prev_streak)
            
            # Badge Checks
            candidate_badges = []
            curr_progress = get_user_progress()
            existing_badges = curr_progress['unlocked_badges']
            
            if current_streak == 7: candidate_badges.append('week_warrior')
            if current_streak == 30: candidate_badges.append('month_master')
            if curr_progress['total_xp'] == 0: candidate_badges.append('first_step')
            
            day_count_res = run_query("SELECT COUNT(*) FROM logs WHERE date = ?", (str(date),))
            if day_count_res and day_count_res[0][0] == 3:
                candidate_badges.append('hat_trick')
                
            new_badges_unlocked = [b for b in candidate_badges if b not in existing_badges]
            new_xp_total, _ = update_user_progress(xp, new_badges_unlocked)
            
            curr_lvl, _ = get_level_info(new_xp_total)
            prev_lvl, _ = get_level_info(new_xp_total - xp)
            level_up = (curr_lvl['level'] > prev_lvl['level'])
            
            return True, {
                "xp_earned": xp,
                "level_up": level_up,
                "current_level": curr_lvl,
                "new_badges": new_badges_unlocked
            }
            
        return True, {"xp_earned": 0}
        
    except Exception as e:
        st.error(f"Brainova Logging Error: {e}")
        return False, {}

# --- BRAINOVA TASKS & PROJECTS ---

def add_reminder(text, priority='low'):
    """Add a quick reminder to Brainova."""
    query = "INSERT INTO reminders (text, priority) VALUES (?, ?)"
    try:
        run_query(query, (text, priority))
        return True
    except Exception as e:
        st.error(f"Error adding Brainova reminder: {e}")
        return False

def add_project(text, description, priority='low'):
    """Add a long-term project to Brainova."""
    query = "INSERT INTO projects (text, description, priority) VALUES (?, ?, ?)"
    try:
        run_query(query, (text, description, priority))
        return True
    except Exception as e:
        st.error(f"Error adding Brainova project: {e}")
        return False