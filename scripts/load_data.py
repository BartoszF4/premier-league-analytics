import sqlite3
from pathlib import Path

import pandas as pd

ROOT_DIR = Path(__file__).resolve().parent.parent
RAW_DATA_DIR = ROOT_DIR / "data" / "raw"
SCHEMA_PATH = ROOT_DIR / "db" / "schema.sql"
DB_PATH = ROOT_DIR / "db" / "premier_league.db"

KEEP_COLUMNS = [
    "Date", "Time", "HomeTeam", "AwayTeam",
    "FTHG", "FTAG", "FTR", "HTHG", "HTAG", "HTR", "Referee",
    "HS", "AS", "HST", "AST", "HF", "AF", "HC", "AC",
    "HY", "AY", "HR", "AR",
    "AvgH", "AvgD", "AvgA", "MaxH", "MaxD", "MaxA",
]


def season_code_to_label(code: str) -> str:
    return f"20{code[:2]}/{code[2:]}"


def create_schema(conn: sqlite3.Connection) -> None:
    conn.executescript(SCHEMA_PATH.read_text())


def get_or_create_id(conn: sqlite3.Connection, table: str, id_col: str,
                      value_col: str, value: str) -> int:
    row = conn.execute(
        f"SELECT {id_col} FROM {table} WHERE {value_col} = ?", (value,)
    ).fetchone()
    if row:
        return row[0]

    cursor = conn.execute(
        f"INSERT INTO {table} ({value_col}) VALUES (?)", (value,)
    )
    return cursor.lastrowid


def load_file(conn: sqlite3.Connection, csv_path: Path, season_label: str) -> int:
    df = pd.read_csv(csv_path)
    available = [c for c in KEEP_COLUMNS if c in df.columns]
    df = df[available]

    season_id = get_or_create_id(conn, "seasons", "season_id", "label", season_label)

    rows_loaded = 0
    for _, row in df.iterrows():
        if pd.isna(row.get("HomeTeam")) or pd.isna(row.get("FTHG")):
            continue

        home_team_id = get_or_create_id(conn, "teams", "team_id", "name", row["HomeTeam"])
        away_team_id = get_or_create_id(conn, "teams", "team_id", "name", row["AwayTeam"])

        match_date = pd.to_datetime(row["Date"], dayfirst=True).strftime("%Y-%m-%d")
        kickoff_time = row.get("Time") if "Time" in df.columns and not pd.isna(row.get("Time")) else None

        cursor = conn.execute(
            """
            INSERT INTO matches (
                season_id, match_date, kickoff_time,
                home_team_id, away_team_id,
                home_goals, away_goals, result,
                home_goals_ht, away_goals_ht, result_ht, referee
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                season_id, match_date, kickoff_time,
                home_team_id, away_team_id,
                int(row["FTHG"]), int(row["FTAG"]), row["FTR"],
                row.get("HTHG"), row.get("HTAG"), row.get("HTR"),
                row.get("Referee"),
            ),
        )
        match_id = cursor.lastrowid

        conn.execute(
            """
            INSERT INTO match_stats (
                match_id, home_shots, away_shots,
                home_shots_on_target, away_shots_on_target,
                home_corners, away_corners, home_fouls, away_fouls,
                home_yellow_cards, away_yellow_cards,
                home_red_cards, away_red_cards
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                match_id, row.get("HS"), row.get("AS"),
                row.get("HST"), row.get("AST"),
                row.get("HC"), row.get("AC"), row.get("HF"), row.get("AF"),
                row.get("HY"), row.get("AY"), row.get("HR"), row.get("AR"),
            ),
        )

        conn.execute(
            """
            INSERT INTO match_odds (
                match_id, avg_home_odds, avg_draw_odds, avg_away_odds,
                max_home_odds, max_draw_odds, max_away_odds
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                match_id, row.get("AvgH"), row.get("AvgD"), row.get("AvgA"),
                row.get("MaxH"), row.get("MaxD"), row.get("MaxA"),
            ),
        )
        rows_loaded += 1

    return rows_loaded


def main() -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)

    create_schema(conn)

    csv_files = sorted(RAW_DATA_DIR.glob("E0_*.csv"))
    if not csv_files:
        print(f"No CSV files found in {RAW_DATA_DIR}. Run download_data.py first")
        return

    for csv_path in csv_files:
        code = csv_path.stem.replace("E0_", "")
        label = season_code_to_label(code)
        count = load_file(conn, csv_path, label)
        print(f"Season {label}: loaded {count} matches")

    conn.commit()
    conn.close()
    print(f"\nDone. Database saved at: {DB_PATH}")


if __name__ == "__main__":
    main()