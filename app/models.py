from sqlalchemy import Column, Integer, String, Float
from .database import Base


class Player(Base):
    __tablename__ = "players"

    id = Column(Integer, primary_key=True, index=True)
    player_name = Column(String, nullable=False, index=True)
    club_name = Column(String, nullable=False, index=True)
    position_name = Column(String, nullable=False, index=True)

    minutes = Column(Integer, default=0)
    total_points = Column(Integer, default=0)
    points_per_game = Column(Float, default=0.0)

    goals_scored = Column(Integer, default=0)
    assists = Column(Integer, default=0)
    clean_sheets = Column(Integer, default=0)
    goals_conceded = Column(Integer, default=0)
    saves = Column(Integer, default=0)
    defensive_contribution = Column(Integer, default=0)

    yellow_cards = Column(Integer, default=0)
    red_cards = Column(Integer, default=0)
    bonus = Column(Integer, default=0)


class PlayerMarketValue(Base):
    __tablename__ = "player_market_values"

    id = Column(Integer, primary_key=True, index=True)
    player_name = Column(String, nullable=False, index=True)
    normalized_name = Column(String, nullable=False, index=True)
    club_name = Column(String, nullable=False, index=True)
    normalized_club = Column(String, nullable=False, index=True)

    age = Column(Integer, default=0)
    position = Column(String, nullable=True)
    position_group = Column(String, nullable=True)
    league_name = Column(String, nullable=True)

    current_value_gbp = Column(Float, default=0.0)
    peak_value_gbp = Column(Float, default=0.0)
    trajectory = Column(String, nullable=True)