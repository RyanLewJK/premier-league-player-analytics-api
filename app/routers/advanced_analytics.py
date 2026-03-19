from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ..database import SessionLocal
from .. import models
from ..scoring import (
    calculate_performance_score,
    calculate_value_score,
    calculate_breakout_score,
    find_market_value_for_player,
    build_market_value_lookup,
    build_position_score_stats,
    get_availability_factor,
)

router = APIRouter(
    prefix="/advanced-analytics",
    tags=["Advanced Analytics"]
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get(
    "/player/{player_id}/availability",
    summary="Get a player's availability factor",
    description="Returns the player's minutes played and the calculated availability factor used in the scoring model."
)
def get_player_availability(player_id: int, db: Session = Depends(get_db)):
    """
    Retrieve the availability factor for a specific player.
    """
    player = db.query(models.Player).filter(models.Player.id == player_id).first()

    if not player:
        raise HTTPException(status_code=404, detail="Player not found")

    availability = get_availability_factor(player.minutes)

    return {
        "player_id": player.id,
        "player_name": player.player_name,
        "minutes": player.minutes,
        "availability_factor": availability
    }


@router.get(
    "/compare",
    summary="Compare two players",
    description="Compares two players side by side using performance score, value score, and breakout score, then identifies the stronger performer based on performance score."
)
def compare_players(
    player1: str = Query(..., description="Name of the first player"),
    player2: str = Query(..., description="Name of the second player"),
    db: Session = Depends(get_db)
):
    """
    Compare two players using the API's analytics model.
    """
    all_players = db.query(models.Player).all()
    market_values = db.query(models.PlayerMarketValue).all()

    market_lookup = build_market_value_lookup(market_values)
    position_stats = build_position_score_stats(all_players)

    def find_player(name):
        return next(
            (p for p in all_players if p.player_name.lower() == name.lower()),
            None
        )

    p1 = find_player(player1)
    p2 = find_player(player2)

    if not p1 or not p2:
        raise HTTPException(status_code=404, detail="One or both players not found")

    def build(player):
        mv = find_market_value_for_player(player, market_lookup)

        perf = calculate_performance_score(player, position_stats)

        value = calculate_value_score(
            perf,
            mv.current_value_gbp if mv else None
        )

        breakout = calculate_breakout_score(
            player,
            position_stats,
            has_market_value=mv is not None
        )

        return {
            "player_name": player.player_name,
            "club": player.club_name,
            "position": player.position_name,
            "performance_score": perf,
            "value_score": value,
            "breakout_score": breakout
        }

    p1_data = build(p1)
    p2_data = build(p2)

    winner = None
    if p1_data["performance_score"] > p2_data["performance_score"]:
        winner = p1.player_name
    elif p2_data["performance_score"] > p1_data["performance_score"]:
        winner = p2.player_name

    return {
        "player_1": p1_data,
        "player_2": p2_data,
        "better_performer": winner
    }


@router.get(
    "/filter",
    summary="Filter players using advanced criteria",
    description="Filters players by optional criteria such as position, club, minimum minutes played, minimum performance score, and maximum market value."
)
def filter_players(
    position: str | None = Query(None, description="Filter by position, for example GK, DEF, MID, or FWD"),
    club: str | None = Query(None, description="Filter by club name"),
    min_minutes: int = Query(0, description="Minimum minutes played"),
    min_performance: float = Query(0, description="Minimum performance score"),
    max_value: float | None = Query(None, description="Maximum market value in GBP"),
    db: Session = Depends(get_db)
):
    """
    Retrieve players using flexible analytics filters.
    """
    all_players = db.query(models.Player).all()
    market_values = db.query(models.PlayerMarketValue).all()

    market_lookup = build_market_value_lookup(market_values)
    position_stats = build_position_score_stats(all_players)

    results = []

    for player in all_players:
        if player.minutes < min_minutes:
            continue

        if position and player.position_name.upper() != position.upper():
            continue

        if club and player.club_name.lower() != club.lower():
            continue

        mv = find_market_value_for_player(player, market_lookup)

        perf = calculate_performance_score(player, position_stats)

        if perf < min_performance:
            continue

        if max_value and mv and mv.current_value_gbp > max_value:
            continue

        results.append({
            "player_name": player.player_name,
            "club": player.club_name,
            "position": player.position_name,
            "performance_score": perf
        })

    results.sort(key=lambda x: x["performance_score"], reverse=True)

    return results


@router.get(
    "/scouting-targets",
    summary="Identify scouting targets",
    description="Returns players who meet scouting-style criteria, such as strong performance, sufficient minutes played, and relatively low market value."
)
def get_scouting_targets(
    min_minutes: int = Query(900, description="Minimum minutes played"),
    max_value: float = Query(20000000, description="Maximum market value in GBP"),
    min_performance: float = Query(65, description="Minimum performance score"),
    db: Session = Depends(get_db)
):
    """
    Identify potential scouting targets based on performance and affordability.
    """
    all_players = db.query(models.Player).all()
    market_values = db.query(models.PlayerMarketValue).all()

    market_lookup = build_market_value_lookup(market_values)
    position_stats = build_position_score_stats(all_players)

    results = []

    for player in all_players:
        if player.minutes < min_minutes:
            continue

        mv = find_market_value_for_player(player, market_lookup)
        if not mv:
            continue

        perf = calculate_performance_score(player, position_stats)

        if perf >= min_performance and mv.current_value_gbp <= max_value:
            results.append({
                "player_name": player.player_name,
                "club": player.club_name,
                "performance_score": perf,
                "market_value": mv.current_value_gbp
            })

    results.sort(key=lambda x: x["performance_score"], reverse=True)

    return results

@router.get(
    "/reliable-value-players",
    summary="Identify reliable value players",
    description="Returns players who combine strong performance, high availability, and relatively low market value. This endpoint is intended to highlight cost-effective and dependable players for scouting and recruitment analysis."
)
def get_reliable_value_players(
    min_minutes: int = Query(1200, description="Minimum minutes played"),
    min_availability: float = Query(0.85, description="Minimum availability factor required"),
    min_performance: float = Query(60.0, description="Minimum performance score required"),
    max_market_value: float = Query(30000000, description="Maximum market value in GBP"),
    limit: int = Query(10, description="Maximum number of players to return"),
    db: Session = Depends(get_db)
):
    """
    Identify players who are consistently available, performing well,
    and still relatively affordable in the market.
    """
    all_players = db.query(models.Player).all()
    market_values = db.query(models.PlayerMarketValue).all()

    market_lookup = build_market_value_lookup(market_values)
    position_stats = build_position_score_stats(all_players)

    results = []

    for player in all_players:
        if player.minutes < min_minutes:
            continue

        availability = get_availability_factor(player.minutes)
        if availability < min_availability:
            continue

        performance_score = calculate_performance_score(player, position_stats)
        if performance_score < min_performance:
            continue

        matched_market_value = find_market_value_for_player(player, market_lookup)
        if not matched_market_value:
            continue

        market_value_gbp = matched_market_value.current_value_gbp
        if market_value_gbp > max_market_value:
            continue

        value_score = calculate_value_score(performance_score, market_value_gbp)

        results.append({
            "player_id": player.id,
            "player_name": player.player_name,
            "club_name": player.club_name,
            "position_name": player.position_name,
            "minutes": player.minutes,
            "availability_factor": availability,
            "performance_score": performance_score,
            "market_value_gbp": market_value_gbp,
            "value_score": value_score,
        })

    results.sort(
        key=lambda x: (
            x["value_score"],
            x["performance_score"],
            x["availability_factor"]
        ),
        reverse=True
    )

    return results[:limit]


@router.get(
    "/overvalued-players",
    summary="Identify potentially overvalued players",
    description="Returns players with high market value but relatively low performance and/or availability according to the API's scoring model. This endpoint is designed to highlight players who may represent inefficient value."
)
def get_overvalued_players(
    min_market_value: float = Query(40000000, description="Minimum market value in GBP"),
    max_performance: float = Query(55.0, description="Maximum performance score allowed"),
    max_availability: float = Query(0.95, description="Maximum availability factor allowed"),
    limit: int = Query(10, description="Maximum number of players to return"),
    db: Session = Depends(get_db)
):
    """
    Identify players who may be overvalued based on high market value
    combined with weaker performance and/or reduced availability.
    """
    all_players = db.query(models.Player).all()
    market_values = db.query(models.PlayerMarketValue).all()

    market_lookup = build_market_value_lookup(market_values)
    position_stats = build_position_score_stats(all_players)

    results = []

    for player in all_players:
        matched_market_value = find_market_value_for_player(player, market_lookup)
        if not matched_market_value:
            continue

        market_value_gbp = matched_market_value.current_value_gbp
        if market_value_gbp < min_market_value:
            continue

        availability = get_availability_factor(player.minutes)
        performance_score = calculate_performance_score(player, position_stats)

        if performance_score > max_performance:
            continue

        if availability > max_availability:
            continue

        value_score = calculate_value_score(performance_score, market_value_gbp)

        results.append({
            "player_id": player.id,
            "player_name": player.player_name,
            "club_name": player.club_name,
            "position_name": player.position_name,
            "minutes": player.minutes,
            "availability_factor": availability,
            "performance_score": performance_score,
            "market_value_gbp": market_value_gbp,
            "value_score": value_score,
        })

    results.sort(
        key=lambda x: (
            x["market_value_gbp"],
            -x["performance_score"],
            -x["availability_factor"]
        ),
        reverse=True
    )

    return results[:limit]