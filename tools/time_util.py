from datetime import datetime


day_in_seconds = 3600 * 24
hour_in_seconds = 3600

def get_current_time():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")