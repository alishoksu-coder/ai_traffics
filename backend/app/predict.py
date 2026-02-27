# app/predict.py
from typing import Dict, List, Tuple
import math


def group_by_location(items: List[Dict]) -> Dict[int, List[Tuple[int, float]]]:
    # items: [{location_id, ts, value}]
    out: Dict[int, List[Tuple[int, float]]] = {}
    for it in items:
        lid = int(it["location_id"])
        out.setdefault(lid, []).append((int(it["ts"]), float(it["value"])))
    for lid in out:
        out[lid].sort(key=lambda x: x[0])
    return out


def predict_naive(series: List[Tuple[int, float]]) -> float:
    return series[-1][1] if series else 0.0


def predict_moving_avg(series: List[Tuple[int, float]], k: int = 5) -> float:
    if not series:
        return 0.0
    tail = series[-k:]
    return sum(v for _, v in tail) / len(tail)


def predict_trend_lr(series: List[Tuple[int, float]], k: int = 10, horizon_min: int = 30) -> float:
    """
    Линейная регрессия по последним k точкам (t, y).
    t берём в минутах относительно начала окна.
    """
    if len(series) < 2:
        return predict_naive(series)

    tail = series[-k:]
    t0 = tail[0][0]
    xs = [(ts - t0) / 60.0 for ts, _ in tail]  # minutes
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


def mae_rmse(y_true: List[float], y_pred: List[float]) -> Dict:
    n = min(len(y_true), len(y_pred))
    if n == 0:
        return {"mae": None, "rmse": None, "n": 0}

    abs_err = [abs(y_true[i] - y_pred[i]) for i in range(n)]
    sq_err = [(y_true[i] - y_pred[i]) ** 2 for i in range(n)]
    mae = sum(abs_err) / n
    rmse = math.sqrt(sum(sq_err) / n)
    return {"mae": mae, "rmse": rmse, "n": n}
