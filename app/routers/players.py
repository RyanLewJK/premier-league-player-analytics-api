from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import SessionLocal
from .. import models, schemas

router = APIRouter(prefix="/players", tags=["Players"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("", response_model=schemas.PlayerResponse, status_code=201)
def create_player(player: schemas.PlayerCreate, db: Session = Depends(get_db)):
    db_player = models.Player(**player.model_dump())
    db.add(db_player)
    db.commit()
    db.refresh(db_player)
    return db_player


@router.get("", response_model=list[schemas.PlayerResponse])
def get_players(db: Session = Depends(get_db)):
    return db.query(models.Player).all()


@router.get("/{player_id}", response_model=schemas.PlayerResponse)
def get_player(player_id: int, db: Session = Depends(get_db)):
    player = db.query(models.Player).filter(models.Player.id == player_id).first()
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")
    return player


@router.put("/{player_id}", response_model=schemas.PlayerResponse)
def update_player(player_id: int, updated_player: schemas.PlayerCreate, db: Session = Depends(get_db)):
    player = db.query(models.Player).filter(models.Player.id == player_id).first()
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")

    for key, value in updated_player.model_dump().items():
        setattr(player, key, value)

    db.commit()
    db.refresh(player)
    return player


@router.delete("/{player_id}")
def delete_player(player_id: int, db: Session = Depends(get_db)):
    player = db.query(models.Player).filter(models.Player.id == player_id).first()
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")

    db.delete(player)
    db.commit()
    return {"message": "Player deleted successfully"}


@router.get("/position/{position}", response_model=list[schemas.PlayerResponse])
def get_players_by_position(position: str, db: Session = Depends(get_db)):
    return db.query(models.Player).filter(models.Player.position_name.ilike(position)).all()


@router.get("/club/{club}", response_model=list[schemas.PlayerResponse])
def get_players_by_club(club: str, db: Session = Depends(get_db)):
    return db.query(models.Player).filter(models.Player.club_name.ilike(club)).all()

@router.patch("/{player_id}", response_model=schemas.PlayerResponse)
def patch_player(player_id: int, updated_fields: schemas.PlayerUpdate, db: Session = Depends(get_db)):
    player = db.query(models.Player).filter(models.Player.id == player_id).first()
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")

    update_data = updated_fields.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(player, key, value)

    db.commit()
    db.refresh(player)
    return player