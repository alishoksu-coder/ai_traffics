# backend/app/ml/metrics.py
"""
Модуль метрик качества моделей прогнозирования.

Содержит функции для расчёта MAE, RMSE и MAPE —
стандартных метрик оценки регрессионных моделей.
Используется для сравнения LSTM, Random Forest и baseline-методов.
"""
import math
from typing import Dict, List


def mae_rmse(y_true: List[float], y_pred: List[float]) -> Dict:
    """
    Рассчитывает MAE (Mean Absolute Error) и RMSE (Root Mean Square Error).

    Аргументы:
        y_true: список истинных значений загруженности (0-100).
        y_pred: список предсказанных значений загруженности (0-100).

    Возвращает:
        Словарь с ключами 'mae', 'rmse', 'n'.
    """
    n = min(len(y_true), len(y_pred))
    if n == 0:
        return {"mae": None, "rmse": None, "n": 0}

    abs_err = [abs(y_true[i] - y_pred[i]) for i in range(n)]
    sq_err = [(y_true[i] - y_pred[i]) ** 2 for i in range(n)]
    mae = sum(abs_err) / n
    rmse = math.sqrt(sum(sq_err) / n)
    return {"mae": mae, "rmse": rmse, "n": n}


def mape(y_true: List[float], y_pred: List[float]) -> Dict:
    """
    Рассчитывает MAPE (Mean Absolute Percentage Error).

    Пропускает точки, где y_true близко к нулю,
    чтобы избежать деления на ноль.
    """
    n = min(len(y_true), len(y_pred))
    if n == 0:
        return {"mape": None, "n": 0}

    errors = []
    for i in range(n):
        if abs(y_true[i]) > 1e-6:
            errors.append(abs(y_true[i] - y_pred[i]) / abs(y_true[i]))

    if not errors:
        return {"mape": None, "n": 0}

    return {"mape": sum(errors) / len(errors) * 100.0, "n": len(errors)}
