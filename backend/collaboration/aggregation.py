from __future__ import annotations

from typing import List


def average_curve(curves: List[List[float]]) -> List[float]:
    if not curves:
        return []
    length = len(curves[0])
    return [round(sum(curve[i] for curve in curves) / len(curves), 4) for i in range(length)]


def weighted_curve(curves: List[List[float]], weights: List[float]) -> List[float]:
    if not curves:
        return []
    total = max(sum(weights), 1e-6)
    length = len(curves[0])
    return [round(sum(curve[i] * w for curve, w in zip(curves, weights)) / total, 4) for i in range(length)]


def weighted_scalar(values: List[float], weights: List[float]) -> float:
    total = max(sum(weights), 1e-6)
    return round(sum(v * w for v, w in zip(values, weights)) / total, 4)
