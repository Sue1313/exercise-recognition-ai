from src.constants import IMPORTANT_ANGLES, ACTIONS, ANGLE_LIMITS
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
import pandas as pd
import numpy as np
import joblib
import os

class Exercise:
    def __init__(self, freq_update = 4,
                 freq_predict = 3,
                 model_path: str = 'exercise_model.pkl',
                 scaler_path: str = 'scaler.pkl',
                 save_model = False):
        
        self.clf = None
        self.index = 0
        self.freq_update = freq_update
        self.freq_predict = freq_predict
        self.scaler = None
        self.model_path = model_path
        self.scaler_path = scaler_path
        self.current_exercise = ACTIONS[0]
        self.cumulative_predictions = np.zeros(len(ACTIONS))
        self.incorrect_joints = []
        self.load_model(save_model=save_model)

    def load_model(self, save_model: bool = False):
        if os.path.exists(self.model_path) and os.path.exists(self.scaler_path):
            self.clf = joblib.load(self.model_path)
            self.scaler = joblib.load(self.scaler_path)
            print("Model and scaler loaded.")
        else:
            print("Model and scaler not found. Training new model...")
            self.train_model(save_model=save_model)

    def train_model(self, csv_file: str = './data/angled_data.csv', save_model = False) -> None:
        data = pd.read_csv(csv_file)
        data = data.sample(frac=1).reset_index(drop=True)  # Randomize data
        train_data, test_data = train_test_split(data, test_size=0.2, random_state=42)
        X_train = train_data.drop('label', axis=1)
        y_train = train_data['label']
        X_test = test_data.drop('label', axis=1)
        y_test = test_data['label']
        
        scaler = StandardScaler()
        X_train = scaler.fit_transform(X_train)
        X_test = scaler.transform(X_test)
        
        clf = RandomForestClassifier(n_estimators=100, random_state=42)
        clf.fit(X_train, y_train)
        
        y_pred = clf.predict(X_test)
        print("Accuracy:", accuracy_score(y_test, y_pred))
        
        self.clf, self.scaler = clf, scaler

        if save_model:
            joblib.dump(clf, 'exercise_model.pkl')
            joblib.dump(scaler, 'scaler.pkl')
            print("Model and scaler saved.")

    def identify_exercise(self, angle_dict) -> int:
        # Create a DataFrame from the angle_dict with the correct column names
        angles_list = {joint: [angle_dict.get(joint, 0)] for joint in IMPORTANT_ANGLES.keys()}
        angles_df = pd.DataFrame(angles_list)

        # Transform the angles using the scaler
        angles_scaled = self.scaler.transform(angles_df)

        # Predict the probability
        return self.clf.predict_proba(angles_scaled)[0]
    
    def predict_on_sample(self):
        if (np.max(self.cumulative_predictions) < 0.5):
             return 
    
        most_likely = np.argmax(self.cumulative_predictions)
        self.current_exercise = ACTIONS[most_likely]
    

    def update_prediction(self, angle_dict: dict) -> str:
        self.index += 1
        if(self.index % self.freq_predict == 0):
            self.cumulative_predictions += self.identify_exercise(angle_dict)
        
        if(self.index % self.freq_update * self.freq_predict == 0):
            self.predict_on_sample()
            self.correct_exercise(angle_dict)
            self.cumulative_predictions = np.zeros(len(ACTIONS))

        return self.current_exercise

    def correct_exercise(self, angle_dict) -> list[str]:
        self.incorrect_joints = []
        for joint, angle in angle_dict.items():
            if joint in ANGLE_LIMITS[self.current_exercise]:
                min_angle, max_angle = ANGLE_LIMITS[self.current_exercise][joint]
                if not (min_angle <= angle <= max_angle):
                     self.incorrect_joints.append(joint)