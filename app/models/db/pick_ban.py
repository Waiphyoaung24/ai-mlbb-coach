from sqlalchemy import Column, String, ForeignKey, Enum as SAEnum, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.models.db.base import UUIDMixin, TimestampMixin
from app.core.database import Base
import enum


class PickBanAction(str, enum.Enum):
    PICK = "pick"
    BAN = "ban"


class DraftPhase(str, enum.Enum):
    FIRST_BAN = "first_ban"
    SECOND_BAN = "second_ban"
    FIRST_PICK = "first_pick"
    SECOND_PICK = "second_pick"


class DraftSide(str, enum.Enum):
    BLUE = "blue"
    RED = "red"


class PickBanRecord(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "pick_ban_records"

    team_id = Column(UUID(as_uuid=True), ForeignKey("teams.id"), nullable=False)
    opponent_team_name = Column(String, nullable=False)
    tournament_name = Column(String, nullable=True)
    match_date = Column(DateTime, nullable=True)
    source = Column(SAEnum("manual", "scraped", name="pickban_source"), default="manual")
    phase = Column(SAEnum(DraftPhase), nullable=False)
    hero_name = Column(String, nullable=False)
    action = Column(SAEnum(PickBanAction), nullable=False)
    side = Column(SAEnum(DraftSide), nullable=False)

    team = relationship("Team", back_populates="pick_bans")
