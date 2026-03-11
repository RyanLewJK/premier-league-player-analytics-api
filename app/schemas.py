from pydantic import BaseModel

class PlayerBase(BaseModel):
    name: str
    team: str
    position: str
    goals: int
    assists: int
    minutes_played: int
    rating: float


class PlayerCreate(PlayerBase):
    pass


class PlayerResponse(PlayerBase):
    id: int

    class Config:
        from_attributes = True