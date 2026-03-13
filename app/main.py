from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session

from .database import SessionLocal, engine, Base
from . import models, schemas
from .scoring import (
    calculate_performance_score,
    calculate_value_score,
    calculate_breakout_score,
    find_market_value_for_player
)

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Premier League Player Analytics API")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/")
def root():
    return {"message": "Premier League Player Analytics API is running"}


# -------------------------
# PLAYER CRUD
# -------------------------

@app.post("/players", response_model=schemas.PlayerResponse, status_code=201)
def create_player(player: schemas.PlayerCreate, db: Session = Depends(get_db)):
    db_player = models.Player(**player.model_dump())
    db.add(db_player)
    db.commit()
    db.refresh(db_player)
    return db_player


@app.get("/players", response_model=list[schemas.PlayerResponse])
def get_players(db: Session = Depends(get_db)):
    return db.query(models.Player).all()


@app.get("/players/{player_id}", response_model=schemas.PlayerResponse)
def get_player(player_id: int, db: Session = Depends(get_db)):
    player = db.query(models.Player).filter(models.Player.id == player_id).first()

    if not player:
        raise HTTPException(status_code=404, detail="Player not found")

    return player


@app.put("/players/{player_id}", response_model=schemas.PlayerResponse)
def update_player(
    player_id: int,
    updated_player: schemas.PlayerCreate,
    db: Session = Depends(get_db)
):
    player = db.query(models.Player).filter(models.Player.id == player_id).first()

    if not player:
        raise HTTPException(status_code=404, detail="Player not found")

    for key, value in updated_player.model_dump().items():
        setattr(player, key, value)

    db.commit()
    db.refresh(player)
    return player


@app.delete("/players/{player_id}")
def delete_player(player_id: int, db: Session = Depends(get_db)):
    player = db.query(models.Player).filter(models.Player.id == player_id).first()

    if not player:
        raise HTTPException(status_code=404, detail="Player not found")

    db.delete(player)
    db.commit()
    return {"message": "Player deleted successfully"}


# -------------------------
# MARKET VALUE READ ENDPOINTS
# -------------------------

@app.get("/market-values", response_model=list[schemas.PlayerMarketValueResponse])
def get_market_values(db: Session = Depends(get_db)):
    return db.query(models.PlayerMarketValue).all()


@app.get("/market-values/{market_value_id}", response_model=schemas.PlayerMarketValueResponse)
def get_market_value(market_value_id: int, db: Session = Depends(get_db)):
    record = (
        db.query(models.PlayerMarketValue)
        .filter(models.PlayerMarketValue.id == market_value_id)
        .first()
    )

    if not record:
        raise HTTPException(status_code=404, detail="Market value record not found")

    return record


# -------------------------
# FILTERED PLAYER ENDPOINTS
# -------------------------

@app.get("/players/position/{position}", response_model=list[schemas.PlayerResponse])
def get_players_by_position(position: str, db: Session = Depends(get_db)):
    players = (
        db.query(models.Player)
        .filter(models.Player.position_name.ilike(position))
        .all()
    )
    return players


@app.get("/players/club/{club}", response_model=list[schemas.PlayerResponse])
def get_players_by_club(club: str, db: Session = Depends(get_db)):
    players = (
        db.query(models.Player)
        .filter(models.Player.club_name.ilike(club))
        .all()
    )
    return players


# -------------------------
# ANALYTICS HELPERS
# -------------------------

def build_player_score(player: models.Player, market_values: list[models.PlayerMarketValue]):
    matched_market_value = find_market_value_for_player(player, market_values)

    performance_score = calculate_performance_score(player)
    market_value_gbp = matched_market_value.current_value_gbp if matched_market_value else None
    value_score = calculate_value_score(performance_score, market_value_gbp)
    breakout_score = calculate_breakout_score(player, matched_market_value is not None)

    return {
        "player_id": player.id,
        "player_name": player.player_name,
        "club_name": player.club_name,
        "position_name": player.position_name,
        "minutes": player.minutes,
        "performance_score": performance_score,
        "market_value_gbp": market_value_gbp,
        "value_score": value_score,
        "breakout_score": breakout_score,
    }


# -------------------------
# ANALYTICS ENDPOINTS
# -------------------------

@app.get("/analytics/player-score/{player_id}", response_model=schemas.PlayerScoreResponse)
def get_player_score(player_id: int, db: Session = Depends(get_db)):
    player = db.query(models.Player).filter(models.Player.id == player_id).first()

    if not player:
        raise HTTPException(status_code=404, detail="Player not found")

    market_values = db.query(models.PlayerMarketValue).all()
    return build_player_score(player, market_values)


@app.get("/analytics/top-performers", response_model=list[schemas.PlayerScoreResponse])
def get_top_performers(limit: int = 10, db: Session = Depends(get_db)):
    players = db.query(models.Player).all()
    market_values = db.query(models.PlayerMarketValue).all()

    scored_players = [build_player_score(player, market_values) for player in players]
    scored_players.sort(key=lambda x: x["performance_score"], reverse=True)

    return scored_players[:limit]


@app.get("/analytics/best-value-players", response_model=list[schemas.PlayerScoreResponse])
def get_best_value_players(limit: int = 10, db: Session = Depends(get_db)):
    players = db.query(models.Player).all()
    market_values = db.query(models.PlayerMarketValue).all()

    scored_players = [build_player_score(player, market_values) for player in players]
    scored_players = [p for p in scored_players if p["value_score"] is not None]
    scored_players.sort(key=lambda x: x["value_score"], reverse=True)

    return scored_players[:limit]


@app.get("/analytics/breakout-players", response_model=list[schemas.PlayerScoreResponse])
def get_breakout_players(limit: int = 10, db: Session = Depends(get_db)):
    players = db.query(models.Player).all()
    market_values = db.query(models.PlayerMarketValue).all()

    scored_players = [build_player_score(player, market_values) for player in players]
    scored_players = [p for p in scored_players if p["breakout_score"] is not None]
    scored_players.sort(key=lambda x: x["breakout_score"], reverse=True)

    return scored_players[:limit]