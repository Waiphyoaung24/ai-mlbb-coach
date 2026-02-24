from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class LLMProvider(str, Enum):
    """Supported LLM providers."""
    CLAUDE = "claude"
    GEMINI = "gemini"


class HeroRole(str, Enum):
    """MLBB Hero Roles."""
    MARKSMAN = "Marksman"
    ASSASSIN = "Assassin"
    FIGHTER = "Fighter"
    TANK = "Tank"
    SUPPORT = "Support"
    MAGE = "Mage"


class HeroLane(str, Enum):
    """MLBB Lanes."""
    GOLD = "Gold Lane"
    EXP = "EXP Lane"
    MID = "Mid Lane"
    JUNGLE = "Jungle"
    ROAM = "Roam"


class Hero(BaseModel):
    """MLBB Hero model."""
    id: str
    name: str
    role: HeroRole
    specialty: List[str]
    lanes: List[HeroLane]
    difficulty: str  # Easy, Medium, Hard
    description: str
    strengths: List[str]
    weaknesses: List[str]
    counters: List[str] = []
    countered_by: List[str] = []


class Item(BaseModel):
    """MLBB Item model."""
    id: str
    name: str
    category: str  # Attack, Defense, Magic, Movement, Jungle
    cost: int
    stats: Dict[str, Any]
    passive: Optional[str] = None
    active: Optional[str] = None
    good_for: List[str] = []


class BuildRecommendation(BaseModel):
    """Hero build recommendation."""
    hero_name: str
    role: HeroRole
    core_items: List[str]
    situational_items: List[str]
    boots: str
    emblem: str
    emblem_talents: List[str]
    battle_spell: str
    playstyle: str
    reasoning: str


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
    lane: Optional[HeroLane] = None
    llm_provider: Optional[LLMProvider] = None


class MatchupAnalysis(BaseModel):
    """Matchup analysis response."""
    your_hero: str
    enemy_hero: str
    lane: Optional[HeroLane]
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
    role: Optional[HeroRole] = None
    lane: Optional[HeroLane] = None


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    version: str
    timestamp: datetime
    services: Dict[str, bool]
