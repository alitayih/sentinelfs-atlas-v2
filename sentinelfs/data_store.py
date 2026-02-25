import sqlite3
import pandas as pd
import streamlit as st
from sentinelfs.config import DATA_DIR, DB_PATH
from sentinelfs.utils import load_json

GEOJSON_VERSION = "v4"


def load_signals() -> pd.DataFrame:
    return pd.read_csv(DATA_DIR / "demo_signals.csv", parse_dates=["date"])


def load_exposure() -> pd.DataFrame:
    return pd.read_csv(DATA_DIR / "demo_exposure.csv")


@st.cache_data(show_spinner=False)
def _load_geojson_cached(version: str) -> dict:
    return load_json(DATA_DIR / "ne_110m_admin_0_countries.geojson")


def load_geojson(version: str = GEOJSON_VERSION) -> dict:
    return _load_geojson_cached(version)


def load_scenarios() -> dict:
    return load_json(DATA_DIR / "scenarios.json")


def get_conn():
    return sqlite3.connect(DB_PATH, check_same_thread=False)


def init_actions_table() -> None:
    conn = get_conn()
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS actions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            owner TEXT,
            due_date TEXT,
            status TEXT,
            country TEXT,
            commodity TEXT,
            expected_risk_impact REAL,
            notes TEXT,
            outcome_notes TEXT,
            observed_impact REAL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    conn.commit()
    conn.close()


def add_action(record: dict) -> None:
    conn = get_conn()
    cols = ",".join(record.keys())
    placeholders = ",".join(["?"] * len(record))
    conn.execute(f"INSERT INTO actions ({cols}) VALUES ({placeholders})", list(record.values()))
    conn.commit()
    conn.close()


def list_actions(country: str | None = None) -> pd.DataFrame:
    conn = get_conn()
    if country:
        df = pd.read_sql_query("SELECT * FROM actions WHERE country = ? ORDER BY due_date", conn, params=[country])
    else:
        df = pd.read_sql_query("SELECT * FROM actions ORDER BY due_date", conn)
    conn.close()
    return df


def update_action_close(action_id: int, outcome_notes: str, observed_impact: float) -> None:
    conn = get_conn()
    conn.execute(
        "UPDATE actions SET status = 'Closed', outcome_notes = ?, observed_impact = ? WHERE id = ?",
        (outcome_notes, observed_impact, action_id),
    )
    conn.commit()
    conn.close()
