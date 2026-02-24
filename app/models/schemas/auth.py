from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID


class RegisterRequest(BaseModel):
    email: str = Field(..., min_length=5)
    username: str = Field(..., min_length=3, max_length=30)
    password: str = Field(..., min_length=8)
    language: str = Field(default="my")


class LoginRequest(BaseModel):
    email: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    id: UUID
    email: str
    username: str
    tier: str
    mlbb_game_id: Optional[str] = None
    mlbb_server_id: Optional[str] = None
    language: str

    class Config:
        from_attributes = True
