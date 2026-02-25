import json
import pandas as pd


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def traffic_light(score: float) -> str:
    if score <= 0.33:
        return "Green"
    if score <= 0.66:
        return "Yellow"
    return "Red"


def sigmoid(x: float) -> float:
    return 1 / (1 + (2.718281828 ** (-x)))


def fmt_pct(value: float) -> str:
    return f"{value * 100:.1f}%"


def ensure_datetime(df: pd.DataFrame, col: str) -> pd.DataFrame:
    out = df.copy()
    out[col] = pd.to_datetime(out[col])
    return out
