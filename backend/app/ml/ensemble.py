# backend/app/ensemble.py
import numpy as np
import pandas as pd
from typing import Dict, List, Optional
from datetime import datetime

from app.ml.rf_model import ai_brain
from app.ml.lstm_model import TrafficLSTM
from app.ml.predictor import predict_weighted_ma

# Создаем инстанс LSTM, так как ранее он импортировался из lstm_engine
ai_lstm_brain = TrafficLSTM()

class TrafficEnsemble:
    def __init__(self):
        # Weights for models: [RF, LSTM, WMA, Seasonal]
        self.weights = {
            'rf': 0.4,
            'lstm': 0.3,
            'wma': 0.15,
            'seasonal': 0.15
        }
        # MAE tracking for adaptive weighting
        self.model_mae = {
            'rf': 10.0,
            'lstm': 10.0,
            'wma': 15.0,
            'seasonal': 15.0
        }
        
    def _update_weights(self):
        """Пересчет весов обратно пропорционально MAE (adaptive weighting)"""
        total_inv_mae = sum(1.0 / mae for mae in self.model_mae.values() if mae > 0)
        if total_inv_mae > 0:
            for model_name, mae in self.model_mae.items():
                if mae > 0:
                    self.weights[model_name] = (1.0 / mae) / total_inv_mae
                    
    def update_mae(self, model_name: str, new_mae: float):
        """Обновление MAE модели (EMA-сглаживание)"""
        if model_name in self.model_mae:
            # Окно сглаживания ~0.8
            self.model_mae[model_name] = 0.8 * self.model_mae[model_name] + 0.2 * new_mae
            self._update_weights()
            
    def predict(self, segment_id: int, hour: int, day_of_week: int, weather_factor: float, recent_history_df: Optional[pd.DataFrame] = None) -> float:
        """Ансамблевый прогноз"""
        predictions = {}
        
        # 1. Random Forest (базовый ИИ)
        try:
            predictions['rf'] = ai_brain.predict(segment_id, hour, day_of_week, weather_factor)
        except Exception as e:
            print(f"RF predict err: {e}")
            
        # 2. LSTM (нейросеть)
        if recent_history_df is not None and not recent_history_df.empty:
            try:
                lstm_preds = ai_lstm_brain.predict_future(recent_history_df, steps_ahead=1)
                predictions['lstm'] = lstm_preds[0]
            except Exception as e:
                print(f"LSTM predict err: {e}")
                
        # 3. Weighted Moving Average (классика)
        if recent_history_df is not None and not recent_history_df.empty:
            try:
                # Берем последние значения
                vals = recent_history_df['value'].values[-6:].tolist()
                predictions['wma'] = predict_weighted_ma(vals)
            except Exception as e:
                print(f"WMA predict err: {e}")
                
        # 4. Seasonal Naive
        if recent_history_df is not None and not recent_history_df.empty:
            try:
                # Ожидаем что recent_history_df имеет колонку hour, если нет - извлечем
                if 'dt' in recent_history_df.columns:
                    recent_history_df['hour_temp'] = recent_history_df['dt'].dt.hour
                elif 'ts' in recent_history_df.columns:
                    recent_history_df['hour_temp'] = pd.to_datetime(recent_history_df['ts'], unit='s').dt.hour
                else:
                    recent_history_df['hour_temp'] = -1
                
                same_hour = recent_history_df[recent_history_df['hour_temp'] == hour]
                if not same_hour.empty:
                    predictions['seasonal'] = same_hour['value'].mean()
            except Exception as e:
                print(f"Seasonal predict err: {e}")
                
        if not predictions:
            return 30.0 * weather_factor
            
        # Взвешенное среднее
        final_pred = 0.0
        active_weight_sum = 0.0
        
        for model_name, val in predictions.items():
            w = self.weights.get(model_name, 0.0)
            final_pred += val * w
            active_weight_sum += w
            
        if active_weight_sum > 0:
            final_pred /= active_weight_sum
        else:
            final_pred = sum(predictions.values()) / len(predictions)
            
        return max(0.0, min(100.0, final_pred))

traffic_ensemble = TrafficEnsemble()
