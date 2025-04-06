class CentralCoordinator:
    def __init__(self, health_agent, safety_agent, reminder_agent, chat_agent):
        self.health_agent = health_agent
        self.safety_agent = safety_agent
        self.reminder_agent = reminder_agent
        self.chat_agent = chat_agent

    def run(self, heart_rate, glucose, spo2, movement, fall_detected, inactivity, location, current_time, user_input):
        health_status = self.health_agent.check_health(heart_rate, glucose, spo2)
        safety_status = self.safety_agent.check_safety(movement, fall_detected, inactivity, location)
        reminders = self.reminder_agent.check_reminders(current_time)

        context = f"""
        Current Health Status: {health_status}
        Current Safety Status: {safety_status}
        Reminders at {current_time}: {', '.join(reminders) if reminders else 'No reminders'}

        Question: {user_input}
        Respond in a caring and concise manner suitable for caregivers or elderly individuals.
        """
        return self.chat_agent.ask(context)
    
    def generate_daily_summary(self):
        with open("conversation_log.txt", "r", encoding="utf-8") as log:
            lines = log.readlines()[-20:]  # Recent interactions
        return "📅 Daily Summary:\n" + "".join(lines)

