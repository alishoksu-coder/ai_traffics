import sys
import os
import sqlite3
import pandas as pd
import numpy as np
from sklearn.metrics import mean_absolute_error, mean_squared_error
from sklearn.linear_model import LinearRegression
import time
import torch

# Добавляем путь к backend
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.lstm_engine import ai_lstm_brain
from app.config import settings

def main():
    print("Starting evaluation of traffic prediction models...")
    db_path = settings.db_path
    if not os.path.exists(db_path):
        print(f"Database not found: {db_path}")
        return

    conn = sqlite3.connect(db_path)
    # Берем последние 10,000 записей для теста
    query = "SELECT value FROM traffic_values ORDER BY ts DESC LIMIT 10000"
    df = pd.read_sql_query(query, conn)
    
    if len(df) < 500:
        print("Not enough data for evaluation (need at least 500 records).")
        conn.close()
        return

    data = df['value'].values.tolist()[::-1]
    split = int(len(data) * 0.8)
    train_data = data[:split]
    test_data = data[split:]
    
    horizons = [30, 60] # минуты
    
    for h in horizons:
        print(f"\n--- Prediction Horizon: {h} min ---")
        
        y_true = []
        y_naive = []
        y_ma = []
        y_lr = []
        y_lstm = []
        
        lookback = 12
        
        # Для простоты теста будем идти по шагам
        for i in range(lookback, len(test_data) - h):
            target = test_data[i + h]
            current = test_data[i]
            window = test_data[i-lookback:i]
            
            # 1. Naive (Просто текущее значение)
            y_naive.append(current)
            
            # 2. Moving Average (k=5)
            y_ma.append(np.mean(window[-5:]))
            
            # 3. Linear Regression (на окне lookback)
            X_lr = np.arange(lookback).reshape(-1, 1)
            model_lr = LinearRegression().fit(X_lr, window)
            y_lr.append(model_lr.predict([[lookback + h]])[0])
            
            # 4. LSTM
            if ai_lstm_brain.is_trained:
                pred_lstm = ai_lstm_brain.predict_future(window, steps_ahead=h)[-1]
                y_lstm.append(pred_lstm)
            
            y_true.append(target)
            
        # Считаем метрики
        def calc(true, pred, name):
            mae = mean_absolute_error(true, pred)
            rmse = np.sqrt(mean_squared_error(true, pred))
            print(f"  [{name}] MAE: {mae:.2f}, RMSE: {rmse:.2f}")
            return mae, rmse

        metrics_to_save = []
        now = int(time.time())
        
        m_mae, m_rmse = calc(y_true, y_naive, "Naive")
        metrics_to_save.append(("Naive", h, m_mae, m_rmse, len(y_true), now))
        
        m_mae, m_rmse = calc(y_true, y_ma, "Moving Avg")
        metrics_to_save.append(("Moving Avg", h, m_mae, m_rmse, len(y_true), now))
        
        m_mae, m_rmse = calc(y_true, y_lr, "Trend LR")
        metrics_to_save.append(("Trend LR", h, m_mae, m_rmse, len(y_true), now))
        
        if y_lstm:
            m_mae, m_rmse = calc(y_true, y_lstm, "LSTM")
            metrics_to_save.append(("LSTM", h, m_mae, m_rmse, len(y_true), now))

        # Сохраняем в БД
        cur = conn.cursor()
        cur.executemany("""
            INSERT INTO model_metrics (model_name, horizon, mae, rmse, n, ts)
            VALUES (?, ?, ?, ?, ?, ?)
        """, metrics_to_save)
        conn.commit()
        print(f"Metrics for horizon {h} saved to DB.")

    conn.close()
    print("\nEvaluation finished successfully!")

if __name__ == "__main__":
    main()
