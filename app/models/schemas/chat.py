from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class LLMProvider(str, Enum):
    """Supported LLM providers."""
    CLAUDE = "claude"
    GEMINI = "gemini"


class ChatMessage(BaseModel):
    """Chat message model."""
    role: str  # user, assistant, system
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ChatRequest(BaseModel):
    """Chat request from user."""
    message: str
    session_id: Optional[str] = None
    llm_provider: Optional[LLMProvider] = None
    context: Optional[Dict[str, Any]] = None


class ChatResponse(BaseModel):
    """Chat response to user."""
    response: str
    session_id: str
    sources: Optional[List[Dict[str, Any]]] = None
    suggestions: Optional[List[str]] = None


class MatchupRequest(BaseModel):
    """Matchup analysis request."""
    your_hero: str
    enemy_hero: str
    lane: Optional[str] = None
    llm_provider: Optional[LLMProvider] = None


class MatchupAnalysis(BaseModel):
    """Matchup analysis response."""
    your_hero: str
    enemy_hero: str
    lane: Optional[str]
    difficulty: str  # Easy, Medium, Hard
    key_points: List[str]
    tips: List[str]
    item_adjustments: List[str]
    win_conditions: List[str]


class BuildRequest(BaseModel):
    """Build recommendation request."""
    hero_name: str
    enemy_composition: Optional[List[str]] = None
    situation: Optional[str] = None  # ahead, behind, balanced
    llm_provider: Optional[LLMProvider] = None


class HeroQueryRequest(BaseModel):
    """Hero information query."""
    hero_name: Optional[str] = None
    role: Optional[str] = None
    lane: Optional[str] = None


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    version: str
    timestamp: datetime
    services: Dict[str, bool]
