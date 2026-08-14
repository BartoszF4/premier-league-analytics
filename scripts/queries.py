import sqlite3
from pathlib import Path

import pandas as pd

DB_PATH = Path(__file__).resolve().parent.parent / "db" / "premier_league.db"

FAVORITE_CTE = """
WITH favorites AS (
    SELECT
        m.match_id,
        m.match_date,
        m.kickoff_time,
        m.result,
        CASE
            WHEN mo.avg_home_odds < mo.avg_away_odds AND mo.avg_home_odds < mo.avg_draw_odds THEN 'H'
            WHEN mo.avg_away_odds < mo.avg_home_odds AND mo.avg_away_odds < mo.avg_draw_odds THEN 'A'
            ELSE NULL
        END AS favorite_side
    FROM matches m
    JOIN match_odds mo ON mo.match_id = m.match_id
    WHERE mo.avg_home_odds IS NOT NULL
)
"""


def get_connection() -> sqlite3.Connection:
    return sqlite3.connect(DB_PATH)


def get_favorite_win_rate_overall(conn: sqlite3.Connection) -> pd.DataFrame:
    query = FAVORITE_CTE + """
    SELECT
        COUNT(*) AS total_matches,
        SUM(CASE WHEN favorite_side = result THEN 1 ELSE 0 END) AS favorite_won,
        ROUND(100.0 * SUM(CASE WHEN favorite_side = result THEN 1 ELSE 0 END) / COUNT(*), 1) AS favorite_win_pct
    FROM favorites
    WHERE favorite_side IS NOT NULL
    """
    return pd.read_sql_query(query, conn)


def get_favorite_win_rate_by_hour(conn: sqlite3.Connection) -> pd.DataFrame:
    query = FAVORITE_CTE + """
    SELECT
        CAST(SUBSTR(kickoff_time, 1, 2) AS INTEGER) AS kickoff_hour,
        COUNT(*) AS total_matches,
        ROUND(100.0 * SUM(CASE WHEN favorite_side = result THEN 1 ELSE 0 END) / COUNT(*), 1) AS favorite_win_pct
    FROM favorites
    WHERE favorite_side IS NOT NULL AND kickoff_time IS NOT NULL
    GROUP BY kickoff_hour
    ORDER BY kickoff_hour
    """
    return pd.read_sql_query(query, conn)


def get_favorite_win_rate_by_weekday(conn: sqlite3.Connection) -> pd.DataFrame:
    query = FAVORITE_CTE + """
    SELECT
        CASE CAST(strftime('%w', match_date) AS INTEGER)
            WHEN 0 THEN 'Sunday'
            WHEN 1 THEN 'Monday'
            WHEN 2 THEN 'Tuesday'
            WHEN 3 THEN 'Wednesday'
            WHEN 4 THEN 'Thursday'
            WHEN 5 THEN 'Friday'
            WHEN 6 THEN 'Saturday'
        END AS weekday,
        CAST(strftime('%w', match_date) AS INTEGER) AS weekday_num,
        COUNT(*) AS total_matches,
        ROUND(100.0 * SUM(CASE WHEN favorite_side = result THEN 1 ELSE 0 END) / COUNT(*), 1) AS favorite_win_pct
    FROM favorites
    WHERE favorite_side IS NOT NULL
    GROUP BY weekday, weekday_num
    ORDER BY weekday_num
    """
    return pd.read_sql_query(query, conn)


def get_referee_stats(conn: sqlite3.Connection, min_matches: int = 30) -> pd.DataFrame:
    query = """
    SELECT
        m.referee,
        COUNT(*) AS matches_officiated,
        ROUND(100.0 * SUM(CASE WHEN m.result = 'H' THEN 1 ELSE 0 END) / COUNT(*), 1) AS home_win_pct,
        ROUND(AVG(ms.home_yellow_cards + ms.away_yellow_cards), 2) AS avg_yellow_cards,
        ROUND(AVG(ms.home_red_cards + ms.away_red_cards), 2) AS avg_red_cards
    FROM matches m
    JOIN match_stats ms ON ms.match_id = m.match_id
    WHERE m.referee IS NOT NULL
    GROUP BY m.referee
    HAVING matches_officiated >= ?
    ORDER BY home_win_pct DESC
    """
    return pd.read_sql_query(query, conn, params=(min_matches,))


def get_biggest_upsets(conn: sqlite3.Connection, min_odds: float = 5.0, limit: int = 15) -> pd.DataFrame:
    query = """
    SELECT
        m.match_date,
        ht.name AS home_team,
        at.name AS away_team,
        m.home_goals,
        m.away_goals,
        m.result,
        mo.avg_home_odds,
        mo.avg_draw_odds,
        mo.avg_away_odds
    FROM matches m
    JOIN teams ht ON ht.team_id = m.home_team_id
    JOIN teams at ON at.team_id = m.away_team_id
    JOIN match_odds mo ON mo.match_id = m.match_id
    WHERE
        (m.result = 'A' AND mo.avg_away_odds >= ?)
        OR (m.result = 'H' AND mo.avg_home_odds >= ?)
    ORDER BY
        CASE WHEN m.result = 'A' THEN mo.avg_away_odds ELSE mo.avg_home_odds END DESC
    LIMIT ?
    """
    return pd.read_sql_query(query, conn, params=(min_odds, min_odds, limit))


def get_referee_impact_for_team(conn: sqlite3.Connection, team_name: str, min_matches: int = 10) -> pd.DataFrame:
    query = """
    SELECT
        m.referee,
        COUNT(*) AS matches,
        SUM(CASE
            WHEN (m.home_team_id = t.team_id AND m.result = 'H')
              OR (m.away_team_id = t.team_id AND m.result = 'A') THEN 3
            WHEN m.result = 'D' THEN 1
            ELSE 0
        END) AS points,
        ROUND(1.0 * SUM(CASE
            WHEN (m.home_team_id = t.team_id AND m.result = 'H')
              OR (m.away_team_id = t.team_id AND m.result = 'A') THEN 3
            WHEN m.result = 'D' THEN 1
            ELSE 0
        END) / COUNT(*), 2) AS points_per_match,
        ROUND(100.0 * SUM(CASE
            WHEN (m.home_team_id = t.team_id AND m.result = 'H')
              OR (m.away_team_id = t.team_id AND m.result = 'A') THEN 1
            ELSE 0
        END) / COUNT(*), 1) AS win_pct
    FROM matches m
    JOIN teams t ON t.name = ?
    WHERE m.home_team_id = t.team_id OR m.away_team_id = t.team_id
    GROUP BY m.referee
    HAVING matches >= ?
    ORDER BY points_per_match DESC
    """
    return pd.read_sql_query(query, conn, params=(team_name, min_matches))


def get_all_team_names(conn: sqlite3.Connection) -> list[str]:
    rows = conn.execute("SELECT name FROM teams ORDER BY name").fetchall()
    return [row[0] for row in rows]