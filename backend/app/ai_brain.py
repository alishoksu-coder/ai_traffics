# backend/app/ai_brain.py
import pandas as pd
import joblib
import os
import httpx
from sklearn.ensemble import RandomForestRegressor
from datetime import datetime
 
from app.config import settings
 
# --- КОНФИГУРАЦИЯ SUPABASE (из настроек) ---
SUPABASE_URL = settings.supabase_url
SUPABASE_KEY = settings.supabase_key
 
# Локальный датасет (заготовка для обучения), лежит в корне backend
BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATASET_PATH = os.path.join(BACKEND_DIR, "astana_traffic_history_20k.csv")
DEFAULT_MODEL_PATH = os.path.join(BACKEND_DIR, "data", "traffic_model.joblib")
 
 
class TrafficAI:
    def __init__(self, model_path=DEFAULT_MODEL_PATH):
        self.model_path = model_path
        self.model = None
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
        """Общая логика обучения по DataFrame с колонками segment_id, value, created_at."""
        df = df.copy()
        df['dt'] = pd.to_datetime(df['created_at'])
        df['hour'] = df['dt'].dt.hour
        df['day_of_week'] = df['dt'].dt.dayofweek
        # Фактор погоды в исторических данных не хранится -> нейтральное значение
        df['weather_factor'] = 1.0
 
        X = df[['segment_id', 'hour', 'day_of_week', 'weather_factor']]
        y = df['value']
 
        self.model = RandomForestRegressor(n_estimators=50, random_state=42)
        self.model.fit(X, y)
        self.save_model()
        print(f"🧠 ИИ-Мозг: Модель успешно обучена на {len(X)} записях ({source})!")
 
    def train_on_history(self):
        """Обучается на локальном датасете; при его отсутствии — на Supabase."""
        print("🧠 ИИ-Мозг: Начало обучения...")
 
        # 1. Приоритет — локальный датасет (не зависит от внешнего облака)
        if os.path.exists(DATASET_PATH):
            try:
                df = pd.read_csv(DATASET_PATH)
                required = {'segment_id', 'value', 'created_at'}
                if not required.issubset(df.columns):
                    print(f"ИИ-Мозг: в датасете нет нужных колонок {required}, пропускаю CSV.")
                elif len(df) < 10:
                    print("ИИ-Мозг: в датасете слишком мало строк для обучения.")
                else:
                    self._fit(df, f"локальный датасет {os.path.basename(DATASET_PATH)}")
                    return
            except Exception as e:
                print(f"ИИ-Мозг: ошибка чтения локального датасета: {e}")
 
        # 2. Фолбэк — облако Supabase (если оно доступно)
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
 
            self._fit(pd.DataFrame(data), "Supabase")
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
        except Exception:
            return 30.0
 
ai_brain = TrafficAI()
 
