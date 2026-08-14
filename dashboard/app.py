import sys
from pathlib import Path

import plotly.express as px
import streamlit as st

sys.path.append(str(Path(__file__).resolve().parent.parent / "scripts"))

from queries import (
    get_connection,
    get_favorite_win_rate_overall,
    get_favorite_win_rate_by_hour,
    get_favorite_win_rate_by_weekday,
    get_referee_stats,
    get_biggest_upsets,
    get_referee_impact_for_team,
    get_all_team_names,
)

st.set_page_config(page_title="Premier League Analytics", layout="wide")

conn = get_connection()

st.title("Premier League Analytics")
st.caption("11 seasons of Premier League data (2015/16 - 2025/26)")

overall = get_favorite_win_rate_overall(conn)
col1, col2, col3 = st.columns(3)
col1.metric("Matches analyzed", int(overall["total_matches"][0]))
col2.metric("Favorite win rate", f"{overall['favorite_win_pct'][0]}%")
col3.metric("Seasons covered", 11)

st.divider()

col_left, col_right = st.columns(2)

with col_left:
    st.subheader("Favorite win rate by kickoff hour")
    hour_df = get_favorite_win_rate_by_hour(conn)
    fig_hour = px.bar(hour_df, x="kickoff_hour", y="favorite_win_pct",
                       labels={"kickoff_hour": "Kickoff hour", "favorite_win_pct": "Favorite win rate (%)"})
    st.plotly_chart(fig_hour, use_container_width=True)

with col_right:
    st.subheader("Favorite win rate by weekday")
    weekday_df = get_favorite_win_rate_by_weekday(conn)
    fig_weekday = px.bar(weekday_df, x="weekday", y="favorite_win_pct",
                          labels={"weekday": "Weekday", "favorite_win_pct": "Favorite win rate (%)"})
    st.plotly_chart(fig_weekday, use_container_width=True)

st.divider()

st.subheader("Referee tendencies")
min_matches = st.slider("Minimum matches officiated", 10, 100, 30)
referee_df = get_referee_stats(conn, min_matches=min_matches)
st.dataframe(referee_df, use_container_width=True)

st.divider()

st.subheader("Find your team's lucky referee")
team_names = get_all_team_names(conn)
selected_team = st.selectbox("Select a team", team_names, index=team_names.index("Chelsea") if "Chelsea" in team_names else 0)
team_min_matches = st.slider("Minimum matches with this referee", 5, 30, 10)
team_ref_df = get_referee_impact_for_team(conn, selected_team, min_matches=team_min_matches)
st.dataframe(team_ref_df, use_container_width=True)

st.divider()

st.subheader("Biggest upsets")
upsets_df = get_biggest_upsets(conn)
st.dataframe(upsets_df, use_container_width=True)

conn.close()