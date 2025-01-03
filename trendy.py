import streamlit as st
from nba_api.stats.endpoints import (
    leaguedashteamstats,
    leaguedashteamshotlocations,
)
import pandas as pd
import numpy as np
import time


# Fetch NBA team stats
def fetch_basic_team_stats():
    wanted = [
        "TEAM_ID",
        "TEAM_NAME",
        "W_PCT",
        "FG3A",
        "FG3_PCT",
        "FTA",
        "FT_PCT",
        "FGA",
    ]

    stats = leaguedashteamstats.LeagueDashTeamStats(
        season="2024-25",
        season_type_all_star="Regular Season",
    ).get_data_frames()[0]

    return stats[wanted]


def fetch_advanced_team_stats():
    wanted = ["TEAM_ID", "NET_RATING", "PACE", "TM_TOV_PCT", "OREB_PCT", "DREB_PCT"]

    stats = leaguedashteamstats.LeagueDashTeamStats(
        season="2024-25",
        season_type_all_star="Regular Season",
        measure_type_detailed_defense="Advanced",
    ).get_data_frames()[0]

    return stats[wanted]


def fetch_opponent_team_stats():
    wanted = ["TEAM_ID", "OPP_FG3A", "OPP_FG3_PCT", "OPP_FTA", "OPP_FT_PCT", "OPP_FGA"]

    stats = leaguedashteamstats.LeagueDashTeamStats(
        season="2024-25",
        season_type_all_star="Regular Season",
        measure_type_detailed_defense="Opponent",
    ).get_data_frames()[0]

    return stats[wanted]


def fetch_four_factors_team_stats():
    wanted = ["TEAM_ID", "OPP_TOV_PCT"]

    stats = leaguedashteamstats.LeagueDashTeamStats(
        season="2024-25",
        season_type_all_star="Regular Season",
        measure_type_detailed_defense="Four Factors",
    ).get_data_frames()[0]

    return stats[wanted]


def fetch_rim_stats():
    team_ids = [
        1610612737,
        1610612738,
        1610612739,
        1610612740,
        1610612741,
        1610612742,
        1610612743,
        1610612744,
        1610612745,
        1610612746,
        1610612747,
        1610612748,
        1610612749,
        1610612750,
        1610612751,
        1610612752,
        1610612753,
        1610612754,
        1610612755,
        1610612756,
        1610612757,
        1610612758,
        1610612759,
        1610612760,
        1610612761,
        1610612762,
        1610612763,
        1610612764,
        1610612765,
        1610612766,
    ]

    rim_stats_list = []
    opponent_rim_stats_list = []

    for team_id in team_ids:
        try:
            team_rim = leaguedashteamshotlocations.LeagueDashTeamShotLocations(
                team_id_nullable=team_id,
                season="2024-25",
                season_type_all_star="Regular Season",
                distance_range="5ft Range",
            ).get_data_frames()[0]

            opponent_rim = leaguedashteamshotlocations.LeagueDashTeamShotLocations(
                team_id_nullable=team_id,
                season="2024-25",
                season_type_all_star="Regular Season",
                measure_type_simple="Opponent",
                distance_range="5ft Range",
            ).get_data_frames()[0]

            team_rim_stats = {
                "TEAM_ID": team_id,
                "FGA_RIM": team_rim.iloc[0, 3],
                "FG_PCT": team_rim.iloc[0, 4],
            }

            opponent_rim_stats = {
                "TEAM_ID": team_id,
                "FGA_RIM_OPP": opponent_rim.iloc[0, 3],
                "FG_PCT_OPP": opponent_rim.iloc[0, 4],
            }

            rim_stats_list.append(team_rim_stats)
            opponent_rim_stats_list.append(opponent_rim_stats)

        except Exception as e:
            print(f"Error fetching rim stats for Team ID {team_id}: {e}")
        time.sleep(1)

    return pd.DataFrame(rim_stats_list), pd.DataFrame(opponent_rim_stats_list)


def combine_stats():
    stats = fetch_basic_team_stats()

    advanced_team_stats = fetch_advanced_team_stats()
    opponent_team_stats = fetch_opponent_team_stats()
    four_factors_team_stats = fetch_four_factors_team_stats()
    team_rim_stats, opponent_rim_stats = fetch_rim_stats()

    stats = stats.merge(advanced_team_stats, on="TEAM_ID", how="left")
    stats = stats.merge(opponent_team_stats, on="TEAM_ID", how="left")
    stats = stats.merge(four_factors_team_stats, on="TEAM_ID", how="left")

    # Rename the rim stats column to avoid duplication
    stats = stats.merge(team_rim_stats, on="TEAM_ID", how="left")
    stats = stats.merge(opponent_rim_stats, on="TEAM_ID", how="left")

    # Rim-related calculations
    stats["RimFGAr"] = stats["FGA_RIM"] / stats["FGA"]
    stats["3PAr"] = stats["FG3A"] / stats["FGA"]
    stats["FTr"] = stats["FTA"] / stats["FGA"]
    stats["OppRimFGAr"] = stats["FGA_RIM_OPP"] / stats["OPP_FGA"]
    stats["Opp3PAr"] = stats["OPP_FG3A"] / stats["OPP_FGA"]
    stats["OppFTr"] = stats["OPP_FTA"] / stats["OPP_FGA"]

    # Final columns and renaming
    final_columns = [
        "TEAM_NAME",
        "W_PCT",
        "NET_RATING",
        "PACE",
        "RimFGAr",
        "FG_PCT",
        "3PAr",
        "FG3_PCT",
        "FTr",
        "FT_PCT",
        "TM_TOV_PCT",
        "OREB_PCT",
        "DREB_PCT",
        "OppRimFGAr",
        "FG_PCT_OPP",
        "Opp3PAr",
        "OPP_FG3_PCT",
        "OppFTr",
        "OPP_FT_PCT",
        "OPP_TOV_PCT",
    ]

    stats = stats[final_columns]

    stats.rename(
        columns={
            "TEAM_NAME": "Team",
            "W_PCT": "Win%",
            "NET_RATING": "NetRtg",
            "PACE": "Pace",
            "FG_PCT": "RimFG%",
            "FG3_PCT": "3P%",
            "FT_PCT": "FT%",
            "TM_TOV_PCT": "Tov%",
            "OREB_PCT": "OReb%",
            "DREB_PCT": "DReb%",
            "FG_PCT_OPP": "OppRimFG%",
            "OPP_FG3_PCT": "Opp3P%",
            "OPP_FT_PCT": "OppFT%",
            "OPP_TOV_PCT": "OppTov%",
        },
        inplace=True,
    )

    return stats


def main():
    st.title("NBA Team Stats Dashboard")

    st.write("Fetching data, please wait...")
    stats = combine_stats()

    # Multiply columns by 100 except for 'Team'
    columns_to_multiply = stats.columns.difference(["Team"])
    stats[columns_to_multiply.difference(["NetRtg", "Pace"])] = (
        stats[columns_to_multiply.difference(["NetRtg", "Pace"])] * 100
    )

    columns_low_to_high = stats.columns.difference(
        [
            "Team",
            "Win%",
            "NetRtg",
            "Pace",
            "RimFGAr",
            "RimFG%",
            "3PAr",
            "3P%",
            "FTr",
            "FT%",
            "OReb%",
            "DReb%",
            "OppTov%",
        ]
    )
    columns_high_to_low = stats.columns.difference(
        [
            "Team",
            "OppRimFGAr",
            "OppRimFG%",
            "Opp3PAr",
            "Opp3P%",
            "OppFTr",
            "OppFT%",
            "Tov%",
        ]
    )

    # Round columns to one decimal place
    stats = stats.round(1)

    # Add a selectbox to choose between values and rankings
    view_option = st.selectbox("View as:", ["Values", "Rankings"])

    if view_option == "Rankings":
        # Compute rankings
        ranked_stats = stats.copy()
        for col in columns_to_multiply:
            ranked_stats[col] = stats[col].rank(
                ascending=True if col in columns_low_to_high else False
            )
        styled_stats = (
            ranked_stats.style.background_gradient(
                cmap="RdYlGn_r", subset=columns_low_to_high
            )
            .background_gradient(cmap="RdYlGn_r", subset=columns_high_to_low)
            .format("{:.1f}", subset=columns_to_multiply)
        )
    else:
        styled_stats = (
            stats.style.background_gradient(cmap="RdYlGn_r", subset=columns_low_to_high)
            .background_gradient(cmap="RdYlGn", subset=columns_high_to_low)
            .format("{:.1f}", subset=columns_to_multiply)
        )

    st.dataframe(styled_stats)


if __name__ == "__main__":
    main()
