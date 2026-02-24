from pydantic import BaseModel, Field
from typing import Optional, List


class LinkAccountRequest(BaseModel):
    game_id: str = Field(..., description="MLBB Game ID")
    server_id: str = Field(..., description="MLBB Server/Zone ID")


class VerifyAccountRequest(BaseModel):
    game_id: str
    server_id: str
    verification_code: str


class PlayerProfile(BaseModel):
    game_id: str
    server_id: str
    username: Optional[str] = None
    rank_tier: Optional[str] = None
    rank_stars: Optional[int] = None
    win_rate: Optional[float] = None
    total_matches: Optional[int] = None
    top_heroes: Optional[List[dict]] = None

    class Config:
        from_attributes = True


class SyncStatusResponse(BaseModel):
    status: str  # syncing, completed, failed
    matches_synced: int = 0
    last_sync: Optional[str] = None
