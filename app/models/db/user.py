from sqlalchemy import Column, String, Enum as SAEnum
from sqlalchemy.orm import relationship
from app.models.db.base import UUIDMixin, TimestampMixin
from app.core.database import Base
import enum


class UserTier(str, enum.Enum):
    FREE = "free"
    PRO = "pro"


class User(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "users"

    email = Column(String, unique=True, nullable=False, index=True)
    username = Column(String, unique=True, nullable=False, index=True)
    hashed_password = Column(String, nullable=False)
    tier = Column(SAEnum(UserTier), default=UserTier.FREE, nullable=False)
    mlbb_game_id = Column(String, nullable=True)
    mlbb_server_id = Column(String, nullable=True)
    mlbb_username = Column(String, nullable=True)
    language = Column(String, default="my")

    teams = relationship("TeamMember", back_populates="user")
    matches = relationship("Match", back_populates="user")
    coaching_plans = relationship("CoachingPlan", back_populates="user")
    stats_snapshots = relationship("PlayerStatsSnapshot", back_populates="user")
