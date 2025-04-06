import csv
from flask import Blueprint, render_template, request, jsonify
from agents.central_coordinator import CentralCoordinator
from agents import HealthMonitorAgent, SafetyMonitorAgent, ReminderAgent, ChatAgent
from agents import simulate_inputs, voice_output
from translate_text import translate_and_speak
import joblib
import pandas as pd
import datetime
import os
from collections import defaultdict

dashboard_bp = Blueprint('dashboard', __name__)

# Load models and reminders
health_model = joblib.load("models/health_alert_model.pkl")
safety_model = joblib.load("models/safety_alert_model.pkl")
reminder_df = pd.read_csv("data/daily_reminder.csv")

# Initialize agents
health_agent = HealthMonitorAgent(health_model)
safety_agent = SafetyMonitorAgent(safety_model)
reminder_agent = ReminderAgent(reminder_df)
chat_agent = ChatAgent()
coordinator = CentralCoordinator(health_agent, safety_agent, reminder_agent, chat_agent)

chat_history = []  # Global chat state

def generate_health_trends(days=7):
    trends = {
        "dates": [],
        "heart_rate": [],
        "spo2": [],
        "glucose": []
    }
    for i in range(days):
        date = (datetime.datetime.now() - datetime.timedelta(days=i)).strftime('%b %d')
        health = simulate_inputs.generate_fake_health_data()
        trends["dates"].insert(0, date)
        trends["heart_rate"].insert(0, health["heart_rate"])
        trends["spo2"].insert(0, health["spo2"])
        trends["glucose"].insert(0, health["glucose"])
    return trends

@dashboard_bp.route('/', methods=['GET', 'POST'])
def dashboard():
    global chat_history

    device_id = 'D11002'
    response = ""
    translated_response = ""

    try:
        health_df = pd.read_csv("data/health_monitoring.csv")
        health_row = health_df[health_df['Device-ID/User-ID'] == device_id].iloc[0]

        health_data = {
            "heart_rate": int(health_row['Heart Rate']),
            "glucose": float(health_row['Glucose Levels']),
            "spo2": int(health_row['Oxygen Saturation (SpO₂%)']),
        }
    except Exception as e:
        print(f"⚠️ Could not load health data: {e}")
        health_data = simulate_inputs.generate_fake_health_data()

    try:
        safety_df = pd.read_csv("data/safety_monitoring.csv")
        safety_row = safety_df[safety_df['Device-ID/User-ID'] == device_id].iloc[0]

        safety_data = {
            "movement_detected": safety_row['Movement Activity'],
            "fall_detected": safety_row['Fall Detected (Yes/No)'] == "Yes",
            "inactivity_minutes": int(safety_row['Post-Fall Inactivity Duration (Seconds)']) // 60,
            "location": safety_row['Location']
        }
    except Exception as e:
        print(f"⚠️ Could not load safety data: {e}")
        safety_data = simulate_inputs.generate_fake_safety_data()

    current_time = simulate_inputs.generate_current_time()

    today = datetime.date.today()
    today_reminders = reminder_df[
        pd.to_datetime(reminder_df['Timestamp'], errors='coerce').dt.date == today
    ]
    reminders = today_reminders.apply(
        lambda row: f"{row['Reminder Type']} at {row['Scheduled Time']}", axis=1
    ).tolist()

    trends = generate_health_trends()

    if request.method == 'POST':
        user_input = request.form['user_input']
        do_voice = 'voice' in request.form
        do_translate = 'translate' in request.form

        response = coordinator.run(
            heart_rate=health_data["heart_rate"],
            glucose=health_data["glucose"],
            spo2=health_data["spo2"],
            movement=safety_data["movement_detected"],
            fall_detected=safety_data["fall_detected"],
            inactivity=safety_data["inactivity_minutes"],
            location=safety_data["location"],
            current_time=current_time,
            user_input=user_input
        )

        if do_translate:
            translated_response = translate_and_speak(response, source_lang="en", target_lang="hi")
        elif do_voice:
            try:
                voice_output.speak(response)
            except Exception as e:
                print(f"❌ Error in speak(): {e}")

        chat_history.append({
            "user": user_input,
            "bot": response
        })
    else:
        chat_history = []

    return render_template(
        'dashboard.html',
        response=response,
        translated_response=translated_response,
        health_data=health_data,
        safety_data=safety_data,
        reminders=reminders,
        chat_history=chat_history,
        health_trends=trends,
        device_id=device_id
    )

@dashboard_bp.route('/reminders', methods=['GET'])
def reminders_page():
    today = datetime.date.today()
    now = datetime.datetime.now().time()
    current_datetime = datetime.datetime.combine(today, now)
    end_datetime = current_datetime + datetime.timedelta(hours=8)

    grouped_reminders = defaultdict(lambda: defaultdict(list))

    for _, row in reminder_df.iterrows():
        timestamp_str = row.get('Timestamp', '').strip()
        try:
            timestamp = datetime.datetime.strptime(timestamp_str, '%m/%d/%Y %H:%M')

            if today == timestamp.date() and current_datetime <= timestamp <= end_datetime:
                reminder_type = row.get("Reminder Type", "Unknown")
                date_str = timestamp.strftime('%Y-%m-%d')
                time_str = timestamp.strftime('%I:%M %p')
                grouped_reminders[reminder_type][date_str].append(time_str)
        except Exception as e:
            print(f"Skipping invalid timestamp '{timestamp_str}': {e}")

    for type_group in grouped_reminders.values():
        for time_list in type_group.values():
            time_list.sort(key=lambda t: datetime.datetime.strptime(t, '%I:%M %p'))

    return render_template('reminders.html', grouped_reminders=grouped_reminders)

@dashboard_bp.route('/trends', methods=['GET'])
def trends_page():
    trends = generate_health_trends()
    return render_template('trends.html', health_trends=trends)

@dashboard_bp.route('/send-help', methods=['POST'])
def send_help():
    print("🚨 Emergency alert triggered!")
    return jsonify({"status": "success"}), 200

@dashboard_bp.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    user_message = data.get('message', '').lower()
    device_id = 'D11002'

    response = ""

    if 'health' in user_message:
        try:
            with open('data/health_monitoring.csv', 'r') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    if row['Device-ID/User-ID'] == device_id:
                        response = (
                            f"Health Report for {device_id}:\n"
                            f"- Heart Rate: {row['Heart Rate']} (Threshold Exceeded: {row['Heart Rate Below/Above Threshold (Yes/No)']})\n"
                            f"- Blood Pressure: {row['Blood Pressure']} (Threshold Exceeded: {row['Blood Pressure Below/Above Threshold (Yes/No)']})\n"
                            f"- Glucose Level: {row['Glucose Levels']} (Threshold Exceeded: {row['Glucose Levels Below/Above Threshold (Yes/No)']})\n"
                            f"- Oxygen Saturation: {row['Oxygen Saturation (SpO₂%)']}% (Below Threshold: {row['SpO₂ Below Threshold (Yes/No)']})\n"
                            f"- Caregiver Notified: {row['Caregiver Notified (Yes/No)']}"
                        )
                        break
                else:
                    response = f"No health records found for device {device_id}."
        except Exception as e:
            response = "Error reading health data."

    elif 'safety' in user_message or 'alert' in user_message:
        try:
            with open('data/safety_monitoring.csv', 'r') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    if row['Device-ID/User-ID'] == device_id:
                        response = (
                            f"Safety Report for {device_id}:\n"
                            f"- Movement: {row['Movement Activity']}, Location: {row['Location']}\n"
                            f"- Fall Detected: {row['Fall Detected (Yes/No)']}, Impact: {row['Impact Force Level']}\n"
                            f"- Inactivity Duration: {row['Post-Fall Inactivity Duration (Seconds)']} seconds\n"
                            f"- Alert Triggered: {row['Alert Triggered (Yes/No)']}, Caregiver Notified: {row['Caregiver Notified (Yes/No)']}"
                        )
                        break
                else:
                    response = f"No safety alerts found for device {device_id}."
        except Exception as e:
            response = "Error reading safety data."
    else:
        response = "I'm sorry, I can only help with health or safety status."

    return jsonify({'message': response})
