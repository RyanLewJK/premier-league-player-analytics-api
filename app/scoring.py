from collections import defaultdict
from statistics import mean, pstdev
from typing import Optional

from .models import Player, PlayerMarketValue


def normalize_text(value: str) -> str:
    return str(value).strip().lower()


def safe_per90(stat: float, minutes: int) -> float:
    adjusted_minutes = max(minutes, 300)
    return stat / (adjusted_minutes / 90)


def get_availability_factor(minutes: int) -> float:
    if minutes < 300:
        return 0.55
    if minutes < 600:
        return 0.70
    if minutes < 1200:
        return 0.85
    if minutes < 2000:
        return 0.95
    return 1.00


def calculate_raw_performance_score(player: Player) -> float:
    minutes = player.minutes
    availability = get_availability_factor(minutes)

    goals_p90 = safe_per90(player.goals_scored, minutes)
    assists_p90 = safe_per90(player.assists, minutes)
    defcon_p90 = safe_per90(player.defensive_contribution, minutes)
    clean_sheets_p90 = safe_per90(player.clean_sheets, minutes)
    goals_conceded_p90 = safe_per90(player.goals_conceded, minutes)
    saves_p90 = safe_per90(player.saves, minutes)
    bonus_p90 = safe_per90(player.bonus, minutes)
    yellow_cards_p90 = safe_per90(player.yellow_cards, minutes)
    red_cards_p90 = safe_per90(player.red_cards, minutes)

    position = player.position_name.upper()

    if position == "FWD":
        raw_score = (
            goals_p90 * 9.0 +
            assists_p90 * 5.5 +
            defcon_p90 * 1.0 +
            clean_sheets_p90 * 0.3 +
            bonus_p90 * 1.5 -
            yellow_cards_p90 * 1.0 -
            red_cards_p90 * 4.0
        )

    elif position == "MID":
        raw_score = (
            goals_p90 * 6.0 +
            assists_p90 * 6.5 +
            defcon_p90 * 2.8 +
            clean_sheets_p90 * 1.5 +
            bonus_p90 * 1.5 -
            yellow_cards_p90 * 1.0 -
            red_cards_p90 * 4.0
        )

    elif position == "DEF":
        raw_score = (
            goals_p90 * 3.5 +
            assists_p90 * 4.5 +
            defcon_p90 * 5.0 +
            clean_sheets_p90 * 4.0 +
            bonus_p90 * 1.5 -
            goals_conceded_p90 * 2.0 -
            yellow_cards_p90 * 1.0 -
            red_cards_p90 * 4.0
        )

    elif position == "GK":
        raw_score = (
            saves_p90 * 2.0 +
            defcon_p90 * 2.0 +
            clean_sheets_p90 * 5.0 +
            bonus_p90 * 1.5 -
            goals_conceded_p90 * 2.5 -
            yellow_cards_p90 * 1.0 -
            red_cards_p90 * 4.0
        )

    else:
        raw_score = 0.0

    return round(raw_score * availability, 4)


def build_position_score_stats(players: list[Player]) -> dict[str, dict[str, float]]:
    grouped_scores = defaultdict(list)

    for player in players:
        position = player.position_name.upper()
        raw_score = calculate_raw_performance_score(player)
        grouped_scores[position].append(raw_score)

    stats = {}

    for position, scores in grouped_scores.items():
        avg = mean(scores)
        std = pstdev(scores) if len(scores) > 1 else 0.0

        stats[position] = {
            "mean": avg,
            "std": std
        }

    return stats


def calculate_league_wide_performance_score(
    player: Player,
    position_stats: dict[str, dict[str, float]]
) -> float:
    raw_score = calculate_raw_performance_score(player)
    position = player.position_name.upper()

    if position not in position_stats:
        return 50.0

    avg = position_stats[position]["mean"]
    std = position_stats[position]["std"]

    if std == 0:
        z_score = 0.0
    else:
        z_score = (raw_score - avg) / std

    # Put all positions onto one shared scale
    league_score = 50 + (15 * z_score)

    # Clamp to keep results readable
    league_score = max(0.0, min(100.0, league_score))

    return round(league_score, 2)


def calculate_performance_score(
    player: Player,
    position_stats: dict[str, dict[str, float]]
) -> float:
    """
    Main public performance score for league-wide comparison.
    """
    return calculate_league_wide_performance_score(player, position_stats)


def calculate_value_score(
    league_performance_score: float,
    market_value_gbp: Optional[float]
) -> Optional[float]:
    if market_value_gbp is None or market_value_gbp <= 0:
        return None

    market_value_millions = market_value_gbp / 1_000_000
    return round(league_performance_score / market_value_millions, 4)


def calculate_breakout_score(
    player: Player,
    position_stats: dict[str, dict[str, float]],
    has_market_value: bool
) -> Optional[float]:
    if has_market_value:
        return None

    league_score = calculate_league_wide_performance_score(player, position_stats)
    availability = get_availability_factor(player.minutes)

    breakout_score = league_score * (0.8 + availability)
    return round(breakout_score, 2)


def find_market_value_for_player(
    player: Player,
    market_lookup: dict
) -> Optional[PlayerMarketValue]:
    player_name = normalize_text(player.player_name)
    return market_lookup.get(player_name)


def build_market_value_lookup(market_values: list[PlayerMarketValue]) -> dict:
    lookup = {}

    for mv in market_values:
        if mv.normalized_name:
            lookup[mv.normalized_name] = mv

    return lookup