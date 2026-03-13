from pydantic import BaseModel
from typing import Optional


class PlayerBase(BaseModel):
    player_name: str
    club_name: str
    position_name: str
    minutes: int
    total_points: int
    points_per_game: float
    goals_scored: int
    assists: int
    clean_sheets: int
    goals_conceded: int
    saves: int
    defensive_contribution: int
    yellow_cards: int
    red_cards: int
    bonus: int


class PlayerCreate(PlayerBase):
    pass


class PlayerResponse(PlayerBase):
    id: int

    class Config:
        from_attributes = True


class PlayerMarketValueBase(BaseModel):
    player_name: str
    club_name: str
    age: int
    position: Optional[str] = None
    position_group: Optional[str] = None
    league_name: Optional[str] = None
    current_value_gbp: float
    peak_value_gbp: float
    trajectory: Optional[str] = None


class PlayerMarketValueResponse(PlayerMarketValueBase):
    id: int

    class Config:
        from_attributes = True


class PlayerScoreResponse(BaseModel):
    player_id: int
    player_name: str
    club_name: str
    position_name: str
    minutes: int
    performance_score: float
    market_value_gbp: Optional[float] = None
    value_score: Optional[float] = None
    breakout_score: Optional[float] = None

    class Config:
        from_attributes = True