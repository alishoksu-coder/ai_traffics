# backend/app/ml/preprocessing.py
"""
Модуль подготовки данных (Feature Engineering) для ML-моделей.

Включает:
- enrich_features() — обогащение датафрейма циклическими временными фичами,
  флагами выходного дня, часа пик, и коэффициентом погоды.
- group_by_location() — группировка истории трафика по location_id.
- get_trend_analysis() — определение направления тренда (up/down/stable).
- detect_anomaly() — обнаружение аномалий методом Z-score.
"""
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple


def enrich_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Добавляет инженерные фичи в датафрейм для обучения и инференса:
    - hour_sin, hour_cos (циклическое кодирование часа)
    - day_sin, day_cos (циклическое кодирование дня недели)
    - is_weekend, is_peak_hour
    - weather_factor
    """
    df = df.copy()

    # Определяем столбец datetime
    if 'timestamp' in df.columns:
        df['dt'] = pd.to_datetime(df['timestamp'])
        df['segment_id'] = df['intersection_id']
        df['value'] = df['congestion_level'] * 100.0
    elif 'created_at' in df.columns:
        df['dt'] = pd.to_datetime(df['created_at'])
    else:
        df['dt'] = pd.to_datetime('now')

    df['hour'] = df['dt'].dt.hour
    df['day_of_week'] = df['dt'].dt.dayofweek

    # 1. Циклическое время
    df['hour_sin'] = np.sin(2 * np.pi * df['hour'] / 24.0)
    df['hour_cos'] = np.cos(2 * np.pi * df['hour'] / 24.0)

    # 2. Циклический день недели
    df['day_sin'] = np.sin(2 * np.pi * df['day_of_week'] / 7.0)
    df['day_cos'] = np.cos(2 * np.pi * df['day_of_week'] / 7.0)

    # 3. Выходной день
    if 'is_weekend' not in df.columns:
        df['is_weekend'] = (df['day_of_week'] >= 5).astype(int)

    # 4. Часы пик (утро 7-9, вечер 17-20)
    if 'is_peak_hour' not in df.columns:
        df['is_peak_hour'] = ((df['hour'].between(7, 9)) | (df['hour'].between(17, 20))).astype(int)

    # 5. Погода
    if 'weather' in df.columns:
        weather_map = {'Clear': 0, 'Rain': 1, 'Snow': 2, 'Fog': 3}
        df['weather_encoded'] = df['weather'].map(weather_map).fillna(0)
        df['weather_factor'] = 1.0 + df['weather_encoded'] * 0.2
    else:
        if 'weather_factor' not in df.columns:
            df['weather_factor'] = 1.0

    # Заполняем пропуски
    if pd.api.types.is_numeric_dtype(df['weather_factor']):
        df = df.fillna(0)

    return df


def group_by_location(items: List[Dict]) -> Dict[int, List[Tuple[int, float]]]:
    """
    Группирует плоский список записей [{location_id, ts, value}, ...]
    в словарь {location_id: [(ts, value), ...]} с сортировкой по времени.
    """
    out: Dict[int, List[Tuple[int, float]]] = {}
    for it in items:
        lid = int(it["location_id"])
        out.setdefault(lid, []).append((int(it["ts"]), float(it["value"])))
    for lid in out:
        out[lid].sort(key=lambda x: x[0])
    return out


def get_trend_analysis(series: List[Tuple[int, float]], k: int = 15) -> Dict:
    """
    Анализирует тренд за последние k точек.
    Сравнивает среднее первой половины окна со средним второй половины.

    Возвращает:
        {"direction": "up"|"down"|"stable", "diff": float, "desc": str}
    """
    if len(series) < 5:
        return {"direction": "stable", "diff": 0, "desc": "Данных недостаточно"}

    tail = series[-k:]
    first_v = sum(v for _, v in tail[:len(tail) // 2]) / (len(tail) // 2)
    last_v = sum(v for _, v in tail[-(len(tail) // 2):]) / (len(tail) // 2)

    diff = last_v - first_v

    if diff > 5:
        return {"direction": "up", "diff": diff, "desc": "Растёт"}
    elif diff < -5:
        return {"direction": "down", "diff": diff, "desc": "Падает"}
    else:
        return {"direction": "stable", "diff": diff, "desc": "Стабильно"}


def detect_anomaly(series: List[Tuple[int, float]]) -> Dict:
    """
    Обнаружение аномалий с использованием Z-score.
    Если текущее значение отклоняется от скользящего среднего более чем на 2-3 sigma,
    фиксируется аномалия (возможное ДТП, перекрытие).
    """
    if len(series) < 5:
        return {"anomaly": False, "severity": "normal", "desc": "Данных недостаточно", "time_to_wait_min": 0}

    tail = series[-15:]
    vals = [v for _, v in tail]
    mean_v = np.mean(vals[:-1])
    std_v = np.std(vals[:-1])
    current_v = vals[-1]

    # Z-score
    z_score = (current_v - mean_v) / (std_v + 1e-5)

    start_v = tail[0][1]
    diff = current_v - start_v

    sudden_spike = any(vals[i] - vals[i - 1] > 25 for i in range(1, len(vals)))

    if sudden_spike and current_v > 70:
        return {
            "anomaly": True,
            "severity": "critical",
            "desc": "Обнаружена критическая аномалия: возможное ДТП. Скорость потока резко упала.",
            "time_to_wait_min": 45
        }
    elif z_score > 3.0 and current_v > 85:
        return {
            "anomaly": True,
            "severity": "critical",
            "desc": "Статистическая аномалия: трафик остановился не по графику. Ищите пути объезда.",
            "time_to_wait_min": 60
        }
    elif diff > 35 or current_v > 90:
        return {
            "anomaly": True,
            "severity": "critical",
            "desc": "Ситуация близка к коллапсу. Трафик почти остановился (возможно перекрытие).",
            "time_to_wait_min": 60
        }
    elif diff > 20 or z_score > 2.0:
        return {
            "anomaly": True,
            "severity": "warning",
            "desc": "Слишком быстрый рост заторов. Час пик формируется активнее прогноза.",
            "time_to_wait_min": 25
        }

    return {"anomaly": False, "severity": "normal", "desc": "Движение в пределах ожидаемого", "time_to_wait_min": 0}
