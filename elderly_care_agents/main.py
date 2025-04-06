import os
import pandas as pd
import joblib
from datetime import datetime
from agents import HealthMonitorAgent, SafetyMonitorAgent, ReminderAgent, ChatAgent
from agents.central_coordinator import CentralCoordinator
from agents import simulate_inputs, voice_output
from translate_text import translate_and_speak


# Load models and data
health_model = joblib.load("models/health_alert_model.pkl")
safety_model = joblib.load("models/safety_alert_model.pkl")
reminder_df = pd.read_csv("data/daily_reminder.csv")

# Initialize agents
health_agent = HealthMonitorAgent(health_model)
safety_agent = SafetyMonitorAgent(safety_model)
reminder_agent = ReminderAgent(reminder_df)
chat_agent = ChatAgent()

# Initialize Coordinator
coordinator = CentralCoordinator(health_agent, safety_agent, reminder_agent, chat_agent)

# Prepare conversation log
log_file = open("conversation_log.txt", "a", encoding="utf-8")

# Prepare status log
os.makedirs("logs", exist_ok=True)
status_log_path = "logs/status_log.csv"

# Input loop
print("\n🧠 Ask the system anything (type 'exit' to quit):")

# Offer translation
do_translate = input("🌍 Would you like the response translated? (yes/no): ").strip().lower()
translate = do_translate == "yes"

while True:
    user_input = input("\n👤 You: ").strip()

    if user_input.lower() == "exit":
        print("👋 Goodbye!")
        break

    if user_input.lower() == "summary":
        summary = coordinator.generate_daily_summary()
        print(summary)
        continue


    # Simulate sensor input
    health_data = simulate_inputs.generate_fake_health_data()
    safety_data = simulate_inputs.generate_fake_safety_data()
    current_time = simulate_inputs.generate_current_time()

    # Run Coordinator
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

    print("\n🤖 Ollama says:\n")
    print(response)
    print("\n---")

    # Log conversation
    log_file.write(f"[{datetime.now()}] 👤 You: {user_input}\n")
    log_file.write(f"[{datetime.now()}] 🤖 Ollama: {response}\n\n")

    # Structured CSV logging
    log_df = pd.DataFrame([{
        "time": current_time,
        "heart_rate": health_data["heart_rate"],
        "glucose": health_data["glucose"],
        "spo2": health_data["spo2"],
        "health_status": coordinator.health_agent.check_health(**health_data),
        "safety_status": coordinator.safety_agent.check_safety(
            movement=safety_data["movement_detected"],
            fall_detected=safety_data["fall_detected"],
            inactivity=safety_data["inactivity_minutes"],
            location=safety_data["location"]
        )
    }])
    log_df.to_csv(status_log_path, mode="a", header=not os.path.exists(status_log_path), index=False)

    # Translate and speak
    if translate:
        source_lang = input("🔤 Enter source language code (e.g., 'en'): ").strip()
        target_lang = input("🌐 Enter target language code (e.g., 'fr'): ").strip()
        translate_and_speak(response, source_lang, target_lang)
    else:
        voice_output.speak(response)

log_file.close()
