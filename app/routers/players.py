from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func

from ..database import SessionLocal
from .. import models, schemas
from ..security import verify_api_key

router = APIRouter(
    prefix="/players",
    tags=["Players"]
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post(
    "",
    response_model=schemas.PlayerResponse,
    status_code=201,
    summary="Create a new player",
    description="Creates a new player record in the database using the supplied player statistics and profile information."
)
def create_player(player: schemas.PlayerCreate, db: Session = Depends(get_db)):
    """
    Add a new player to the database.
    """
    db_player = models.Player(**player.model_dump())
    db.add(db_player)
    db.commit()
    db.refresh(db_player)
    return db_player


@router.get(
    "",
    response_model=list[schemas.PlayerResponse],
    summary="Get all players",
    description="Returns a list of all players stored in the database."
)
def get_players(db: Session = Depends(get_db)):
    """
    Retrieve all player records.
    """
    return db.query(models.Player).all()


@router.get(
    "/search",
    response_model=list[schemas.PlayerResponse],
    summary="Search players by name",
    description="Searches for players using a partial, case-insensitive match on the player name."
)
def search_players(
    name: str = Query(
        ...,
        min_length=1,
        description="Player name or partial name to search for"
    ),
    db: Session = Depends(get_db)
):
    """
    Search for players by name.
    """
    players = (
        db.query(models.Player)
        .filter(func.lower(models.Player.player_name).contains(name.lower()))
        .all()
    )
    return players


@router.get(
    "/position/{position}",
    response_model=list[schemas.PlayerResponse],
    summary="Get players by position",
    description="Returns all players whose position matches the supplied position value, such as GK, DEF, MID, or FWD."
)
def get_players_by_position(position: str, db: Session = Depends(get_db)):
    """
    Retrieve players filtered by playing position.
    """
    return db.query(models.Player).filter(models.Player.position_name.ilike(position)).all()


@router.get(
    "/club/{club}",
    response_model=list[schemas.PlayerResponse],
    summary="Get players by club",
    description="Returns all players belonging to the specified club."
)
def get_players_by_club(club: str, db: Session = Depends(get_db)):
    """
    Retrieve players filtered by club name.
    """
    return db.query(models.Player).filter(models.Player.club_name.ilike(club)).all()


@router.get(
    "/{player_id}",
    response_model=schemas.PlayerResponse,
    summary="Get a player by ID",
    description="Returns a single player record using its unique database ID."
)
def get_player(player_id: int, db: Session = Depends(get_db)):
    """
    Retrieve one player by ID.
    """
    player = db.query(models.Player).filter(models.Player.id == player_id).first()
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")
    return player


@router.put(
    "/{player_id}",
    response_model=schemas.PlayerResponse,
    dependencies=[Depends(verify_api_key)],
    summary="Replace a player record",
    description="Fully updates an existing player record. All fields must be supplied, as PUT replaces the full resource."
)
def update_player(player_id: int, updated_player: schemas.PlayerCreate, db: Session = Depends(get_db)):
    """
    Fully replace an existing player record.
    """
    player = db.query(models.Player).filter(models.Player.id == player_id).first()
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")

    for key, value in updated_player.model_dump().items():
        setattr(player, key, value)

    db.commit()
    db.refresh(player)
    return player


@router.patch(
    "/{player_id}",
    response_model=schemas.PlayerResponse,
    dependencies=[Depends(verify_api_key)],
    summary="Partially update a player record",
    description="Updates only the supplied fields of an existing player record, leaving all other fields unchanged."
)
def patch_player(player_id: int, updated_fields: schemas.PlayerUpdate, db: Session = Depends(get_db)):
    """
    Partially update an existing player record.
    """
    player = db.query(models.Player).filter(models.Player.id == player_id).first()
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")

    update_data = updated_fields.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(player, key, value)

    db.commit()
    db.refresh(player)
    return player


@router.delete(
    "/{player_id}",
    summary="Delete a player",
    dependencies=[Depends(verify_api_key)],
    description="Deletes an existing player record from the database using its unique ID."
)
def delete_player(player_id: int, db: Session = Depends(get_db)):
    """
    Delete a player by ID.
    """
    player = db.query(models.Player).filter(models.Player.id == player_id).first()
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")

    db.delete(player)
    db.commit()
    return {"message": "Player deleted successfully"}