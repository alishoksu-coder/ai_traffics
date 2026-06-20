# backend/app/ai_brain.py
import pandas as pd
import numpy as np
import joblib
import os
import httpx
from sklearn.ensemble import RandomForestRegressor
from datetime import datetime

from app.core.config import settings

# --- КОНФИГУРАЦИЯ SUPABASE (из настроек) ---
SUPABASE_URL = settings.supabase_url
SUPABASE_KEY = settings.supabase_key

BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATASET_PATH_YESIL = os.path.join(BACKEND_DIR, "yesil_traffic_history_dataset.csv")
DATASET_PATH_ASTANA = os.path.join(BACKEND_DIR, "astana_traffic_history_20k.csv")
DEFAULT_MODEL_PATH = os.path.join(BACKEND_DIR, "data", "traffic_model.joblib")


from app.ml.preprocessing import enrich_features

class TrafficAI:
    def __init__(self, model_path=DEFAULT_MODEL_PATH):
        self.model_path = model_path
        self.model = None
        self.features = ['segment_id', 'hour_sin', 'hour_cos', 'day_sin', 'day_cos', 
                         'is_weekend', 'is_peak_hour', 'weather_factor']
        self.load_model()

    def load_model(self):
        if os.path.exists(self.model_path):
            try:
                self.model = joblib.load(self.model_path)
            except Exception:
                self.model = None

    def save_model(self):
        os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
        joblib.dump(self.model, self.model_path)

    def _fit(self, df, source):
        """Обучение Random Forest с расширенным набором фичей."""
        df = enrich_features(df)
        
        # Проверяем, что все фичи есть
        for f in self.features:
            if f not in df.columns:
                df[f] = 0
                
        X = df[self.features]
        y = df['value']

        # Улучшенный Random Forest
        self.model = RandomForestRegressor(
            n_estimators=100, 
            max_depth=15, 
            min_samples_split=5,
            random_state=42,
            n_jobs=-1
        )
        self.model.fit(X, y)
        self.save_model()
        print(f"🧠 ИИ-Мозг (RF): Модель обучена на {len(X)} записях ({source}). Использовано {len(self.features)} фичей.")

    def train_on_history(self):
        """Обучается на Yesil (50K) или Astana (40K) или Supabase."""
        print("🧠 ИИ-Мозг: Начало обучения Random Forest...")

        # 1. Приоритет — датасет Yesil (50K)
        if os.path.exists(DATASET_PATH_YESIL):
            try:
                df = pd.read_csv(DATASET_PATH_YESIL)
                if len(df) > 10:
                    self._fit(df, f"богатый датасет {os.path.basename(DATASET_PATH_YESIL)}")
                    return
            except Exception as e:
                print(f"ИИ-Мозг: ошибка чтения Yesil датасета: {e}")
                
        # 2. Фолбэк — датасет Astana (40K)
        if os.path.exists(DATASET_PATH_ASTANA):
            try:
                df = pd.read_csv(DATASET_PATH_ASTANA)
                if len(df) > 10:
                    self._fit(df, f"локальный датасет {os.path.basename(DATASET_PATH_ASTANA)}")
                    return
            except Exception as e:
                print(f"ИИ-Мозг: ошибка чтения Astana датасета: {e}")

        # 3. Фолбэк — облако Supabase
        url = f"{SUPABASE_URL}/rest/v1/traffic_history?select=*"
        headers = {
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {SUPABASE_KEY}",
        }
        try:
            with httpx.Client() as client:
                r = client.get(url, headers=headers)
                if r.status_code == 200:
                    data = r.json()
                    if len(data) >= 10:
                        self._fit(pd.DataFrame(data), "Supabase")
                        return
        except Exception as e:
            print(f"Ошибка во время обучения из облака: {e}")

    def predict(self, segment_id, hour, day_of_week, weather_factor=1.0):
        if self.model is None:
            base = 30.0
            if (8 <= hour <= 10) or (17 <= hour <= 19): base = 70.0
            return base * weather_factor

        try:
            # Ручное конструирование фичей для предсказания
            hour_sin = np.sin(2 * np.pi * hour / 24.0)
            hour_cos = np.cos(2 * np.pi * hour / 24.0)
            day_sin = np.sin(2 * np.pi * day_of_week / 7.0)
            day_cos = np.cos(2 * np.pi * day_of_week / 7.0)
            is_weekend = 1 if day_of_week >= 5 else 0
            is_peak = 1 if (7 <= hour <= 9) or (17 <= hour <= 20) else 0

            X_pred = pd.DataFrame([[segment_id, hour_sin, hour_cos, day_sin, day_cos, 
                                    is_weekend, is_peak, weather_factor]], 
                                 columns=self.features)
            val = float(self.model.predict(X_pred)[0])
            return max(0.0, min(100.0, val))
        except Exception as e:
            print(f"ИИ-Мозг predict error: {e}")
            return 30.0

ai_brain = TrafficAI()
 
