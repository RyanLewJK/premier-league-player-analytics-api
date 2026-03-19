from fastapi import FastAPI
from .database import engine, Base, SessionLocal
from .routers import players, market_values, analytics, advanced_analytics
from . import models

from scripts import import_dataset, import_players_value

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Premier League Player Analytics API")

app.include_router(players.router)
app.include_router(market_values.router)
app.include_router(analytics.router)
app.include_router(advanced_analytics.router)


@app.on_event("startup")
def seed_database():
    db = SessionLocal()
    try:
        player_count = db.query(models.Player).count()
        market_value_count = db.query(models.PlayerMarketValue).count()

        if player_count == 0:
            print("Players table empty. Importing player dataset...")
            import_dataset.main()

        if market_value_count == 0:
            print("Market values table empty. Importing market value dataset...")
            import_players_value.main()

        if player_count > 0 and market_value_count > 0:
            print("Database already populated.")
    finally:
        db.close()


@app.get("/", tags=["Root"])
def root():
    return {"message": "Premier League Player Analytics API is running"}