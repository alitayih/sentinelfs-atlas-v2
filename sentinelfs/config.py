from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
DB_PATH = ROOT / "sentinelfs_actions.db"

RISK_BINS = {
    "green_max": 0.33,
    "yellow_max": 0.66,
}

HORIZON_FACTORS = {7: 0.85, 14: 1.0, 30: 1.2}
