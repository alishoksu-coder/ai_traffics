"""
Модуль: Цифровой Клон & Нейросетевое Прогнозирование (Real PyTorch LSTM).
Этот файл реализует архитектуру Long Short-Term Memory для глубокого анализа временных рядов.
"""

import torch
import torch.nn as nn
import numpy as np
import os
from typing import List, Tuple

# Класс архитектуры LSTM
class LSTMModel(nn.Module):
    def __init__(self, input_size=1, hidden_size=64, num_layers=2, output_size=1):
        super(LSTMModel, self).__init__()
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        self.lstm = nn.LSTM(input_size, hidden_size, num_layers, batch_first=True, dropout=0.2)
        self.fc = nn.Linear(hidden_size, output_size)

    def forward(self, x):
        # x shape: (batch, seq_len, input_size)
        h0 = torch.zeros(self.num_layers, x.size(0), self.hidden_size).to(x.device)
        c0 = torch.zeros(self.num_layers, x.size(0), self.hidden_size).to(x.device)
        
        out, _ = self.lstm(x, (h0, c0))
        # Берем последний выход последовательности
        out = self.fc(out[:, -1, :])
        return out

class TrafficLSTM:
    def __init__(self, model_path="data/lstm_traffic.pth"):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", model_path))
        self.model = LSTMModel().to(self.device)
        self.is_trained = False
        self.lookback = 12
        self.load_model()

    def load_model(self):
        if os.path.exists(self.model_path):
            try:
                self.model.load_state_dict(torch.load(self.model_path, map_location=self.device))
                self.model.eval()
                self.is_trained = True
                print(f"LSTM: Model loaded from {self.model_path}")
            except Exception as e:
                print(f"LSTM Load error: {e}")

    def save_model(self):
        os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
        torch.save(self.model.state_dict(), self.model_path)

    def _prepare_sequences(self, data: List[float], seq_len: int):
        X, Y = [], []
        for i in range(len(data) - seq_len):
            X.append(data[i:(i + seq_len)])
            Y.append(data[i + seq_len])
        return np.array(X), np.array(Y)

    def train_historical(self, traffic_data: List[float], epochs=20, lr=0.001, batch_size=64):
        """Обучение на переданном массиве данных (0-100)"""
        if len(traffic_data) <= self.lookback:
            return False
        
        X, Y = self._prepare_sequences(traffic_data, self.lookback)
        
        # Конвертация в тензоры
        X_tensor = torch.FloatTensor(X).unsqueeze(-1) # (samples, seq_len, 1)
        Y_tensor = torch.FloatTensor(Y).unsqueeze(-1) # (samples, 1)

        dataset = torch.utils.data.TensorDataset(X_tensor, Y_tensor)
        loader = torch.utils.data.DataLoader(dataset, batch_size=batch_size, shuffle=True)

        optimizer = torch.optim.Adam(self.model.parameters(), lr=lr)
        criterion = nn.MSELoss()

        self.model.train()
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
            
            if (epoch + 1) % 5 == 0:
                print(f"Epoch [{epoch+1}/{epochs}], Avg Loss: {total_loss/len(loader):.4f}")

        self.is_trained = True
        self.model.eval()
        self.save_model()
        return True

    def predict_future(self, recent_history: List[float], steps_ahead: int = 1) -> List[float]:
        if not self.is_trained:
            # Simple linear fallback if not trained
            last = recent_history[-1] if recent_history else 30.0
            return [last] * steps_ahead

        self.model.eval()
        predictions = []
        current_seq = recent_history[-self.lookback:]
        
        # Если история короче окна, дополняем средним
        if len(current_seq) < self.lookback:
            current_seq = [sum(recent_history)/len(recent_history)] * (self.lookback - len(current_seq)) + current_seq

        with torch.no_grad():
            for _ in range(steps_ahead):
                x_input = torch.FloatTensor(current_seq).view(1, self.lookback, 1).to(self.device)
                pred = self.model(x_input)
                val = pred.item()
                val = max(0.0, min(100.0, val))
                predictions.append(val)
                current_seq = current_seq[1:] + [val]

        return predictions

ai_lstm_brain = TrafficLSTM()
