from sqlalchemy import Column, String, Text, ForeignKey, Enum as SAEnum, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.models.db.base import UUIDMixin, TimestampMixin
from app.core.database import Base


class ScoutingReport(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "scouting_reports"

    team_id = Column(UUID(as_uuid=True), ForeignKey("teams.id"), nullable=False)
    opponent_team_name = Column(String, nullable=False)
    generated_by_llm = Column(SAEnum("claude", "gemini", name="llm_provider_enum"), nullable=False)
    report_content = Column(Text, nullable=False)
    pick_ban_summary = Column(JSON, default=dict)
    key_players = Column(JSON, default=list)
    recommended_strategy = Column(Text, nullable=True)

    team = relationship("Team", back_populates="scouting_reports")
