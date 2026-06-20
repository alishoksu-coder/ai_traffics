# backend/app/ml/baselines.py
"""
Baseline модели для сравнения с LSTM и Random Forest.
Используются для валидации эффективности сложных архитектур.
"""
import numpy as np
import pandas as pd
from typing import List
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from app.ml.preprocessing import enrich_features

class NaiveForecast:
    """
    Наивный прогноз: следующее значение равно текущему.
    """
    def __init__(self):
        self.last_value = 30.0

    def fit(self, df: pd.DataFrame):
        if not df.empty and 'value' in df.columns:
            self.last_value = df['value'].iloc[-1]

    def predict_future(self, recent_data: pd.DataFrame, steps_ahead: int = 1) -> List[float]:
        last = recent_data['value'].iloc[-1] if not recent_data.empty else self.last_value
        return [last] * steps_ahead


class MovingAverageForecast:
    """
    Скользящее среднее за последние window_size шагов.
    """
    def __init__(self, window_size: int = 4): # 4 шага = 1 час
        self.window_size = window_size
        self.last_mean = 30.0

    def fit(self, df: pd.DataFrame):
        if not df.empty and len(df) >= self.window_size:
            self.last_mean = df['value'].tail(self.window_size).mean()

    def predict_future(self, recent_data: pd.DataFrame, steps_ahead: int = 1) -> List[float]:
        if recent_data.empty:
            return [self.last_mean] * steps_ahead
        
        vals = recent_data['value'].tolist()
        preds = []
        for _ in range(steps_ahead):
            # Берем среднее последних window_size (используя свои же прогнозы если нужно)
            window = vals[-self.window_size:]
            nxt = sum(window) / len(window) if window else 30.0
            preds.append(nxt)
            vals.append(nxt)
        
        return preds


class LinearRegressionForecast:
    """
    Простая линейная регрессия на сгенерированных признаках времени.
    """
    def __init__(self):
        self.model = LinearRegression()
        self.features = ['hour_sin', 'hour_cos', 'is_peak_hour', 'weather_factor']
        self.is_trained = False

    def fit(self, df: pd.DataFrame):
        df_enr = enrich_features(df)
        
        # Для LR мы хотим предсказывать Y(t+1) на основе признаков t
        # Но проще предсказывать value просто как функцию от часа пик и времени
        X = df_enr[self.features]
        y = df_enr['value']
        
        if len(X) > 0:
            self.model.fit(X, y)
            self.is_trained = True

    def predict_future(self, recent_data: pd.DataFrame, steps_ahead: int = 1) -> List[float]:
        if not self.is_trained:
            return [30.0] * steps_ahead
            
        df_enr = enrich_features(recent_data)
        last_dt = df_enr['dt'].iloc[-1] if not df_enr.empty else pd.to_datetime('now')
        weather_factor = df_enr['weather_factor'].iloc[-1] if not df_enr.empty else 1.0
        
        preds = []
        for i in range(steps_ahead):
            next_dt = last_dt + pd.Timedelta(minutes=15 * (i + 1))
            next_hour = next_dt.hour
            
            hour_sin = np.sin(2 * np.pi * next_hour / 24.0)
            hour_cos = np.cos(2 * np.pi * next_hour / 24.0)
            is_peak = 1 if (7 <= next_hour <= 9) or (17 <= next_hour <= 20) else 0
            
            x_pred = pd.DataFrame([[hour_sin, hour_cos, is_peak, weather_factor]], columns=self.features)
            val = float(self.model.predict(x_pred)[0])
            val = max(0.0, min(100.0, val))
            preds.append(val)
            
        return preds

class RandomForestForecast:
    """
    Случайный лес на извлеченных признаках.
    """
    def __init__(self):
        self.model = RandomForestRegressor(n_estimators=100, max_depth=10, random_state=42)
        self.features = ['hour_sin', 'hour_cos', 'is_peak_hour', 'is_weekend', 'weather_factor']
        self.is_trained = False

    def fit(self, df: pd.DataFrame):
        df_enr = enrich_features(df)
        X = df_enr[self.features]
        y = df_enr['value']
        if len(X) > 0:
            self.model.fit(X, y)
            self.is_trained = True

    def predict_future(self, recent_data: pd.DataFrame, steps_ahead: int = 1) -> List[float]:
        if not self.is_trained:
            return [30.0] * steps_ahead
            
        df_enr = enrich_features(recent_data)
        last_dt = df_enr['dt'].iloc[-1] if not df_enr.empty else pd.to_datetime('now')
        weather_factor = df_enr['weather_factor'].iloc[-1] if not df_enr.empty else 1.0
        
        preds = []
        for i in range(steps_ahead):
            next_dt = last_dt + pd.Timedelta(minutes=15 * (i + 1))
            next_hour = next_dt.hour
            day_of_week = next_dt.dayofweek
            
            hour_sin = np.sin(2 * np.pi * next_hour / 24.0)
            hour_cos = np.cos(2 * np.pi * next_hour / 24.0)
            is_peak = 1 if (7 <= next_hour <= 9) or (17 <= next_hour <= 20) else 0
            is_weekend = 1 if day_of_week >= 5 else 0
            
            x_pred = pd.DataFrame([[hour_sin, hour_cos, is_peak, is_weekend, weather_factor]], columns=self.features)
            val = float(self.model.predict(x_pred)[0])
            val = max(0.0, min(100.0, val))
            preds.append(val)
            
        return preds

