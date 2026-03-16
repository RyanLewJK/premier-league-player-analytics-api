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


@router.post("", response_model=schemas.PlayerMarketValueResponse, status_code=201)
def create_market_value(
    market_value: schemas.PlayerMarketValueCreate,
    db: Session = Depends(get_db)
):
    db_record = models.PlayerMarketValue(**market_value.model_dump())
    db.add(db_record)
    db.commit()
    db.refresh(db_record)
    return db_record


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


@router.put("/{market_value_id}", response_model=schemas.PlayerMarketValueResponse)
def update_market_value(
    market_value_id: int,
    updated_record: schemas.PlayerMarketValueCreate,
    db: Session = Depends(get_db)
):
    record = db.query(models.PlayerMarketValue).filter(
        models.PlayerMarketValue.id == market_value_id
    ).first()

    if not record:
        raise HTTPException(status_code=404, detail="Market value record not found")

    for key, value in updated_record.model_dump().items():
        setattr(record, key, value)

    db.commit()
    db.refresh(record)
    return record


@router.patch("/{market_value_id}", response_model=schemas.PlayerMarketValueResponse)
def patch_market_value(
    market_value_id: int,
    updated_fields: schemas.PlayerMarketValueUpdate,
    db: Session = Depends(get_db)
):
    record = db.query(models.PlayerMarketValue).filter(
        models.PlayerMarketValue.id == market_value_id
    ).first()

    if not record:
        raise HTTPException(status_code=404, detail="Market value record not found")

    update_data = updated_fields.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(record, key, value)

    db.commit()
    db.refresh(record)
    return record


@router.delete("/{market_value_id}")
def delete_market_value(market_value_id: int, db: Session = Depends(get_db)):
    record = db.query(models.PlayerMarketValue).filter(
        models.PlayerMarketValue.id == market_value_id
    ).first()

    if not record:
        raise HTTPException(status_code=404, detail="Market value record not found")

    db.delete(record)
    db.commit()
    return {"message": "Market value record deleted successfully"}