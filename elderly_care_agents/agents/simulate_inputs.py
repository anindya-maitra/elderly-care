import random
from datetime import datetime

def generate_fake_health_data():
    return {
        "heart_rate": random.randint(60, 100),
        "glucose": random.randint(70, 160),
        "spo2": random.randint(92, 100)
    }

def generate_fake_safety_data():
    return {
        "movement_detected": random.choice([0, 1]),
        "fall_detected": random.choice([0, 1]),
        "inactivity_minutes": random.randint(5, 60),
        "location": random.choice([0, 1])  # 0: inside, 1: outside
    }

def generate_current_time():
    return datetime.now().strftime("%H:%M:%S")
