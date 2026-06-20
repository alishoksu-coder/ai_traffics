# backend/app/ml/predictor.py
"""
Единый фасад (Facade) для всех ML-моделей прогнозирования трафика.

Этот модуль инкапсулирует:
1. Baseline-модели: Naive Forecast, Moving Average, EMA, Linear Regression.
2. Продвинутые модели: Random Forest (через ai_brain), LSTM (через lstm_model).
3. Ансамбль (Ensemble) — взвешенное среднее всех моделей.

Все модели инициализируются один раз при импорте модуля.
API-слой (routers) вызывает только функции этого модуля, не обращаясь к ML напрямую.
"""
from typing import Dict, List, Tuple

import numpy as np


# ──────────────────── Baseline-модели ────────────────────


def predict_naive(series: List[Tuple[int, float]]) -> float:
    """Наивный прогноз: последнее наблюдённое значение."""
    return series[-1][1] if series else 0.0


def predict_moving_avg(series: List[Tuple[int, float]], k: int = 5) -> float:
    """Скользящее среднее (Simple Moving Average) по последним k точкам."""
    if not series:
        return 0.0
    tail = series[-k:]
    return sum(v for _, v in tail) / len(tail)


def predict_weighted_ma(series_values: List[float]) -> float:
    """
    Взвешенная скользящая средняя (Weighted Moving Average).
    Более свежие данные имеют экспоненциально больший вес.
    """
    if not series_values:
        return 0.0
    weights = np.exp(np.linspace(-1., 0., len(series_values)))
    weights /= weights.sum()
    return float(np.dot(weights, series_values))


def predict_ema(series: List[Tuple[int, float]], alpha: float = 0.3) -> float:
    """
    Экспоненциальное скользящее среднее (EMA).
    Придаёт больший вес свежим данным. Полезно для резких изменений в трафике.

    Аргументы:
        alpha: коэффициент сглаживания (0 < alpha < 1). Чем больше, тем чувствительнее.
    """
    if not series:
        return 0.0
    ema = series[0][1]
    for _, val in series[1:]:
        ema = alpha * val + (1 - alpha) * ema
    return max(0.0, min(100.0, ema))


def predict_trend_lr(series: List[Tuple[int, float]], k: int = 10, horizon_min: int = 30) -> float:
    """
    Линейная регрессия по последним k точкам.
    Экстраполирует тренд на horizon_min минут вперёд.
    """
    if len(series) < 2:
        return predict_naive(series)

    tail = series[-k:]
    t0 = tail[0][0]
    xs = [(ts - t0) / 60.0 for ts, _ in tail]  # в минутах
    ys = [v for _, v in tail]

    n = len(xs)
    mx = sum(xs) / n
    my = sum(ys) / n

    num = sum((xs[i] - mx) * (ys[i] - my) for i in range(n))
    den = sum((xs[i] - mx) * (xs[i] - mx) for i in range(n))
    if den == 0:
        return predict_naive(series)

    a = num / den
    b = my - a * mx

    x_pred = xs[-1] + horizon_min
    y_pred = a * x_pred + b
    return max(0.0, min(100.0, y_pred))
