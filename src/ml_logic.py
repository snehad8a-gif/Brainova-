import pandas as pd
import random

def get_motivational_message(streak):
    """Return a message based on streak length for Brainova users."""
    if streak == 0:
        return random.choice([
            "Every Brainova journey begins with a single step. Start today!",
            "Don't worry about yesterday. Today is a new opportunity to grow with Brainova.",
            "Small progress is still progress. Let's get started!"
        ])
    elif streak < 3:
        return random.choice([
            "You're off to a great start on Brainova! Keep it up!",
            "Consistency is key. You're building momentum in your Brainova routine.",
            "Great job! Two days in a row!"
        ])
    elif streak < 7:
        return random.choice([
            "You're on fire! 🔥 Brainova looks good on you.",
            "Almost a full week! Don't break your Brainova chain!",
            "You are becoming unstoppable."
        ])
    else:
        return random.choice([
            "Legendary streak! 🏆 You're a Brainova pro.",
            "This habit is now part of you. Brainova is proud!",
            "Incredible dedication. Use this energy for other goals too!"
        ])

def get_smart_suggestions(habits, logs):
    """
    Analyze logs to find patterns and suggest improvements for Brainova users.
    """
    if logs.empty or habits.empty:
        return ["Start logging your habits on Brainova to get smart insights!"]
    
    suggestions = []
    
    # Analyze skipped days (simple heuristic)
    logs['date'] = pd.to_datetime(logs['date'])
    logs['weekday'] = logs['date'].dt.day_name()
    
    weekday_counts = logs['weekday'].value_counts()
    
    if not weekday_counts.empty:
        best_day = weekday_counts.idxmax()
        suggestions.append(f"💡 You are most consistent on **{best_day}s**. Try to schedule your hardest Brainova tasks then!")
    
    # Streak check
    for _, habit in habits.iterrows():
        habit_logs = logs[logs['habit_id'] == habit['id']]
        if habit_logs.empty:
            suggestions.append(f"👀 You haven't started **{habit['name']}** on Brainova yet. How about doing just 5 minutes today?")
    
    if not suggestions:
        suggestions.append("🌟 You are doing great! Keep tracking on Brainova to unlock more insights.")
        
    return suggestions