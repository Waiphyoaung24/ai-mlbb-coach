from pydantic import BaseModel, Field
from typing import Optional, List


class ValidateAccountRequest(BaseModel):
    game_id: str = Field(..., description="MLBB Game ID")
    server_id: str = Field(..., description="MLBB Server/Zone ID")


class ValidateAccountResponse(BaseModel):
    valid: bool
    game_id: str
    server_id: str
    username: Optional[str] = None
    country: Optional[str] = None
    error: Optional[str] = None


class ConfirmLinkRequest(BaseModel):
    game_id: str = Field(..., description="MLBB Game ID")
    server_id: str = Field(..., description="MLBB Server/Zone ID")
    username: str = Field(..., description="Confirmed in-game username")


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
