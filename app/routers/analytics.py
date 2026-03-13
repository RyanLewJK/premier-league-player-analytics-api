from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import SessionLocal
from .. import models, schemas

router = APIRouter(prefix="/market-values", tags=["Market Values"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("", response_model=list[schemas.PlayerMarketValueResponse])
def get_market_values(db: Session = Depends(get_db)):
    return db.query(models.PlayerMarketValue).all()


@router.get("/{market_value_id}", response_model=schemas.PlayerMarketValueResponse)
def get_market_value(market_value_id: int, db: Session = Depends(get_db)):
    record = db.query(models.PlayerMarketValue).filter(
        models.PlayerMarketValue.id == market_value_id
    ).first()

    if not record:
        raise HTTPException(status_code=404, detail="Market value record not found")

    return record