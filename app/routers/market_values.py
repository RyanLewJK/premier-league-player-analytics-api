from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import SessionLocal
from .. import models, schemas
from ..security import verify_api_key

router = APIRouter(
    prefix="/market-values",
    tags=["Market Values"]
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def normalize_text(text: str) -> str:
    """
    Normalize text for consistent matching and lookup.
    """
    return text.strip().lower()


@router.post(
    "",
    response_model=schemas.PlayerMarketValueResponse,
    status_code=201,
    dependencies=[Depends(verify_api_key)],
    summary="Create a market value record",
    description="Creates a new market value entry for a player, including current value, peak value, and optional metadata such as position and trajectory."
)
def create_market_value(
    market_value: schemas.PlayerMarketValueCreate,
    db: Session = Depends(get_db)
):
    """
    Add a new player market value record to the database.
    """
    data = market_value.model_dump()
    data["normalized_name"] = normalize_text(data["player_name"])
    data["normalized_club"] = normalize_text(data["club_name"])

    db_record = models.PlayerMarketValue(**data)
    db.add(db_record)
    db.commit()
    db.refresh(db_record)
    return db_record


@router.get(
    "",
    response_model=list[schemas.PlayerMarketValueResponse],
    summary="Get all market values",
    description="Returns all stored player market value records."
)
def get_market_values(db: Session = Depends(get_db)):
    """
    Retrieve all market value records.
    """
    return db.query(models.PlayerMarketValue).all()


@router.get(
    "/{market_value_id}",
    response_model=schemas.PlayerMarketValueResponse,
    summary="Get market value by ID",
    description="Returns a specific market value record using its unique ID."
)
def get_market_value(market_value_id: int, db: Session = Depends(get_db)):
    """
    Retrieve a single market value record by ID.
    """
    record = db.query(models.PlayerMarketValue).filter(
        models.PlayerMarketValue.id == market_value_id
    ).first()

    if not record:
        raise HTTPException(status_code=404, detail="Market value record not found")

    return record


@router.put(
    "/{market_value_id}",
    response_model=schemas.PlayerMarketValueResponse,
    summary="Replace a market value record",
    dependencies=[Depends(verify_api_key)],
    description="Fully updates an existing market value record. All fields must be provided, as PUT replaces the entire resource."
)
def update_market_value(
    market_value_id: int,
    updated_record: schemas.PlayerMarketValueCreate,
    db: Session = Depends(get_db)
):
    """
    Fully replace an existing market value record.
    """
    record = db.query(models.PlayerMarketValue).filter(
        models.PlayerMarketValue.id == market_value_id
    ).first()

    if not record:
        raise HTTPException(status_code=404, detail="Market value record not found")

    update_data = updated_record.model_dump()
    update_data["normalized_name"] = normalize_text(update_data["player_name"])
    update_data["normalized_club"] = normalize_text(update_data["club_name"])

    for key, value in update_data.items():
        setattr(record, key, value)

    db.commit()
    db.refresh(record)
    return record


@router.patch(
    "/{market_value_id}",
    response_model=schemas.PlayerMarketValueResponse,
    summary="Partially update a market value record",
    dependencies=[Depends(verify_api_key)],
    description="Updates only the supplied fields of a market value record, leaving all other fields unchanged."
)
def patch_market_value(
    market_value_id: int,
    updated_fields: schemas.PlayerMarketValueUpdate,
    db: Session = Depends(get_db)
):
    """
    Partially update an existing market value record.
    """
    record = db.query(models.PlayerMarketValue).filter(
        models.PlayerMarketValue.id == market_value_id
    ).first()

    if not record:
        raise HTTPException(status_code=404, detail="Market value record not found")

    update_data = updated_fields.model_dump(exclude_unset=True)

    if "player_name" in update_data:
        update_data["normalized_name"] = normalize_text(update_data["player_name"])

    if "club_name" in update_data:
        update_data["normalized_club"] = normalize_text(update_data["club_name"])

    for key, value in update_data.items():
        setattr(record, key, value)

    db.commit()
    db.refresh(record)
    return record


@router.delete(
    "/{market_value_id}",
    summary="Delete a market value record",
    dependencies=[Depends(verify_api_key)],
    description="Deletes a market value record from the database using its unique ID."
)
def delete_market_value(market_value_id: int, db: Session = Depends(get_db)):
    """
    Delete a market value record by ID.
    """
    record = db.query(models.PlayerMarketValue).filter(
        models.PlayerMarketValue.id == market_value_id
    ).first()

    if not record:
        raise HTTPException(status_code=404, detail="Market value record not found")

    db.delete(record)
    db.commit()
    return {"message": "Market value record deleted successfully"}