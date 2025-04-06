import pandas as pd

class SafetyMonitorAgent:
    def __init__(self, model):
        self.model = model

    def check_safety(self, movement, fall_detected, inactivity, location):
        # Preprocess Movement Activity
        movement_mapping = {
            "No Movement": 0,
            "Lying": 1,
            "Sitting": 2,
            "Standing": 3,
            "Walking": 4,
            "Running": 5
        }
        movement_numeric = movement_mapping.get(movement, 0)  # default to 0 if unknown

        # Preprocess Fall Detected
        if fall_detected:
            fall_numeric = 1 
        else:
            fall_numeric = 0

        # Preprocess Inactivity
        try:
            inactivity_seconds = float(inactivity)
        except ValueError:
            inactivity_seconds = 0.0

        # Optional: Encode location if your model uses it
        location_mapping = {
            "Kitchen": 0,
            "Living Room": 1,
            "Bedroom": 2,
            "Bathroom": 3,
            "Hallway": 4
        }
        location_numeric = location_mapping.get(location, -1)  # or one-hot encode if needed

        # Create DataFrame with preprocessed values
        data = pd.DataFrame([[movement_numeric, fall_numeric, inactivity_seconds, location_numeric]],
                            columns=["Movement Activity", "Fall Detected (Yes/No)",
                                     "Post-Fall Inactivity Duration (Seconds)", "Location"])

        prediction = self.model.predict(data)
        return "🚨 Safety Alert!" if prediction[0] == 1 else "✅ Safe"
