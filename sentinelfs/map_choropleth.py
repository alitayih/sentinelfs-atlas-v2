import json
import hashlib
import pandas as pd
import streamlit as st
import plotly.express as px

RISK_COLORSCALE = [
    [0.0, "#2ca25f"],
    [0.33, "#2ca25f"],
    [0.34, "#fec44f"],
    [0.66, "#fec44f"],
    [0.67, "#de2d26"],
    [1.0, "#de2d26"],
]

COMMODITY_MULTIPLIER = {
    "All": 1.00,
    "Wheat": 1.07,
    "Rice": 0.96,
    "Frozen Protein": 1.12,
}


@st.cache_data(show_spinner=False)
def load_admin0_geojson(path: str):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


@st.cache_data(show_spinner=False)
def build_country_risk_df(signals_df: pd.DataFrame, geojson: dict, window_days: int, commodity: str) -> pd.DataFrame:
    max_date = signals_df["date"].max()
    scoped = signals_df[signals_df["date"] >= (max_date - pd.Timedelta(days=window_days - 1))].copy()

    scoped["baseline_score"] = (
        0.35 * scoped["conflict_intensity"]
        + 0.25 * scoped["freight_volatility"]
        + 0.2 * scoped["export_restriction_score"]
        + 0.2 * scoped["escalation_probability"]
    ).clip(0, 1)

    latest = scoped.sort_values("date").groupby("country").tail(1).copy()
    mean_scores = scoped.groupby("country", as_index=False)["baseline_score"].mean().rename(columns={"baseline_score":"mean_score"})
    latest = latest.merge(mean_scores, on="country", how="left")
    latest["risk_score"] = (0.65 * latest["baseline_score"] + 0.35 * latest["mean_score"]).clip(0, 1)
    latest["risk_score"] = (latest["risk_score"] * COMMODITY_MULTIPLIER.get(commodity, 1.0)).clip(0, 1)

    idx = {f["properties"].get("country_name"): f["properties"].get("iso_a3") for f in geojson.get("features", [])}
    latest["iso3"] = latest["country"].map(idx)
    latest = latest.dropna(subset=["iso3"]).copy()
    latest["country_name"] = latest["country"]
    latest["risk_score"] = (latest["risk_score"] * 100).round(1)
    latest["risk_level"] = pd.cut(
        latest["risk_score"],
        bins=[-0.001, 33, 66, 100],
        labels=["Low", "Med", "High"],
    ).astype(str)
    latest["commodity"] = commodity
    latest["window_days"] = window_days

    return latest[["iso3", "country_name", "risk_score", "risk_level", "commodity", "window_days"]].sort_values("country_name")


def _stable_uirevision(window_days: int, commodity: str):
    return hashlib.md5(f"{window_days}:{commodity}".encode()).hexdigest()[:12]


def render_country_choropleth(risk_df: pd.DataFrame, geojson: dict, window_days: int, commodity: str):
    fig = px.choropleth(
        risk_df,
        geojson=geojson,
        locations="iso3",
        featureidkey="properties.iso_a3",
        color="risk_score",
        color_continuous_scale=RISK_COLORSCALE,
        range_color=(0, 100),
        hover_name="country_name",
        custom_data=["iso3", "country_name", "risk_level", "commodity", "window_days", "risk_score"],
        labels={"risk_score": "Risk score"},
        projection="equirectangular",
    )

    fig.update_traces(
        marker_line_width=0.5,
        marker_line_color="#6d6d6d",
        hovertemplate=(
            "<b>%{customdata[1]}</b><br>"
            "ISO3: %{customdata[0]}<br>"
            "Risk score: %{customdata[5]}<br>"
            "Risk level: %{customdata[2]}<br>"
            "Commodity: %{customdata[3]}<br>"
            "Date window: %{customdata[4]} days<extra></extra>"
        ),
    )
    fig.update_geos(showcoastlines=False, showframe=False, bgcolor="rgba(0,0,0,0)")
    fig.update_layout(margin={"l": 0, "r": 0, "t": 0, "b": 0}, uirevision=_stable_uirevision(window_days, commodity), coloraxis_colorbar_title="Risk")
    return fig
