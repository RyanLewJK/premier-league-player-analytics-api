from app.models import Player, PlayerMarketValue
from app.scoring import (
    normalize_text,
    safe_per90,
    get_availability_factor,
    calculate_raw_performance_score,
    build_position_score_stats,
    calculate_league_wide_performance_score,
    calculate_performance_score,
    calculate_value_score,
    calculate_breakout_score,
    find_market_value_for_player,
    build_market_value_lookup,
)


def make_player(
    player_name="Test Player",
    club_name="Test Club",
    position_name="MID",
    minutes=2000,
    goals_scored=5,
    assists=5,
    clean_sheets=5,
    goals_conceded=20,
    saves=0,
    defensive_contribution=20,
    yellow_cards=1,
    red_cards=0,
    bonus=10,
    total_points=100,
    points_per_game=5.0,
):
    return Player(
        player_name=player_name,
        club_name=club_name,
        position_name=position_name,
        minutes=minutes,
        total_points=total_points,
        points_per_game=points_per_game,
        goals_scored=goals_scored,
        assists=assists,
        clean_sheets=clean_sheets,
        goals_conceded=goals_conceded,
        saves=saves,
        defensive_contribution=defensive_contribution,
        yellow_cards=yellow_cards,
        red_cards=red_cards,
        bonus=bonus,
    )


def test_normalize_text():
    assert normalize_text(" Mohamed Salah ") == "mohamed salah"


def test_safe_per90_uses_minimum_300_minutes():
    result = safe_per90(10, 100)
    assert result == 3.0


def test_get_availability_factor_bands():
    assert get_availability_factor(200) == 0.55
    assert get_availability_factor(500) == 0.70
    assert get_availability_factor(1000) == 0.85
    assert get_availability_factor(1500) == 0.95
    assert get_availability_factor(2500) == 1.00


def test_raw_performance_score_forward_higher_than_poor_forward():
    strong = make_player(
        position_name="FWD",
        minutes=2200,
        goals_scored=18,
        assists=7,
        defensive_contribution=8,
        clean_sheets=2,
        yellow_cards=1,
        red_cards=0,
        bonus=18,
    )

    weak = make_player(
        position_name="FWD",
        minutes=2200,
        goals_scored=2,
        assists=1,
        defensive_contribution=2,
        clean_sheets=1,
        yellow_cards=4,
        red_cards=1,
        bonus=2,
    )

    assert calculate_raw_performance_score(strong) > calculate_raw_performance_score(weak)


def test_raw_performance_score_unknown_position_returns_zero():
    player = make_player(position_name="XYZ")
    assert calculate_raw_performance_score(player) == 0.0


def test_build_position_score_stats_groups_by_position():
    players = [
        make_player(player_name="Mid 1", position_name="MID", goals_scored=10),
        make_player(player_name="Mid 2", position_name="MID", goals_scored=4),
        make_player(player_name="Def 1", position_name="DEF", clean_sheets=15),
    ]

    stats = build_position_score_stats(players)

    assert "MID" in stats
    assert "DEF" in stats
    assert "mean" in stats["MID"]
    assert "std" in stats["MID"]


def test_calculate_league_wide_performance_score_returns_50_when_position_missing():
    player = make_player(position_name="GK")
    stats = {"MID": {"mean": 10.0, "std": 2.0}}

    assert calculate_league_wide_performance_score(player, stats) == 50.0


def test_calculate_league_wide_performance_score_clamped_between_0_and_100():
    strong = make_player(player_name="Strong Mid", position_name="MID", goals_scored=20, assists=15, bonus=20)
    average1 = make_player(player_name="Avg 1", position_name="MID", goals_scored=5, assists=5, bonus=5)
    average2 = make_player(player_name="Avg 2", position_name="MID", goals_scored=4, assists=4, bonus=4)

    stats = build_position_score_stats([strong, average1, average2])
    score = calculate_league_wide_performance_score(strong, stats)

    assert 0.0 <= score <= 100.0


def test_calculate_performance_score_matches_main_public_function():
    player = make_player(position_name="MID")
    stats = build_position_score_stats([player])

    assert calculate_performance_score(player, stats) == calculate_league_wide_performance_score(player, stats)


def test_calculate_value_score_returns_none_for_missing_or_zero_value():
    assert calculate_value_score(75.0, None) is None
    assert calculate_value_score(75.0, 0) is None


def test_calculate_value_score_computes_correctly():
    assert calculate_value_score(80.0, 20000000) == 4.0


def test_calculate_breakout_score_returns_none_if_market_value_exists():
    player = make_player()
    stats = build_position_score_stats([player])

    assert calculate_breakout_score(player, stats, has_market_value=True) is None


def test_calculate_breakout_score_returns_value_if_no_market_value():
    player = make_player(minutes=1500)
    stats = build_position_score_stats([player])

    score = calculate_breakout_score(player, stats, has_market_value=False)
    assert score is not None
    assert score >= 0


def test_build_market_value_lookup_and_find_market_value_for_player():
    player = make_player(player_name="Mohamed Salah")

    mv = PlayerMarketValue(
        player_name="Mohamed Salah",
        normalized_name="mohamed salah",
        club_name="Liverpool",
        normalized_club="liverpool",
        age=32,
        position="RW",
        position_group="MID",
        league_name="Premier League",
        current_value_gbp=55000000,
        peak_value_gbp=130000000,
        trajectory="falling",
    )

    lookup = build_market_value_lookup([mv])
    found = find_market_value_for_player(player, lookup)

    assert found is not None
    assert found.player_name == "Mohamed Salah"
    assert found.current_value_gbp == 55000000