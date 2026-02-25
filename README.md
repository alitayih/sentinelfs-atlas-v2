# SentinelFS Atlas v2

SentinelFS Atlas is a **map-first** Streamlit app for anticipatory food/logistics risk monitoring.

## Features
- Clickable world polygon map on Home page (no country dropdown).
- Country Focus with simple and advanced diagnostics.
- Rule-based scenario simulation (including Hormuz Closure) with impact map.
- SQLite action tracking for mitigation plans.
- Plain-language guidance for non-experts.

## Repository layout
```text
.
├─ app.py
├─ pages/
│  ├─ 1_Map_Home.py
│  ├─ 2_Country_Focus.py
│  ├─ 3_Scenarios.py
│  ├─ 4_Action_Tracking.py
│  ├─ 5_Help_User_Manual.py
├─ sentinelfs/
│  ├─ __init__.py
│  ├─ config.py
│  ├─ data_store.py
│  ├─ risk_engine.py
│  ├─ scenario_engine.py
│  ├─ maps.py
│  ├─ ui.py
│  ├─ utils.py
├─ data/
│  ├─ world_countries.geojson
│  ├─ demo_signals.csv
│  ├─ demo_exposure.csv
│  ├─ scenarios.json
│  └─ README_DATA.md
├─ requirements.txt
└─ README.md
```

## Local run
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

## Streamlit Cloud deploy
1. Push to GitHub, using `main` branch.
2. In Streamlit Cloud, create app from this repo.
3. Set entrypoint to `app.py`.
4. Deploy, then use **Clear cache** and **Reboot app** if needed.

## Notes
- Demo data is synthetic.
- Maps use **Folium + streamlit-folium** only (no PyDeck).
