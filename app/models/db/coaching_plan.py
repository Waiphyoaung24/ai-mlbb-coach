from sqlalchemy import Column, String, Float, Integer, ForeignKey, Enum as SAEnum, Date, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.models.db.base import UUIDMixin, TimestampMixin
from app.core.database import Base
import enum


class PlanType(str, enum.Enum):
    DAILY = "daily"
    WEEKLY = "weekly"


class CoachingPlan(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "coaching_plans"

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    plan_type = Column(SAEnum(PlanType), nullable=False)
    focus_areas = Column(JSON, default=list)
    tasks = Column(JSON, default=list)
    generated_by = Column(SAEnum("ai", "manual", name="plan_generator"), default="ai")
    valid_from = Column(Date, nullable=False)
    valid_until = Column(Date, nullable=False)

    user = relationship("User", back_populates="coaching_plans")


class PlayerStatsSnapshot(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "player_stats_snapshots"

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    rank_tier = Column(String, nullable=True)
    rank_stars = Column(Integer, nullable=True)
    win_rate = Column(Float, nullable=True)
    top_heroes = Column(JSON, default=list)
    weaknesses_detected = Column(JSON, default=list)
    snapshot_date = Column(Date, nullable=False)

    user = relationship("User", back_populates="stats_snapshots")
