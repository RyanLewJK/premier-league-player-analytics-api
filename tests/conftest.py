import os
import sys

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Make sure project root is importable
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.main import app
from app.database import Base
from app.models import Player, PlayerMarketValue
from app.routers.players import get_db as players_get_db
from app.routers.market_values import get_db as market_values_get_db
from app.routers.analytics import get_db as analytics_get_db
from app.routers.advanced_analytics import get_db as advanced_analytics_get_db

TEST_DATABASE_URL = "sqlite:///./test_premier_league.db"

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False}
)

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[players_get_db] = override_get_db
app.dependency_overrides[market_values_get_db] = override_get_db
app.dependency_overrides[analytics_get_db] = override_get_db
app.dependency_overrides[advanced_analytics_get_db] = override_get_db


@pytest.fixture(scope="function")
def db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db):
    yield TestClient(app)


@pytest.fixture(scope="function")
def sample_players(db):
    players = [
        Player(
            player_name="Mohamed Salah",
            club_name="Liverpool",
            position_name="MID",
            minutes=2800,
            total_points=240,
            points_per_game=7.5,
            goals_scored=18,
            assists=10,
            clean_sheets=12,
            goals_conceded=30,
            saves=0,
            defensive_contribution=20,
            yellow_cards=2,
            red_cards=0,
            bonus=25
        ),
        Player(
            player_name="Cole Palmer",
            club_name="Chelsea",
            position_name="MID",
            minutes=2500,
            total_points=210,
            points_per_game=6.8,
            goals_scored=16,
            assists=9,
            clean_sheets=8,
            goals_conceded=38,
            saves=0,
            defensive_contribution=15,
            yellow_cards=4,
            red_cards=0,
            bonus=20
        ),
        Player(
            player_name="Virgil van Dijk",
            club_name="Liverpool",
            position_name="DEF",
            minutes=3000,
            total_points=170,
            points_per_game=5.2,
            goals_scored=4,
            assists=2,
            clean_sheets=16,
            goals_conceded=28,
            saves=0,
            defensive_contribution=80,
            yellow_cards=3,
            red_cards=0,
            bonus=18
        ),
        Player(
            player_name="Alphonse Areola",
            club_name="West Ham",
            position_name="GK",
            minutes=2600,
            total_points=140,
            points_per_game=4.5,
            goals_scored=0,
            assists=0,
            clean_sheets=9,
            goals_conceded=45,
            saves=120,
            defensive_contribution=10,
            yellow_cards=1,
            red_cards=0,
            bonus=12
        ),
        Player(
            player_name="Young Prospect",
            club_name="Brighton",
            position_name="FWD",
            minutes=950,
            total_points=95,
            points_per_game=5.0,
            goals_scored=8,
            assists=3,
            clean_sheets=2,
            goals_conceded=20,
            saves=0,
            defensive_contribution=5,
            yellow_cards=1,
            red_cards=0,
            bonus=8
        ),
    ]

    db.add_all(players)
    db.commit()

    for player in players:
        db.refresh(player)

    return players


@pytest.fixture(scope="function")
def sample_market_values(db):
    market_values = [
        PlayerMarketValue(
            player_name="Mohamed Salah",
            normalized_name="mohamed salah",
            club_name="Liverpool",
            normalized_club="liverpool",
            age=32,
            position="RW",
            position_group="MID",
            league_name="Premier League",
            current_value_gbp=55000000,
            peak_value_gbp=130000000,
            trajectory="falling"
        ),
        PlayerMarketValue(
            player_name="Cole Palmer",
            normalized_name="cole palmer",
            club_name="Chelsea",
            normalized_club="chelsea",
            age=22,
            position="AM",
            position_group="MID",
            league_name="Premier League",
            current_value_gbp=40000000,
            peak_value_gbp=45000000,
            trajectory="rising"
        ),
        PlayerMarketValue(
            player_name="Virgil van Dijk",
            normalized_name="virgil van dijk",
            club_name="Liverpool",
            normalized_club="liverpool",
            age=33,
            position="CB",
            position_group="DEF",
            league_name="Premier League",
            current_value_gbp=28000000,
            peak_value_gbp=90000000,
            trajectory="falling"
        ),
        PlayerMarketValue(
            player_name="Alphonse Areola",
            normalized_name="alphonse areola",
            club_name="West Ham",
            normalized_club="west ham",
            age=31,
            position="GK",
            position_group="GK",
            league_name="Premier League",
            current_value_gbp=9000000,
            peak_value_gbp=18000000,
            trajectory="stable"
        ),
    ]

    db.add_all(market_values)
    db.commit()

    for mv in market_values:
        db.refresh(mv)

    return market_values