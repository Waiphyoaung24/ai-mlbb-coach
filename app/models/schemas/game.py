from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from enum import Enum


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
