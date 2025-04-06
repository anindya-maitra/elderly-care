import pandas as pd

class HealthMonitorAgent:
    def __init__(self, model):
        self.model = model

    def check_health(self, heart_rate, glucose, spo2):
        data = pd.DataFrame([[heart_rate, glucose, spo2]],
                            columns=['Heart Rate', 'Glucose Levels', 'Oxygen Saturation (SpO₂%)'])
        prediction = self.model.predict(data)
        return "🚨 Health Alert!" if prediction[0] == 1 else "✅ Health OK"
