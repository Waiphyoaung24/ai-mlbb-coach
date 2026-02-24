from sqlalchemy import Column, String, ForeignKey, Enum as SAEnum, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.models.db.base import UUIDMixin, TimestampMixin
from app.core.database import Base
from datetime import datetime
import enum


class TeamMemberRole(str, enum.Enum):
    OWNER = "owner"
    COACH = "coach"
    ANALYST = "analyst"
    PLAYER = "player"


class Team(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "teams"

    name = Column(String, nullable=False)
    owner_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    tier = Column(SAEnum("free", "pro", name="team_tier"), default="free")
    region = Column(String, default="MM")

    owner = relationship("User", foreign_keys=[owner_id])
    members = relationship("TeamMember", back_populates="team")
    pick_bans = relationship("PickBanRecord", back_populates="team")
    scouting_reports = relationship("ScoutingReport", back_populates="team")


class TeamMember(Base):
    __tablename__ = "team_members"

    team_id = Column(UUID(as_uuid=True), ForeignKey("teams.id"), primary_key=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), primary_key=True)
    role = Column(SAEnum(TeamMemberRole), default=TeamMemberRole.PLAYER)
    joined_at = Column(DateTime, default=datetime.utcnow)

    team = relationship("Team", back_populates="members")
    user = relationship("User", back_populates="teams")
