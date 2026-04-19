import sys
import os
import sqlite3
import pandas as pd

# Добавляем путь к backend, чтобы импортировать app
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.lstm_engine import ai_lstm_brain
from app.config import settings

def main():
    print("Loading data from SQLite for LSTM training...")
    db_path = settings.db_path
    if not os.path.exists(db_path):
        print(f"Database not found at: {db_path}")
        return

    conn = sqlite3.connect(db_path)
    # Берем последние 5,000 записей для быстрого обучения
    query = "SELECT value FROM traffic_values ORDER BY ts DESC LIMIT 5000"
    df = pd.read_sql_query(query, conn)
    conn.close()

    if df.empty:
        print("No data for training. Run simulator first.")
        return

    traffic_data = df['value'].values.tolist()[::-1] # Разворачиваем, чтобы было в хронологическом порядке
    
    print(f"Found {len(traffic_data)} points. Starting PyTorch LSTM training...")
    success = ai_lstm_brain.train_historical(traffic_data, epochs=30)
    
    if success:
        print("LSTM model successfully trained and saved!")
    else:
        print("Training error.")

if __name__ == "__main__":
    main()
