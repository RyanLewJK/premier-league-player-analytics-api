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


def calculate_performance_score(player: Player) -> float:
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
            goals_p90 * 10.0 +
            assists_p90 * 6.0 +
            defcon_p90 * 1.5 +
            clean_sheets_p90 * 0.5 +
            bonus_p90 * 2.0 -
            yellow_cards_p90 * 1.0 -
            red_cards_p90 * 4.0
        )

    elif position == "MID":
        raw_score = (
            goals_p90 * 6.0 +
            assists_p90 * 7.0 +
            defcon_p90 * 3.5 +
            clean_sheets_p90 * 2.0 +
            bonus_p90 * 2.0 -
            yellow_cards_p90 * 1.0 -
            red_cards_p90 * 4.0
        )

    elif position == "DEF":
        raw_score = (
            goals_p90 * 4.0 +
            assists_p90 * 5.0 +
            defcon_p90 * 7.0 +
            clean_sheets_p90 * 6.0 +
            bonus_p90 * 2.0 -
            goals_conceded_p90 * 1.5 -
            yellow_cards_p90 * 1.0 -
            red_cards_p90 * 4.0
        )

    elif position == "GK":
        raw_score = (
            saves_p90 * 3.0 +
            defcon_p90 * 4.0 +
            clean_sheets_p90 * 6.5 +
            bonus_p90 * 2.0 -
            goals_conceded_p90 * 1.5 -
            yellow_cards_p90 * 1.0 -
            red_cards_p90 * 4.0
        )

    else:
        raw_score = 0.0

    return round(raw_score * availability, 2)


def calculate_value_score(performance_score: float, market_value_gbp: Optional[float]) -> Optional[float]:
    if market_value_gbp is None or market_value_gbp <= 0:
        return None
    return round((performance_score * 1_000_000) / market_value_gbp, 4)


def calculate_breakout_score(player: Player, has_market_value: bool) -> Optional[float]:
    if has_market_value:
        return None

    performance_score = calculate_performance_score(player)
    availability = get_availability_factor(player.minutes)

    breakout_score = performance_score * (0.8 + availability)
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