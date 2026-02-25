import pandas as pd
from sentinelfs.utils import traffic_light


def compute_baseline_risk(signals: pd.DataFrame, window_days: int = 90) -> pd.DataFrame:
    max_date = signals["date"].max()
    scoped = signals[signals["date"] >= (max_date - pd.Timedelta(days=window_days - 1))].copy()
    scoped["risk_score"] = (
        0.35 * scoped["conflict_intensity"]
        + 0.25 * scoped["freight_volatility"]
        + 0.2 * scoped["export_restriction_score"]
        + 0.2 * scoped["escalation_probability"]
    ).clip(0, 1)
    latest = scoped.sort_values("date").groupby("country").tail(1).copy()
    latest["risk_level"] = latest["risk_score"].map(traffic_light)
    return latest[["country", "date", "risk_score", "risk_level"]].sort_values("country")


def detect_trend(signals: pd.DataFrame, country: str) -> str:
    cdf = signals[signals["country"] == country].sort_values("date").tail(14).copy()
    if len(cdf) < 4:
        return "stable"
    cdf["score"] = (
        0.35 * cdf["conflict_intensity"]
        + 0.25 * cdf["freight_volatility"]
        + 0.2 * cdf["export_restriction_score"]
        + 0.2 * cdf["escalation_probability"]
    )
    slope = cdf["score"].iloc[-1] - cdf["score"].iloc[0]
    if slope > 0.06:
        return "up"
    if slope < -0.06:
        return "down"
    return "stable"
