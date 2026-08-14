from queries import (
    get_connection,
    get_favorite_win_rate_overall,
    get_favorite_win_rate_by_hour,
    get_favorite_win_rate_by_weekday,
    get_referee_stats,
    get_biggest_upsets,
)


def print_df(title: str, df) -> None:
    print(f"\n=== {title} ===")
    print(df.to_string(index=False))


def main() -> None:
    conn = get_connection()

    print_df("Favorite win rate (overall)", get_favorite_win_rate_overall(conn))
    print_df("Favorite win rate by kickoff hour", get_favorite_win_rate_by_hour(conn))
    print_df("Favorite win rate by weekday", get_favorite_win_rate_by_weekday(conn))
    print_df("Referee stats (min 30 matches)", get_referee_stats(conn, min_matches=30))
    print_df("Biggest upsets (odds >= 5.0)", get_biggest_upsets(conn))

    conn.close()


if __name__ == "__main__":
    main()