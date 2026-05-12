import pandas as pd
import datetime

def is_habit_due(habit, date_check):
    """
    Brainova Core Logic: Check if a study habit or task is due on a specific date.
    Supports Brainova's frequency types: Daily, Weekly, Bi-weekly, Monthly, 
    Bi-monthly, Custom (X days), and Specific Days.
    """
    # Normalize date_check to date object for Brainova scheduling
    if isinstance(date_check, str):
        date_check = pd.to_datetime(date_check).date()
    elif isinstance(date_check, pd.Timestamp):
        date_check = date_check.date()
    elif isinstance(date_check, datetime.datetime):
        date_check = date_check.date()
        
    # Parse Brainova habit creation date safely
    try:
        created_at = pd.to_datetime(habit['created_at']).date()
    except (KeyError, ValueError, TypeError):
        # Fallback to current check date if metadata is missing
        created_at = date_check 
        
    # If the Brainova habit was created after the check date, it isn't due yet
    if date_check < created_at:
        return False

    ftype = habit.get('frequency_type', 'daily')
    fvalue = habit.get('frequency_value')
    
    if ftype == 'daily':
        return True
    
    elif ftype == 'days_of_week':
        # Brainova value example: "Mon,Wed,Fri"
        if not fvalue: return False
        day_name = date_check.strftime("%a") # Mon, Tue...
        return day_name in fvalue
        
    elif ftype == 'weekly':
        # Brainova value: "Mon", "Tue" etc.
        if not fvalue: return False
        day_name = date_check.strftime("%a")
        return day_name == fvalue
        
    elif ftype == 'biweekly':
        # Brainova interval: Every 2 weeks on a specific day
        if not fvalue: return False
        day_name = date_check.strftime("%a")
        if day_name != fvalue: return False
        
        # Calculate weeks since Brainova habit inception
        delta_days = (date_check - created_at).days
        week_diff = delta_days // 7
        return (week_diff % 2) == 0
        
    elif ftype == 'monthly':
        # Brainova value: "1", "15" etc.
        try:
            target_day = int(fvalue)
        except (ValueError, TypeError):
            return False
            
        return date_check.day == target_day
        
    elif ftype == 'bimonthly':
        # Brainova interval: Every 2 months on a specific day of the month
        try:
            target_day = int(fvalue)
        except (ValueError, TypeError):
            return False
            
        if date_check.day != target_day: return False
        
        # Check Brainova month parity
        current_months = date_check.year * 12 + date_check.month
        created_months = created_at.year * 12 + created_at.month
        diff = current_months - created_months
        return (diff % 2) == 0
        
    elif ftype == 'custom':
        # Brainova Custom: Every X days
        try:
            interval = int(fvalue)
        except (ValueError, TypeError):
            return False # Fixed: returns False instead of 1 if fvalue is invalid
        
        if interval < 1: interval = 1
        delta_days = (date_check - created_at).days
        return (delta_days % interval) == 0
        
    return True