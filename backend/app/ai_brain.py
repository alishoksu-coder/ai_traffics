# backend/app/ai_brain.py
import pandas as pd
import joblib
import os
import httpx
from sklearn.ensemble import RandomForestRegressor
from datetime import datetime

# --- КОНФИГУРАЦИЯ SUPABASE ---
SUPABASE_URL = "https://nxmefixitnmfzgaxlzsl.supabase.co"
SUPABASE_KEY = "sb_publishable_bJaa7PQeXNJwlewmCu6ZeA_fBtQnn4U"

class TrafficAI:
    def __init__(self, model_path="data/traffic_model.joblib"):
        self.model_path = model_path
        self.model = None
        self.load_model()

    def load_model(self):
        if os.path.exists(self.model_path):
            try:
                self.model = joblib.load(self.model_path)
            except:
                self.model = None

    def save_model(self):
        os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
        joblib.dump(self.model, self.model_path)

    def train_on_history(self):
        """Обучается на истории из облака Supabase (traffic_history)"""
        print("🧠 ИИ-Мозг: Начало обучения на облачных данных...")
        
        # 1. Тянем данные из Supabase REST API
        url = f"{SUPABASE_URL}/rest/v1/traffic_history?select=*"
        headers = {
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {SUPABASE_KEY}",
        }
        
        try:
            with httpx.Client() as client:
                r = client.get(url, headers=headers)
                if r.status_code != 200:
                    print(f"Ошибка загрузки данных из облака: {r.text}")
                    return
                data = r.json()
                
            if len(data) < 10:
                print("ИИ-Мозг: Недостаточно данных в облаке для обучения (нужно хотя бы 10 записей).")
                return

            df = pd.DataFrame(data)
            # Извлекаем дату из created_at
            df['dt'] = pd.to_datetime(df['created_at'])
            df['hour'] = df['dt'].dt.hour
            df['day_of_week'] = df['dt'].dt.dayofweek
            
            # Временно добавим фактор погоды 1.0 если его нет в этой таблице
            df['weather_factor'] = 1.0
            
            X = df[['segment_id', 'hour', 'day_of_week', 'weather_factor']]
            y = df['value']

            self.model = RandomForestRegressor(n_estimators=50, random_state=42)
            self.model.fit(X, y)
            self.save_model()
            print(f"🧠 ИИ-Мозг: Модель успешно обучена на {len(X)} записях из Supabase!")
            
        except Exception as e:
            print(f"Ошибка во время обучения: {e}")

    def predict(self, segment_id, hour, day_of_week, weather_factor=1.0):
        if self.model is None:
            # Базовая модель на случай, если ИИ еще не обучен
            base = 30.0
            if (8 <= hour <= 10) or (17 <= hour <= 19): base = 70.0
            return base * weather_factor

        try:
            X_pred = pd.DataFrame([[segment_id, hour, day_of_week, weather_factor]], 
                                 columns=['segment_id', 'hour', 'day_of_week', 'weather_factor'])
            return float(self.model.predict(X_pred)[0])
        except:
            return 30.0

ai_brain = TrafficAI()
