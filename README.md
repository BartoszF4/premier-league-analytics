# Premier League Analytics

**[Live demo](https://alto-msie-peripherals-motel.trycloudflare.com/)**

A SQL-backed data analytics project covering 11 seasons (2015/16 - 2025/26) of Premier League matches. Raw match data is normalized into a relational database, then queried to answer questions about home advantage, betting favorites, and referee tendencies. Results are served through an interactive dashboard, containerized and deployed on a self-hosted server.

## Tech stack

- Python (requests, pandas)
- SQLite
- SQL (schema design, CTEs, aggregations)
- Streamlit, Plotly
- Docker, Docker Compose
- Cloudflare Tunnel

## Data source

Match data: [football-data.co.uk](https://www.football-data.co.uk/englandm.php)

## Project structure

```
data/raw/        raw season CSV files
db/schema.sql    database schema
scripts/         data download, loading and query logic
dashboard/       Streamlit dashboard
```

## Setup

Local (without Docker):
```
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt

python scripts/download_data.py
python scripts/load_data.py
streamlit run dashboard/app.py
```

With Docker:
```
docker compose up -d --build
```

## Database schema

Five tables: `teams`, `seasons`, `matches`, `match_stats`, `match_odds`. Match facts, in-game statistics and betting odds are split into separate tables joined on `match_id`.

## Dashboard features

- League-wide favorite win rate, broken down by kickoff hour and weekday
- Referee tendencies: home-win bias, card averages
- Per-team "lucky referee" lookup
- Biggest upsets by betting odds

## Key findings

- Betting favorites win only 54.5% of matches across 2,658 games with valid odds - a reminder of how unpredictable football is.
- Favorites perform best in 20:00 kickoffs (59.3% win rate) and worst at 17:00 (50.0%) - likely reflecting which fixtures get selected for prime-time broadcast rather than kickoff time itself.
- Referees show a real spread in home-win rates under their officiating, from 53.9% down to 33.3%, though small sample sizes need care at the low end.

## Possible extensions

- Expected goals (xG) or match outcome prediction model
- Fantasy Premier League player data integration
- Scheduled updates as the 2026/27 season progresses