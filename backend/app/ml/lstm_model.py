# backend/app/ml/lstm_model.py
"""
Модуль LSTM нейронной сети для прогнозирования трафика.

Архитектура:
- 2-слойный LSTM (Long Short-Term Memory) с dropout=0.2
- BatchNorm1d для стабилизации обучения
- Fully Connected слой для финальной регрессии

Модель загружается один раз при инициализации класса TrafficLSTM (Singleton-паттерн).
Веса хранятся в файле .pth и не перезагружаются при каждом запросе API.
"""
import os

import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from typing import List

from app.ml.preprocessing import enrich_features


# ---------- Архитектура LSTM ----------

class LSTMModel(nn.Module):
    """
    PyTorch LSTM для прогнозирования загруженности дорог.

    Параметры:
        input_size: количество входных фичей (value, hour_sin, hour_cos, is_peak_hour, weather_factor).
        hidden_size: размер скрытого состояния LSTM.
        num_layers: количество стекированных LSTM-слоёв.
        output_size: размерность выхода (1 = регрессия).
    """

    def __init__(self, input_size=5, hidden_size=64, num_layers=2, output_size=1):
        super(LSTMModel, self).__init__()
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        self.lstm = nn.LSTM(input_size, hidden_size, num_layers, batch_first=True, dropout=0.2)
        self.bn = nn.BatchNorm1d(hidden_size)
        self.fc = nn.Linear(hidden_size, output_size)

    def forward(self, x):
        h0 = torch.zeros(self.num_layers, x.size(0), self.hidden_size).to(x.device)
        c0 = torch.zeros(self.num_layers, x.size(0), self.hidden_size).to(x.device)

        out, _ = self.lstm(x, (h0, c0))
        out = out[:, -1, :]  # Берём последний шаг последовательности
        out = self.bn(out)
        out = self.fc(out)
        return out


# ---------- Обёртка для обучения и инференса ----------

# Пути к датасетам
BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DATASET_PATH_YESIL = os.path.join(BACKEND_DIR, "yesil_traffic_history_dataset.csv")
DATASET_PATH_ASTANA = os.path.join(BACKEND_DIR, "astana_traffic_history_20k.csv")


class TrafficLSTM:
    """
    Singleton-обёртка вокруг PyTorch LSTM-модели.

    - Загружает веса один раз при создании экземпляра.
    - Предоставляет методы train_on_dataset() и predict_future().
    - Нормализация: value (0-100) → (0-1) на входе, обратно на выходе.
    """

    def __init__(self, model_path="data/lstm_traffic.pth"):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", model_path))
        self.features = ['value', 'hour_sin', 'hour_cos', 'is_peak_hour', 'weather_factor']
        self.model = LSTMModel(input_size=len(self.features)).to(self.device)
        self.is_trained = False
        self.lookback = 24  # 6 часов при 15-мин интервалах
        self._load_model()

    def _load_model(self):
        """Загрузка сохранённых весов модели (вызывается один раз при старте)."""
        if os.path.exists(self.model_path):
            try:
                self.model.load_state_dict(
                    torch.load(self.model_path, map_location=self.device, weights_only=True)
                )
                self.model.eval()
                self.is_trained = True
                print(f"LSTM: Model loaded from {self.model_path}")
            except Exception as e:
                print(f"LSTM Load error: {e}")

    def save_model(self):
        """Сохранение весов модели на диск."""
        os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
        torch.save(self.model.state_dict(), self.model_path)

    def train_on_dataset(self, df: pd.DataFrame = None, epochs=20, lr=0.001, batch_size=64) -> bool:
        """
        Обучение LSTM на переданном датасете (или загрузка по умолчанию).
        Включает early stopping с patience=3.
        Возвращает True в случае успеха. История лоссов сохраняется в self.loss_history.
        """
        if df is None:
            if os.path.exists(DATASET_PATH_YESIL):
                df = pd.read_csv(DATASET_PATH_YESIL)
                print("LSTM: Training on Yesil dataset")
            elif os.path.exists(DATASET_PATH_ASTANA):
                df = pd.read_csv(DATASET_PATH_ASTANA)
                print("LSTM: Training on Astana dataset")

        if df is None or len(df) <= self.lookback:
            print("LSTM: Not enough data for training.")
            return False

        self.loss_history = []

        df = enrich_features(df)

        # Для простоты берём один перекрёсток из Yesil
        if 'segment_id' in df.columns:
            df = df[df['segment_id'] == df['segment_id'].iloc[0]].sort_values('dt')

        # Нормализация value (0-100 -> 0-1)
        df['value_norm'] = df['value'] / 100.0
        features_to_use = self.features.copy()
        features_to_use[0] = 'value_norm'

        data = df[features_to_use].values
        Y_data = df['value_norm'].values

        X, Y = [], []
        for i in range(len(data) - self.lookback):
            X.append(data[i:(i + self.lookback)])
            Y.append(Y_data[i + self.lookback])

        X = np.array(X)
        Y = np.array(Y)

        if len(X) == 0:
            return False

        X_tensor = torch.FloatTensor(X)
        Y_tensor = torch.FloatTensor(Y).unsqueeze(-1)

        dataset = torch.utils.data.TensorDataset(X_tensor, Y_tensor)
        loader = torch.utils.data.DataLoader(dataset, batch_size=batch_size, shuffle=True)

        optimizer = torch.optim.Adam(self.model.parameters(), lr=lr)
        criterion = nn.MSELoss()

        self.model.train()

        best_loss = float('inf')
        patience = 3
        patience_counter = 0

        for epoch in range(epochs):
            total_loss = 0
            for batch_X, batch_Y in loader:
                batch_X, batch_Y = batch_X.to(self.device), batch_Y.to(self.device)
                optimizer.zero_grad()
                outputs = self.model(batch_X)
                loss = criterion(outputs, batch_Y)
                loss.backward()
                optimizer.step()
                total_loss += loss.item()

            avg_loss = total_loss / len(loader)
            self.loss_history.append(avg_loss)
            
            if (epoch + 1) % 5 == 0 or epoch == 0:
                print(f"LSTM Epoch [{epoch + 1}/{epochs}], Avg Loss: {avg_loss:.4f}")

            # Early stopping
            if avg_loss < best_loss:
                best_loss = avg_loss
                patience_counter = 0
            else:
                patience_counter += 1
                if patience_counter >= patience:
                    print(f"LSTM Early stopping at epoch {epoch + 1}")
                    break

        self.is_trained = True
        self.model.eval()
        self.save_model()
        return True

    def predict_future(self, recent_data: pd.DataFrame, steps_ahead: int = 1) -> List[float]:
        """
        Авторегрессивный прогноз на steps_ahead шагов (каждый шаг = 15 мин).

        Аргументы:
            recent_data: DataFrame с колонками ['value', 'dt', ...].
            steps_ahead: количество шагов прогноза вперёд.

        Возвращает:
            Список предсказанных значений загруженности (0-100).
        """
        if not self.is_trained or len(recent_data) == 0:
            last = recent_data['value'].iloc[-1] if len(recent_data) > 0 else 30.0
            return [last] * steps_ahead

        self.model.eval()
        predictions = []

        df = enrich_features(recent_data)
        df['value_norm'] = df['value'] / 100.0
        features_to_use = self.features.copy()
        features_to_use[0] = 'value_norm'

        current_seq = df[features_to_use].values[-self.lookback:].tolist()

        # Если история короче окна, дублируем первое значение
        if len(current_seq) < self.lookback:
            pad_len = self.lookback - len(current_seq)
            current_seq = [current_seq[0]] * pad_len + current_seq

        last_dt = df['dt'].iloc[-1]

        with torch.no_grad():
            for i in range(steps_ahead):
                x_input = torch.FloatTensor(current_seq).view(
                    1, self.lookback, len(self.features)
                ).to(self.device)
                pred = self.model(x_input)
                val_norm = pred.item()
                val = max(0.0, min(100.0, val_norm * 100.0))
                predictions.append(val)

                # Авторегрессия: генерируем фичи для следующего шага
                next_dt = last_dt + pd.Timedelta(minutes=15 * (i + 1))
                next_hour = next_dt.hour

                hour_sin = np.sin(2 * np.pi * next_hour / 24.0)
                hour_cos = np.cos(2 * np.pi * next_hour / 24.0)
                is_peak = 1 if (7 <= next_hour <= 9) or (17 <= next_hour <= 20) else 0
                weather_factor = current_seq[-1][4]

                next_step = [val_norm, hour_sin, hour_cos, is_peak, weather_factor]
                current_seq = current_seq[1:] + [next_step]

        return predictions
