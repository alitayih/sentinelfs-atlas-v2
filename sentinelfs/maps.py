import pandas as pd

COLOR_MAP = {"Green": "#2ca25f", "Yellow": "#fec44f", "Red": "#de2d26"}


def _join_geojson(geojson: dict, value_df: pd.DataFrame, value_col: str, level_col: str):
    idx = value_df.set_index("country")
    for feat in geojson.get("features", []):
        cname = feat.get("properties", {}).get("country_name")
        if cname in idx.index:
            feat["properties"][value_col] = float(idx.loc[cname, value_col])
            feat["properties"][level_col] = str(idx.loc[cname, level_col])
        else:
            feat["properties"][value_col] = 0.0
            feat["properties"][level_col] = "Green"
    return geojson


def _extract_clicked_country(map_data):
    if not map_data:
        return None
    obj = map_data.get("last_object_clicked_tooltip") or map_data.get("last_active_drawing")
    if isinstance(obj, str) and "country_name:" in obj:
        return obj.split("country_name:")[-1].split("<")[0].strip()
    clicked = map_data.get("last_object_clicked")
    if isinstance(clicked, dict):
        props = clicked.get("properties") or {}
        return props.get("country_name")
    return None


def render_baseline_risk_map_folium(geojson: dict, latest_risk_df: pd.DataFrame):
    import folium
    from streamlit_folium import st_folium

    gj = _join_geojson(
        geojson,
        latest_risk_df.rename(columns={"risk_score": "score", "risk_level": "level"}),
        "score",
        "level",
    )
    m = folium.Map(location=[18, 10], zoom_start=2, tiles="cartodbpositron")
    folium.GeoJson(
        gj,
        style_function=lambda feat: {
            "fillColor": COLOR_MAP.get(feat["properties"].get("level", "Green"), "#2ca25f"),
            "color": "#3f3f3f",
            "weight": 0.4,
            "fillOpacity": 0.75,
        },
        tooltip=folium.GeoJsonTooltip(fields=["country_name", "level", "score"], aliases=["Country", "Risk", "Score"]),
    ).add_to(m)
    map_data = st_folium(m, width=None, height=560, key="baseline_map")
    return _extract_clicked_country(map_data)


def render_impact_map_folium(geojson: dict, impact_df: pd.DataFrame, show_hormuz: bool = False):
    import folium
    from streamlit_folium import st_folium

    gj = _join_geojson(
        geojson,
        impact_df.rename(columns={"impact_severity": "score", "impact_level": "level"}),
        "score",
        "level",
    )
    m = folium.Map(location=[18, 10], zoom_start=2, tiles="cartodbpositron")
    folium.GeoJson(
        gj,
        style_function=lambda feat: {
            "fillColor": COLOR_MAP.get(feat["properties"].get("level", "Green"), "#2ca25f"),
            "color": "#3f3f3f",
            "weight": 0.4,
            "fillOpacity": 0.75,
        },
        tooltip=folium.GeoJsonTooltip(fields=["country_name", "level", "score"], aliases=["Country", "Impact", "Severity"]),
    ).add_to(m)
    if show_hormuz:
        folium.Marker(
            location=[26.5, 56.3],
            tooltip="Hormuz chokepoint",
            icon=folium.Icon(color="red", icon="info-sign"),
        ).add_to(m)
    map_data = st_folium(m, width=None, height=540, key="impact_map")
    return _extract_clicked_country(map_data)
