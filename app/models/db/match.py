from sqlalchemy import Column, String, Integer, Float, Text, ForeignKey, Enum as SAEnum, DateTime, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.models.db.base import UUIDMixin, TimestampMixin
from app.core.database import Base
import enum


class MatchSource(str, enum.Enum):
    MANUAL = "manual"
    MLBB_ACADEMY = "mlbb_academy"
    SCRAPED = "scraped"


class MatchType(str, enum.Enum):
    RANKED = "ranked"
    TOURNAMENT = "tournament"
    SCRIM = "scrim"
    CUSTOM = "custom"


class MatchResult(str, enum.Enum):
    WIN = "win"
    LOSS = "loss"


class Match(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "matches"

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    team_id = Column(UUID(as_uuid=True), ForeignKey("teams.id"), nullable=True)
    source = Column(SAEnum(MatchSource), nullable=False)
    match_type = Column(SAEnum(MatchType), nullable=False)
    result = Column(SAEnum(MatchResult), nullable=False)
    duration_seconds = Column(Integer, nullable=True)
    hero_played = Column(String, nullable=False)
    role_played = Column(String, nullable=True)
    kills = Column(Integer, default=0)
    deaths = Column(Integer, default=0)
    assists = Column(Integer, default=0)
    gold_earned = Column(Integer, nullable=True)
    damage_dealt = Column(Integer, nullable=True)
    match_date = Column(DateTime, nullable=True)
    opponent_team_name = Column(String, nullable=True)
    notes = Column(Text, nullable=True)
    raw_data = Column(JSON, nullable=True)

    user = relationship("User", back_populates="matches")
    team = relationship("Team")
