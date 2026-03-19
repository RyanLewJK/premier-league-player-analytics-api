from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ..database import SessionLocal
from .. import models, schemas
from ..scoring import (
    calculate_performance_score,
    calculate_value_score,
    calculate_breakout_score,
    find_market_value_for_player,
    build_market_value_lookup,
    build_position_score_stats,
)

router = APIRouter(
    prefix="/analytics",
    tags=["Analytics"]
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def build_player_score(
    player: models.Player,
    market_lookup: dict,
    position_stats: dict
) -> schemas.PlayerScoreResponse:
    """
    Build a complete analytics profile for a player.
    """
    performance_score = calculate_performance_score(player, position_stats)
    matched_market_value = find_market_value_for_player(player, market_lookup)

    market_value_gbp = None
    value_score = None
    breakout_score = None

    if matched_market_value:
        market_value_gbp = matched_market_value.current_value_gbp
        value_score = calculate_value_score(performance_score, market_value_gbp)
    else:
        breakout_score = calculate_breakout_score(
            player,
            position_stats,
            has_market_value=False
        )

    return schemas.PlayerScoreResponse(
        player_id=player.id,
        player_name=player.player_name,
        club_name=player.club_name,
        position_name=player.position_name,
        minutes=player.minutes,
        performance_score=performance_score,
        market_value_gbp=market_value_gbp,
        value_score=value_score,
        breakout_score=breakout_score,
    )


def normalize_position(position: str) -> str:
    position = position.upper()
    valid_positions = {"GK", "DEF", "MID", "FWD"}

    if position not in valid_positions:
        raise HTTPException(
            status_code=400,
            detail="Invalid position. Use one of: GK, DEF, MID, FWD"
        )

    return position


@router.get(
    "/player-scores",
    response_model=list[schemas.PlayerScoreResponse],
    summary="Get all player scores",
    description="Returns performance, value, and breakout scores for all players in the league."
)
def get_player_scores(db: Session = Depends(get_db)):
    """
    Retrieve full analytics for all players.
    """
    players = db.query(models.Player).all()
    market_values = db.query(models.PlayerMarketValue).all()

    market_lookup = build_market_value_lookup(market_values)
    position_stats = build_position_score_stats(players)

    return [
        build_player_score(player, market_lookup, position_stats)
        for player in players
    ]


@router.get(
    "/top-performers",
    response_model=list[schemas.PlayerScoreResponse],
    summary="Get top-performing players",
    description="Returns the highest-performing players in the league based on performance score."
)
def get_top_performers(
    limit: int = Query(10, description="Number of players to return"),
    db: Session = Depends(get_db)
):
    """
    Retrieve top-performing players in the league.
    """
    players = db.query(models.Player).all()
    market_values = db.query(models.PlayerMarketValue).all()

    market_lookup = build_market_value_lookup(market_values)
    position_stats = build_position_score_stats(players)

    results = [
        build_player_score(player, market_lookup, position_stats)
        for player in players
    ]

    results.sort(key=lambda x: x.performance_score, reverse=True)
    return results[:limit]


@router.get(
    "/best-value",
    response_model=list[schemas.PlayerScoreResponse],
    summary="Get best value players",
    description="Returns players who deliver the highest performance relative to their market value."
)
def get_best_value(
    limit: int = Query(10, description="Number of players to return"),
    db: Session = Depends(get_db)
):
    """
    Identify the most cost-effective players.
    """
    players = db.query(models.Player).all()
    market_values = db.query(models.PlayerMarketValue).all()

    market_lookup = build_market_value_lookup(market_values)
    position_stats = build_position_score_stats(players)

    results = [
        build_player_score(player, market_lookup, position_stats)
        for player in players
    ]

    results = [r for r in results if r.value_score is not None]
    results.sort(key=lambda x: x.value_score, reverse=True)

    return results[:limit]


@router.get(
    "/breakout-players",
    response_model=list[schemas.PlayerScoreResponse],
    summary="Get breakout players",
    description="Returns players without market values who show strong performance, indicating potential emerging talent."
)
def get_breakout_players(
    limit: int = Query(10, description="Number of players to return"),
    db: Session = Depends(get_db)
):
    """
    Identify emerging or undervalued players.
    """
    players = db.query(models.Player).all()
    market_values = db.query(models.PlayerMarketValue).all()

    market_lookup = build_market_value_lookup(market_values)
    position_stats = build_position_score_stats(players)

    results = [
        build_player_score(player, market_lookup, position_stats)
        for player in players
    ]

    results = [r for r in results if r.breakout_score is not None]
    results.sort(key=lambda x: x.breakout_score, reverse=True)

    return results[:limit]


@router.get(
    "/best-value/{position}",
    response_model=list[schemas.PlayerScoreResponse],
    summary="Get best value players by position",
    description="Returns the most cost-effective players within a specific position (GK, DEF, MID, FWD)."
)
def get_best_value_by_position(
    position: str,
    limit: int = Query(10, description="Number of players to return"),
    db: Session = Depends(get_db)
):
    """
    Identify best-value players within a specific position.
    """
    position = normalize_position(position)

    all_players = db.query(models.Player).all()
    market_values = db.query(models.PlayerMarketValue).all()

    market_lookup = build_market_value_lookup(market_values)
    position_stats = build_position_score_stats(all_players)

    filtered_players = [
        p for p in all_players if p.position_name.upper() == position
    ]

    results = [
        build_player_score(player, market_lookup, position_stats)
        for player in filtered_players
    ]

    results = [r for r in results if r.value_score is not None]
    results.sort(key=lambda x: x.value_score, reverse=True)

    return results[:limit]


@router.get(
    "/top-performers/{position}",
    response_model=list[schemas.PlayerScoreResponse],
    summary="Get top performers by position",
    description="Returns the highest-performing players within a specific position, with optional minimum minutes filtering."
)
def get_top_performers_by_position(
    position: str,
    limit: int = Query(10, description="Number of players to return"),
    min_minutes: int = Query(0, description="Minimum minutes played"),
    db: Session = Depends(get_db)
):
    """
    Retrieve top-performing players within a specific position.
    """
    position = normalize_position(position)

    all_players = db.query(models.Player).all()
    market_values = db.query(models.PlayerMarketValue).all()

    market_lookup = build_market_value_lookup(market_values)
    position_stats = build_position_score_stats(all_players)

    filtered_players = [
        p for p in all_players
        if p.position_name.upper() == position and p.minutes >= min_minutes
    ]

    results = [
        build_player_score(player, market_lookup, position_stats)
        for player in filtered_players
    ]

    results.sort(key=lambda x: x.performance_score, reverse=True)

    return results[:limit]