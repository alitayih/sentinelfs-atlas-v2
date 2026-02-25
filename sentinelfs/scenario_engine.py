import pandas as pd
from sentinelfs.config import HORIZON_FACTORS
from sentinelfs.utils import sigmoid, traffic_light


def simulate_scenario(latest_risk: pd.DataFrame, exposure: pd.DataFrame, scenario_name: str, base_impact: float, severity: int, horizon_days: int):
    merged = latest_risk.merge(exposure, left_on="country", right_on="country", how="left").fillna(0)
    horizon_factor = HORIZON_FACTORS.get(horizon_days, 1.0)
    sev_factor = severity / 5

    merged["impact_shipping"] = base_impact * merged["shipping_route_dependency"] * sev_factor * horizon_factor
    merged["impact_price"] = base_impact * merged["energy_dependency"] * sev_factor * horizon_factor
    weighted = (
        1.3 * merged["impact_shipping"]
        + 1.1 * merged["impact_price"]
        + 0.8 * merged["food_import_dependency"]
        - 0.9 * merged["reserve_buffer_score"]
    )
    merged["supply_disruption_prob"] = (weighted.apply(sigmoid) * 100).clip(0, 100)
    merged["impact_severity"] = (
        0.25 * merged["risk_score"]
        + 0.3 * merged["impact_shipping"]
        + 0.25 * merged["impact_price"]
        + 0.2 * (merged["supply_disruption_prob"] / 100)
    ).clip(0, 1)
    merged["impact_level"] = merged["impact_severity"].map(traffic_light)
    merged["confidence"] = (55 + 35 * (1 - (merged["reserve_buffer_score"] - 0.5).abs())).clip(50, 95)

    def top_factors(row):
        items = {
            "shipping_route_dependency": row["shipping_route_dependency"],
            "energy_dependency": row["energy_dependency"],
            "food_import_dependency": row["food_import_dependency"],
            "reserve_buffer_score": 1 - row["reserve_buffer_score"],
            "baseline_risk": row["risk_score"],
        }
        return ", ".join([k for k, _ in sorted(items.items(), key=lambda x: x[1], reverse=True)[:3]])

    merged["top_contributors"] = merged.apply(top_factors, axis=1)
    assumptions = {
        "scenario": scenario_name,
        "base_impact": base_impact,
        "severity": severity,
        "horizon_days": horizon_days,
        "horizon_factor": horizon_factor,
        "method": "rule_based_v1",
    }
    return merged, assumptions


def second_order_effects(scenario_name: str):
    base = [
        "Retail shelf prices can adjust 1-3 weeks after shipping disruptions.",
        "Upstream supplier lead times may become less reliable.",
        "Working capital pressure may increase due to safety-stock decisions.",
    ]
    if scenario_name == "Hormuz Closure":
        base.insert(0, "Fuel and bunker costs can spike quickly, increasing landed cost.")
    return base
