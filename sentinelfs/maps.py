import copy
import pandas as pd

COLOR_MAP = {"Green": "#2ca25f", "Yellow": "#fec44f", "Red": "#de2d26"}


def _join_geojson(geojson: dict, value_df: pd.DataFrame, value_col: str, level_col: str):
    gj = copy.deepcopy(geojson)
    idx = value_df.set_index("country") if not value_df.empty else pd.DataFrame()
    for feat in gj.get("features", []):
        props = feat.setdefault("properties", {})
        cname = props.get("country_name")
        if cname is not None and not idx.empty and cname in idx.index:
            props[value_col] = float(idx.loc[cname, value_col])
            props[level_col] = str(idx.loc[cname, level_col])
        else:
            props[value_col] = 0.33
            props[level_col] = "Yellow"
    return gj


def _parse_popup_text(popup_value):
    if not popup_value or not isinstance(popup_value, str):
        return None
    lines = [line.strip() for line in popup_value.replace("<br>", "\n").split("\n") if line.strip()]
    parsed = {}
    for line in lines:
        if ":" not in line:
            continue
        k, v = line.split(":", 1)
        parsed[k.strip().lower()] = v.strip()
    country = parsed.get("country") or parsed.get("country_name")
    iso3 = parsed.get("iso_a3")
    if country:
        return {"country_name": country, "iso_a3": iso3}
    return None


def _extract_clicked_country(map_data):
    if not map_data:
        return None

    popup_data = _parse_popup_text(map_data.get("last_object_clicked_popup"))
    if popup_data:
        return popup_data

    clicked = map_data.get("last_object_clicked")
    if isinstance(clicked, dict):
        props = clicked.get("properties") or {}
        country_name = props.get("country_name")
        if country_name:
            return {"country_name": country_name, "iso_a3": props.get("iso_a3")}

    tooltip = map_data.get("last_object_clicked_tooltip")
    if isinstance(tooltip, str) and "Country" in tooltip and ":" in tooltip:
        country = tooltip.split(":", 1)[-1].split("<")[0].strip()
        if country:
            return {"country_name": country, "iso_a3": None}

    return None


def render_baseline_risk_map_folium(geojson: dict, latest_risk_df: pd.DataFrame):
    import folium
    from streamlit_folium import st_folium

    gj = _join_geojson(geojson, latest_risk_df.rename(columns={"risk_score": "risk_score", "risk_level": "risk_level"}), "risk_score", "risk_level")

    for feat in gj.get("features", []):
        props = feat.get("properties", {})
        popup_parts = [f"Country: {props.get('country_name', 'Unknown')}"]
        if props.get("iso_a3"):
            popup_parts.append(f"iso_a3: {props.get('iso_a3')}")
        props["popup_text"] = "\n".join(popup_parts)

    m = folium.Map(location=[18, 10], zoom_start=2, tiles="cartodbpositron")
    folium.GeoJson(
        gj,
        style_function=lambda feat: {
            "fillColor": COLOR_MAP.get(feat["properties"].get("risk_level", "Yellow"), "#fec44f"),
            "color": "#3f3f3f",
            "weight": 0.5,
            "fillOpacity": 0.78,
        },
        tooltip=folium.GeoJsonTooltip(fields=["country_name", "risk_level", "risk_score"], aliases=["Country", "Risk", "Score"]),
        popup=folium.GeoJsonPopup(fields=["popup_text"], labels=False),
    ).add_to(m)

    map_data = st_folium(
        m,
        width=None,
        height=560,
        key="baseline_map",
        returned_objects=["last_object_clicked_popup", "last_object_clicked", "last_active_drawing", "last_object_clicked_tooltip"],
    )
    return _extract_clicked_country(map_data)


def render_impact_map_folium(geojson: dict, impact_df: pd.DataFrame, show_hormuz: bool = False):
    import folium
    from streamlit_folium import st_folium

    gj = _join_geojson(geojson, impact_df.rename(columns={"impact_severity": "impact_severity", "impact_level": "impact_level"}), "impact_severity", "impact_level")
    m = folium.Map(location=[18, 10], zoom_start=2, tiles="cartodbpositron")
    folium.GeoJson(
        gj,
        style_function=lambda feat: {
            "fillColor": COLOR_MAP.get(feat["properties"].get("impact_level", "Yellow"), "#fec44f"),
            "color": "#3f3f3f",
            "weight": 0.5,
            "fillOpacity": 0.78,
        },
        tooltip=folium.GeoJsonTooltip(fields=["country_name", "impact_level", "impact_severity"], aliases=["Country", "Impact", "Severity"]),
        popup=folium.GeoJsonPopup(fields=["country_name", "iso_a3"], aliases=["Country", "ISO3"]),
    ).add_to(m)
    if show_hormuz:
        folium.Marker(location=[26.5, 56.3], tooltip="Hormuz chokepoint", icon=folium.Icon(color="red", icon="info-sign")).add_to(m)

    map_data = st_folium(m, width=None, height=540, key="impact_map", returned_objects=["last_object_clicked_popup", "last_object_clicked"])
    return _extract_clicked_country(map_data)
