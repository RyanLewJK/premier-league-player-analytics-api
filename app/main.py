from fastapi import FastAPI
from .database import engine, Base
from .routers import players, market_values, analytics, advanced_analytics

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Premier League Player Analytics API")

app.include_router(players.router)
app.include_router(market_values.router)
app.include_router(analytics.router)
app.include_router(advanced_analytics.router)


@app.get("/", tags=["Root"])
def root():
    return {"message": "Premier League Player Analytics API is running"}