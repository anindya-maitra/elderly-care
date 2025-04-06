from datetime import datetime, timedelta

class ReminderAgent:
    def __init__(self, reminder_df):
        self.df = reminder_df

    def check_reminders(self, current_time):
        try:
            now = datetime.strptime(current_time, "%H:%M:%S")
            time_window = timedelta(minutes=5)

            reminders = []
            for _, row in self.df.iterrows():
                sched_time = datetime.strptime(row["Scheduled Time"], "%H:%M:%S")
                if abs((now - sched_time).total_seconds()) <= time_window.total_seconds():
                    reminders.append(row["Reminder Type"])
            return reminders
        except Exception as e:
            print("Reminder check failed:", e)
            return []
