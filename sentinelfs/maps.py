import copy
import re
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


def _popup_html_to_selection(popup_value: str | None):
    if not popup_value or not isinstance(popup_value, str):
        return None
    txt = re.sub(r"<[^>]+>", "\n", popup_value)
    txt = re.sub(r"\s+", " ", txt).strip()
    country = None
    iso3 = None

    m_country = re.search(r"Country\s*([^A-Z].*?)\s*(ISO3|$)", txt, flags=re.IGNORECASE)
    if m_country:
        country = m_country.group(1).strip(" :")

    m_iso = re.search(r"ISO3\s*([A-Z0-9-]{3,})", txt, flags=re.IGNORECASE)
    if m_iso:
        iso3 = m_iso.group(1).strip()

    # fallback for popup text "Country: X | ISO3: Y"
    if not country and "Country:" in popup_value:
        country = popup_value.split("Country:", 1)[1].split("|")[0].split("<")[0].strip()
    if not iso3 and "ISO3:" in popup_value:
        iso3 = popup_value.split("ISO3:", 1)[1].split("<")[0].strip()

    if country:
        return {"country_name": country, "iso_a3": iso3 or None}
    return None


def _extract_clicked_country(map_data):
    if not map_data:
        return None

    popup_data = _popup_html_to_selection(map_data.get("last_object_clicked_popup"))
    if popup_data:
        return popup_data

    clicked = map_data.get("last_object_clicked")
    if isinstance(clicked, dict):
        props = clicked.get("properties") or {}
        cname = props.get("country_name")
        if cname:
            return {"country_name": cname, "iso_a3": props.get("iso_a3")}

    return None


def render_baseline_risk_map_folium(geojson: dict, latest_risk_df: pd.DataFrame):
    import folium
    from streamlit_folium import st_folium

    gj = _join_geojson(geojson, latest_risk_df, "risk_score", "risk_level")
    m = folium.Map(location=[18, 10], zoom_start=2, tiles="cartodbpositron")

    folium.GeoJson(
        gj,
        style_function=lambda feat: {
            "fillColor": COLOR_MAP.get(feat["properties"].get("risk_level", "Yellow"), "#fec44f"),
            "color": "#666666",
            "weight": 0.7,
            "fillOpacity": 0.72,
        },
        highlight_function=lambda feat: {
            "color": "#111111",
            "weight": 2.0,
            "fillOpacity": 0.9,
        },
        tooltip=folium.GeoJsonTooltip(
            fields=["country_name", "risk_level", "risk_score"],
            aliases=["Country", "Risk", "Score"],
            localize=True,
            sticky=True,
        ),
        popup=folium.GeoJsonPopup(fields=["country_name", "iso_a3"], aliases=["Country", "ISO3"]),
    ).add_to(m)

    map_data = st_folium(
        m,
        width=None,
        height=560,
        key="baseline_map_v3",
        returned_objects=["last_object_clicked_popup", "last_object_clicked"],
    )
    return _extract_clicked_country(map_data)


def render_impact_map_folium(geojson: dict, impact_df: pd.DataFrame, show_hormuz: bool = False):
    import folium
    from streamlit_folium import st_folium

    gj = _join_geojson(geojson, impact_df.rename(columns={"impact_severity": "risk_score", "impact_level": "risk_level"}), "risk_score", "risk_level")
    m = folium.Map(location=[18, 10], zoom_start=2, tiles="cartodbpositron")
    folium.GeoJson(
        gj,
        style_function=lambda feat: {
            "fillColor": COLOR_MAP.get(feat["properties"].get("risk_level", "Yellow"), "#fec44f"),
            "color": "#666666",
            "weight": 0.7,
            "fillOpacity": 0.72,
        },
        highlight_function=lambda feat: {"color": "#111111", "weight": 2.0, "fillOpacity": 0.9},
        tooltip=folium.GeoJsonTooltip(fields=["country_name", "risk_level", "risk_score"], aliases=["Country", "Impact", "Severity"]),
        popup=folium.GeoJsonPopup(fields=["country_name", "iso_a3"], aliases=["Country", "ISO3"]),
    ).add_to(m)

    if show_hormuz:
        folium.Marker(location=[26.5, 56.3], tooltip="Hormuz chokepoint", icon=folium.Icon(color="red", icon="info-sign")).add_to(m)

    map_data = st_folium(m, width=None, height=540, key="impact_map_v3", returned_objects=["last_object_clicked_popup", "last_object_clicked"])
    return _extract_clicked_country(map_data)
