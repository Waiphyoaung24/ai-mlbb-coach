# Phase 1: Foundation Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Restructure the existing MLBB AI Coach into a SaaS-ready monolith with auth, PostgreSQL, MLBB Academy integration, and a React frontend — targeting Myanmar players.

**Architecture:** Monolith First. FastAPI backend with v1 API routes, SQLAlchemy ORM + Alembic migrations for PostgreSQL, JWT auth, existing LangChain/LangGraph/RAG services preserved and wrapped with auth. React + Vite + TypeScript frontend with Burmese + English i18n.

**Tech Stack:** FastAPI, SQLAlchemy, Alembic, python-jose, passlib, React, Vite, TypeScript, react-i18next, Recharts, LangChain, LangGraph, Pinecone, Anthropic Claude, Google Gemini.

**Existing code to preserve:** `app/services/llm/provider.py` (LLM factory), `app/services/rag/` (vector store + retrievers), `app/services/langgraph/coaching_graph.py` (coaching workflow), `app/data/` (MLBB knowledge base JSON files), `app/utils/session_manager.py`.

---

## Task 1: Project Restructure — New Directory Layout

**Files:**
- Create: `app/api/v1/__init__.py`
- Create: `app/api/deps.py`
- Create: `app/core/security.py` (empty placeholder)
- Create: `app/core/database.py` (empty placeholder)
- Create: `app/models/db/__init__.py`
- Create: `app/models/schemas/__init__.py`
- Move: `app/models/schemas.py` → `app/models/schemas/chat.py`
- Create: `app/services/mlbb_academy/__init__.py`
- Create: `app/services/analytics/__init__.py`
- Create: `app/services/scouting/__init__.py`
- Create: `app/services/coaching/__init__.py`

**Step 1: Create new directory structure**

```bash
mkdir -p app/api/v1
mkdir -p app/models/db
mkdir -p app/models/schemas
mkdir -p app/services/mlbb_academy
mkdir -p app/services/analytics
mkdir -p app/services/scouting
mkdir -p app/services/coaching
```

**Step 2: Create `__init__.py` files for all new packages**

Create empty `__init__.py` in each new directory:
- `app/api/v1/__init__.py`
- `app/models/db/__init__.py`
- `app/models/schemas/__init__.py`
- `app/services/mlbb_academy/__init__.py`
- `app/services/analytics/__init__.py`
- `app/services/scouting/__init__.py`
- `app/services/coaching/__init__.py`

**Step 3: Move existing schemas**

Move `app/models/schemas.py` to `app/models/schemas/chat.py`. Update the `LLMProvider` enum and chat-related schemas into this file. Keep `HeroRole`, `HeroLane`, `Hero`, `Item` in a new `app/models/schemas/game.py`.

In `app/models/schemas/__init__.py`, re-export everything so existing imports still work:

```python
from app.models.schemas.chat import *
from app.models.schemas.game import *
```

**Step 4: Create empty placeholder files**

Create these files with just docstrings — they'll be filled in later tasks:
- `app/core/security.py` — `"""JWT authentication and password hashing."""`
- `app/core/database.py` — `"""SQLAlchemy engine and session management."""`
- `app/api/deps.py` — `"""Shared API dependencies (auth, DB session)."""`

**Step 5: Verify existing code still works**

Run: `cd /workspace/Test-AI-Matchmaking && python -c "from app.main import app; print('OK')"`
Expected: `OK` (no import errors)

**Step 6: Commit**

```bash
git add -A
git commit -m "refactor: restructure project for SaaS architecture

Create v1 API directory, split schemas into domain modules,
add placeholder files for auth, database, and new services."
```

---

## Task 2: PostgreSQL Database Setup with SQLAlchemy + Alembic

**Files:**
- Modify: `app/core/config.py` — add DATABASE_URL handling
- Create: `app/core/database.py` — SQLAlchemy async engine and session
- Create: `app/models/db/base.py` — Base model class
- Create: `app/models/db/user.py` — User ORM model
- Create: `app/models/db/team.py` — Team + TeamMember ORM models
- Create: `app/models/db/match.py` — Match ORM model
- Create: `app/models/db/pick_ban.py` — PickBanRecord ORM model
- Create: `app/models/db/coaching_plan.py` — CoachingPlan + PlayerStatsSnapshot ORM models
- Create: `app/models/db/scouting_report.py` — ScoutingReport ORM model
- Create: `alembic.ini`
- Create: `alembic/env.py`
- Create: `tests/conftest.py`
- Create: `tests/test_db.py`

**Step 1: Write `app/core/database.py`**

```python
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from app.core.config import get_settings


class Base(DeclarativeBase):
    pass


settings = get_settings()

engine = create_async_engine(
    settings.DATABASE_URL or "sqlite+aiosqlite:///./test.db",
    echo=settings.DEBUG,
)

async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def get_db() -> AsyncSession:
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()
```

**Step 2: Write `app/models/db/base.py`**

```python
import uuid
from datetime import datetime
from sqlalchemy import Column, DateTime
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base


class TimestampMixin:
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class UUIDMixin:
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
```

**Step 3: Write `app/models/db/user.py`**

```python
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
    language = Column(String, default="my")

    teams = relationship("TeamMember", back_populates="user")
    matches = relationship("Match", back_populates="user")
    coaching_plans = relationship("CoachingPlan", back_populates="user")
    stats_snapshots = relationship("PlayerStatsSnapshot", back_populates="user")
```

**Step 4: Write `app/models/db/team.py`**

```python
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
```

**Step 5: Write `app/models/db/match.py`**

```python
from sqlalchemy import Column, String, Integer, Float, Text, ForeignKey, Enum as SAEnum, DateTime
from sqlalchemy.dialects.postgresql import UUID, JSONB
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
    raw_data = Column(JSONB, nullable=True)

    user = relationship("User", back_populates="matches")
    team = relationship("Team")
```

**Step 6: Write `app/models/db/pick_ban.py`**

```python
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
```

**Step 7: Write `app/models/db/coaching_plan.py`**

```python
from sqlalchemy import Column, String, Float, Integer, ForeignKey, Enum as SAEnum, Date
from sqlalchemy.dialects.postgresql import UUID, JSONB
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
    focus_areas = Column(JSONB, default=list)
    tasks = Column(JSONB, default=list)
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
    top_heroes = Column(JSONB, default=list)
    weaknesses_detected = Column(JSONB, default=list)
    snapshot_date = Column(Date, nullable=False)

    user = relationship("User", back_populates="stats_snapshots")
```

**Step 8: Write `app/models/db/scouting_report.py`**

```python
from sqlalchemy import Column, String, Text, ForeignKey, Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from app.models.db.base import UUIDMixin, TimestampMixin
from app.core.database import Base


class ScoutingReport(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "scouting_reports"

    team_id = Column(UUID(as_uuid=True), ForeignKey("teams.id"), nullable=False)
    opponent_team_name = Column(String, nullable=False)
    generated_by_llm = Column(SAEnum("claude", "gemini", name="llm_provider_enum"), nullable=False)
    report_content = Column(Text, nullable=False)
    pick_ban_summary = Column(JSONB, default=dict)
    key_players = Column(JSONB, default=list)
    recommended_strategy = Column(Text, nullable=True)

    team = relationship("Team", back_populates="scouting_reports")
```

**Step 9: Write `app/models/db/__init__.py`** to export all models

```python
from app.models.db.user import User, UserTier
from app.models.db.team import Team, TeamMember, TeamMemberRole
from app.models.db.match import Match, MatchSource, MatchType, MatchResult
from app.models.db.pick_ban import PickBanRecord, PickBanAction, DraftPhase, DraftSide
from app.models.db.coaching_plan import CoachingPlan, PlayerStatsSnapshot, PlanType
from app.models.db.scouting_report import ScoutingReport
```

**Step 10: Initialize Alembic**

Run: `cd /workspace/Test-AI-Matchmaking && alembic init alembic`

Then modify `alembic/env.py` to use async engine and import all models:

Replace the `run_migrations_online` and imports in `alembic/env.py`:

```python
import asyncio
from logging.config import fileConfig
from sqlalchemy import pool
from sqlalchemy.ext.asyncio import create_async_engine
from alembic import context
from app.core.config import get_settings
from app.core.database import Base
from app.models.db import *  # noqa: F401,F403 — import all models for autogenerate

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata
settings = get_settings()


def run_migrations_offline():
    url = settings.DATABASE_URL
    context.configure(url=url, target_metadata=target_metadata, literal_binds=True)
    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection):
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online():
    connectable = create_async_engine(
        settings.DATABASE_URL,
        poolclass=pool.NullPool,
    )
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
```

Update `alembic.ini` — set `sqlalchemy.url` to empty (we use settings):
```ini
sqlalchemy.url =
```

**Step 11: Add `aiosqlite` to requirements for testing**

Append to `requirements.txt`:
```
aiosqlite==0.20.0
```

**Step 12: Write test `tests/test_db.py`**

```python
import pytest
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from app.core.database import Base
from app.models.db import User, UserTier, Team, TeamMember, TeamMemberRole


@pytest.fixture
async def db_session():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with session_factory() as session:
        yield session
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest.mark.asyncio
async def test_create_user(db_session):
    user = User(
        email="test@example.com",
        username="testplayer",
        hashed_password="fakehash",
        tier=UserTier.FREE,
        language="my",
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    assert user.id is not None
    assert user.email == "test@example.com"
    assert user.tier == UserTier.FREE


@pytest.mark.asyncio
async def test_create_team_with_member(db_session):
    user = User(email="owner@test.com", username="owner", hashed_password="hash")
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    team = Team(name="Myanmar Esports", owner_id=user.id, region="MM")
    db_session.add(team)
    await db_session.commit()
    await db_session.refresh(team)

    member = TeamMember(team_id=team.id, user_id=user.id, role=TeamMemberRole.OWNER)
    db_session.add(member)
    await db_session.commit()

    assert team.name == "Myanmar Esports"
    assert team.region == "MM"
```

**Step 13: Write test config `tests/conftest.py`**

```python
import pytest

pytest_plugins = []
```

**Step 14: Run tests to verify models work**

Run: `cd /workspace/Test-AI-Matchmaking && python -m pytest tests/test_db.py -v`
Expected: 2 tests PASS

**Step 15: Commit**

```bash
git add -A
git commit -m "feat: add PostgreSQL database models and Alembic migrations

Add SQLAlchemy ORM models for users, teams, matches, pick/ban records,
coaching plans, player stats snapshots, and scouting reports.
Configure Alembic for async migrations. Add DB tests."
```

---

## Task 3: JWT Authentication System

**Files:**
- Create: `app/core/security.py` — JWT token creation + password hashing
- Create: `app/models/schemas/auth.py` — Auth request/response schemas
- Create: `app/api/deps.py` — `get_current_user` dependency
- Create: `app/api/v1/auth.py` — Register + login + refresh endpoints
- Create: `tests/test_auth.py`

**Step 1: Write `app/core/security.py`**

```python
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.core.config import get_settings

settings = get_settings()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

ALGORITHM = "HS256"


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)


def decode_access_token(token: str) -> Optional[dict]:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None
```

**Step 2: Write `app/models/schemas/auth.py`**

```python
from pydantic import BaseModel, EmailStr, Field
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
```

**Step 3: Write `app/api/deps.py`**

```python
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.core.security import decode_access_token
from app.models.db.user import User

security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> User:
    token = credentials.credentials
    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload")

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

    return user
```

**Step 4: Write `app/api/v1/auth.py`**

```python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.core.security import get_password_hash, verify_password, create_access_token
from app.models.db.user import User
from app.models.schemas.auth import RegisterRequest, LoginRequest, TokenResponse, UserResponse
from app.api.deps import get_current_user

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(request: RegisterRequest, db: AsyncSession = Depends(get_db)):
    # Check email uniqueness
    result = await db.execute(select(User).where(User.email == request.email))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email already registered")

    # Check username uniqueness
    result = await db.execute(select(User).where(User.username == request.username))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Username already taken")

    user = User(
        email=request.email,
        username=request.username,
        hashed_password=get_password_hash(request.password),
        language=request.language,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)

    token = create_access_token(data={"sub": str(user.id)})
    return TokenResponse(access_token=token)


@router.post("/login", response_model=TokenResponse)
async def login(request: LoginRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == request.email))
    user = result.scalar_one_or_none()

    if not user or not verify_password(request.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    token = create_access_token(data={"sub": str(user.id)})
    return TokenResponse(access_token=token)


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user
```

**Step 5: Write `tests/test_auth.py`**

```python
import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from app.core.database import Base, get_db
from app.main import app


@pytest.fixture
async def test_db():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async def override_get_db():
        async with session_factory() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db
    yield
    app.dependency_overrides.clear()
    await engine.dispose()


@pytest.fixture
async def client(test_db):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.mark.asyncio
async def test_register(client):
    response = await client.post("/api/v1/auth/register", json={
        "email": "player@test.com",
        "username": "mmplayer",
        "password": "securepass123",
        "language": "my",
    })
    assert response.status_code == 201
    data = response.json()
    assert "access_token" in data


@pytest.mark.asyncio
async def test_login(client):
    # Register first
    await client.post("/api/v1/auth/register", json={
        "email": "login@test.com",
        "username": "loginuser",
        "password": "securepass123",
    })
    # Login
    response = await client.post("/api/v1/auth/login", json={
        "email": "login@test.com",
        "password": "securepass123",
    })
    assert response.status_code == 200
    assert "access_token" in response.json()


@pytest.mark.asyncio
async def test_get_me(client):
    # Register
    reg = await client.post("/api/v1/auth/register", json={
        "email": "me@test.com",
        "username": "meuser",
        "password": "securepass123",
    })
    token = reg.json()["access_token"]

    response = await client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["email"] == "me@test.com"


@pytest.mark.asyncio
async def test_duplicate_email(client):
    await client.post("/api/v1/auth/register", json={
        "email": "dup@test.com", "username": "user1", "password": "securepass123",
    })
    response = await client.post("/api/v1/auth/register", json={
        "email": "dup@test.com", "username": "user2", "password": "securepass123",
    })
    assert response.status_code == 400
```

**Step 6: Wire auth router into `app/main.py`**

Add to `app/main.py`:
```python
from app.api.v1.auth import router as auth_router
app.include_router(auth_router, prefix="/api/v1")
```

**Step 7: Run tests**

Run: `cd /workspace/Test-AI-Matchmaking && python -m pytest tests/test_auth.py -v`
Expected: 4 tests PASS

**Step 8: Commit**

```bash
git add -A
git commit -m "feat: add JWT authentication system

Register, login, and /me endpoints with password hashing,
JWT token creation/validation, and get_current_user dependency."
```

---

## Task 4: Port Existing Chat to v1 API with Auth

**Files:**
- Create: `app/api/v1/chat.py` — Authed version of chat endpoint
- Create: `app/api/v1/heroes.py` — Hero info endpoints
- Modify: `app/main.py` — Mount v1 router, keep old routes for backward compat
- Create: `tests/test_chat.py`

**Step 1: Write `app/api/v1/chat.py`**

Port the existing chat endpoint from `app/api/routes.py` but add auth dependency. Keep the same LangGraph workflow.

```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
import uuid
import logging

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.db.user import User
from app.models.schemas.chat import ChatRequest, ChatResponse, LLMProvider
from app.services.langgraph.coaching_graph import MLBBCoachingGraph, _extract_text
from app.services.llm.provider import LLMFactory

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/chat", tags=["chat"])

# In-memory sessions (migrate to Redis later)
sessions = {}


def _check_provider(llm_provider: Optional[LLMProvider] = None):
    available = LLMFactory.list_available_providers()
    if not available:
        raise HTTPException(status_code=503, detail="No LLM providers configured.")
    if llm_provider and llm_provider not in available:
        raise HTTPException(
            status_code=400,
            detail=f"Provider '{llm_provider.value}' not available. Available: {[p.value for p in available]}",
        )


@router.post("/", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
):
    _check_provider(request.llm_provider)

    try:
        session_id = request.session_id or str(uuid.uuid4())
        if session_id not in sessions:
            sessions[session_id] = []

        graph = MLBBCoachingGraph(llm_provider=request.llm_provider)
        result = graph.process_message(
            user_message=request.message,
            conversation_history=sessions[session_id],
            llm_provider=request.llm_provider,
        )
        sessions[session_id] = sessions.get(session_id, [])

        return ChatResponse(
            response=result["response"],
            session_id=session_id,
            sources=None,
            suggestions=_suggestions(result["intent"]),
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


def _suggestions(intent: str):
    m = {
        "hero_info": ["What items should I build?", "How do I play this matchup?"],
        "build_recommendation": ["When should I build defensively?", "Best emblem?"],
        "matchup_analysis": ["How do I position in team fights?", "Counter items?"],
        "general_strategy": ["How do I farm efficiently?", "Team fight tips?"],
    }
    return m.get(intent, ["Tell me about a hero", "Recommend a build"])
```

**Step 2: Write `app/api/v1/heroes.py`**

```python
from fastapi import APIRouter
from typing import List, Optional
import json
from pathlib import Path

router = APIRouter(prefix="/heroes", tags=["heroes"])

DATA_DIR = Path(__file__).parent.parent.parent / "data" / "heroes"


@router.get("/", response_model=List[dict])
async def list_heroes(role: Optional[str] = None):
    heroes = []
    for file in DATA_DIR.glob("*.json"):
        with open(file) as f:
            data = json.load(f)
            for hero in data:
                if role is None or hero.get("role", "").lower() == role.lower():
                    heroes.append({
                        "id": hero["id"],
                        "name": hero["name"],
                        "role": hero["role"],
                        "difficulty": hero["difficulty"],
                        "lanes": hero.get("lanes", []),
                    })
    return heroes


@router.get("/{hero_id}")
async def get_hero(hero_id: str):
    for file in DATA_DIR.glob("*.json"):
        with open(file) as f:
            data = json.load(f)
            for hero in data:
                if hero["id"] == hero_id:
                    return hero
    return {"error": "Hero not found"}
```

**Step 3: Update `app/main.py` to mount v1 routers**

Add imports and mount:
```python
from app.api.v1.auth import router as auth_router
from app.api.v1.chat import router as chat_router
from app.api.v1.heroes import router as heroes_router

app.include_router(auth_router, prefix="/api/v1")
app.include_router(chat_router, prefix="/api/v1")
app.include_router(heroes_router, prefix="/api/v1")
```

Keep the old `app.include_router(router, tags=["coaching"])` for backward compatibility during migration.

**Step 4: Verify**

Run: `cd /workspace/Test-AI-Matchmaking && python -c "from app.main import app; print('Routes:', len(app.routes))"`
Expected: No import errors, prints route count

**Step 5: Commit**

```bash
git add -A
git commit -m "feat: port chat and heroes endpoints to v1 API with auth

Add authenticated /api/v1/chat and /api/v1/heroes endpoints.
Old routes preserved at /api/ for backward compatibility."
```

---

## Task 5: MLBB Academy Integration Service

**Files:**
- Create: `app/services/mlbb_academy/client.py` — Academy API client
- Create: `app/models/schemas/player.py` — Player-related schemas
- Create: `app/api/v1/players.py` — Player profile + link account endpoints
- Create: `tests/test_mlbb_academy.py`

**Step 1: Write `app/models/schemas/player.py`**

```python
from pydantic import BaseModel, Field
from typing import Optional, List
from uuid import UUID


class LinkAccountRequest(BaseModel):
    game_id: str = Field(..., description="MLBB Game ID")
    server_id: str = Field(..., description="MLBB Server/Zone ID")


class VerifyAccountRequest(BaseModel):
    game_id: str
    server_id: str
    verification_code: str


class PlayerProfile(BaseModel):
    game_id: str
    server_id: str
    username: Optional[str] = None
    rank_tier: Optional[str] = None
    rank_stars: Optional[int] = None
    win_rate: Optional[float] = None
    total_matches: Optional[int] = None
    top_heroes: Optional[List[dict]] = None

    class Config:
        from_attributes = True


class SyncStatusResponse(BaseModel):
    status: str  # syncing, completed, failed
    matches_synced: int = 0
    last_sync: Optional[str] = None
```

**Step 2: Write `app/services/mlbb_academy/client.py`**

```python
import httpx
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

ACADEMY_BASE_URL = "https://www.mobilelegends.com"


class MLBBAcademyClient:
    """Client for interacting with MLBB Academy APIs.

    The MLBB Academy site (mobilelegends.com/academy/self) authenticates
    via Game ID + Server ID + in-game mail verification code.

    This client wraps the underlying API calls the Academy SPA makes.
    Endpoints need to be discovered via browser network inspection.
    """

    def __init__(self):
        self._http = httpx.AsyncClient(
            base_url=ACADEMY_BASE_URL,
            timeout=30.0,
            headers={"User-Agent": "MLBB-AI-Coach/1.0"},
        )
        self._session_tokens: Dict[str, str] = {}

    async def request_verification(self, game_id: str, server_id: str) -> dict:
        """Request a verification code to be sent to player's in-game mail.

        TODO: Reverse-engineer the actual Academy API endpoint.
        For now, returns a mock response so the flow can be built end-to-end.
        """
        logger.info(f"Requesting verification for game_id={game_id}, server_id={server_id}")

        # TODO: Replace with real API call once endpoint is discovered
        # The real flow:
        # 1. POST to Academy login endpoint with game_id + server_id
        # 2. Academy sends verification code to in-game mail
        # 3. Return session token for verification step

        return {
            "status": "verification_sent",
            "message": "Verification code sent to your in-game mail",
            "game_id": game_id,
            "server_id": server_id,
        }

    async def verify_and_login(
        self, game_id: str, server_id: str, verification_code: str
    ) -> Optional[dict]:
        """Verify the code and establish an authenticated session.

        TODO: Reverse-engineer the actual verification endpoint.
        """
        logger.info(f"Verifying game_id={game_id} with code")

        # TODO: Replace with real API call
        # The real flow:
        # 1. POST verification code to Academy
        # 2. Receive auth token/cookie
        # 3. Store session for subsequent data fetches

        return {
            "status": "verified",
            "session_token": f"mock_token_{game_id}_{server_id}",
        }

    async def fetch_player_profile(self, game_id: str, server_id: str) -> Optional[dict]:
        """Fetch player profile data from Academy.

        TODO: Replace with real API call.
        """
        logger.info(f"Fetching profile for game_id={game_id}")

        # TODO: Real API call to fetch profile
        return {
            "game_id": game_id,
            "server_id": server_id,
            "username": None,  # Will come from real API
            "rank_tier": None,
            "win_rate": None,
            "total_matches": None,
        }

    async def fetch_match_history(
        self, game_id: str, server_id: str, limit: int = 50
    ) -> list:
        """Fetch recent match history from Academy.

        TODO: Replace with real API call.
        """
        logger.info(f"Fetching match history for game_id={game_id}, limit={limit}")

        # TODO: Real API call to fetch matches
        return []

    async def close(self):
        await self._http.aclose()


# Singleton
_client: Optional[MLBBAcademyClient] = None


def get_academy_client() -> MLBBAcademyClient:
    global _client
    if _client is None:
        _client = MLBBAcademyClient()
    return _client
```

**Step 3: Write `app/api/v1/players.py`**

```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.db.user import User
from app.models.db.match import Match
from app.models.schemas.player import (
    LinkAccountRequest, VerifyAccountRequest, PlayerProfile, SyncStatusResponse,
)
from app.services.mlbb_academy.client import get_academy_client

router = APIRouter(prefix="/players", tags=["players"])


@router.post("/link-account")
async def link_account(
    request: LinkAccountRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Step 1: Request verification code for MLBB account linking."""
    client = get_academy_client()
    result = await client.request_verification(request.game_id, request.server_id)

    # Store game_id and server_id on user (unverified)
    current_user.mlbb_game_id = request.game_id
    current_user.mlbb_server_id = request.server_id
    await db.commit()

    return result


@router.post("/verify-account")
async def verify_account(
    request: VerifyAccountRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Step 2: Verify code and complete account linking."""
    client = get_academy_client()
    result = await client.verify_and_login(
        request.game_id, request.server_id, request.verification_code,
    )

    if not result or result.get("status") != "verified":
        raise HTTPException(status_code=400, detail="Verification failed")

    # Fetch initial profile data
    profile = await client.fetch_player_profile(request.game_id, request.server_id)

    return {
        "status": "account_linked",
        "profile": profile,
        "message": "Account linked successfully. Match data will sync shortly.",
    }


@router.get("/me/profile", response_model=PlayerProfile)
async def get_profile(
    current_user: User = Depends(get_current_user),
):
    if not current_user.mlbb_game_id:
        raise HTTPException(status_code=404, detail="No MLBB account linked")

    client = get_academy_client()
    profile = await client.fetch_player_profile(
        current_user.mlbb_game_id, current_user.mlbb_server_id,
    )
    return PlayerProfile(
        game_id=current_user.mlbb_game_id,
        server_id=current_user.mlbb_server_id,
        **(profile or {}),
    )


@router.post("/me/sync")
async def sync_matches(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Trigger a sync of match history from MLBB Academy."""
    if not current_user.mlbb_game_id:
        raise HTTPException(status_code=404, detail="No MLBB account linked")

    client = get_academy_client()
    matches = await client.fetch_match_history(
        current_user.mlbb_game_id, current_user.mlbb_server_id,
    )

    synced = 0
    for match_data in matches:
        match = Match(
            user_id=current_user.id,
            source="mlbb_academy",
            match_type=match_data.get("match_type", "ranked"),
            result=match_data.get("result", "win"),
            hero_played=match_data.get("hero_played", "Unknown"),
            kills=match_data.get("kills", 0),
            deaths=match_data.get("deaths", 0),
            assists=match_data.get("assists", 0),
            raw_data=match_data,
        )
        db.add(match)
        synced += 1

    await db.commit()
    return SyncStatusResponse(status="completed", matches_synced=synced)
```

**Step 4: Mount players router in `app/main.py`**

```python
from app.api.v1.players import router as players_router
app.include_router(players_router, prefix="/api/v1")
```

**Step 5: Write test `tests/test_mlbb_academy.py`**

```python
import pytest
from app.services.mlbb_academy.client import MLBBAcademyClient


@pytest.mark.asyncio
async def test_request_verification():
    client = MLBBAcademyClient()
    result = await client.request_verification("123456789", "5001")
    assert result["status"] == "verification_sent"
    assert result["game_id"] == "123456789"
    await client.close()


@pytest.mark.asyncio
async def test_verify_and_login():
    client = MLBBAcademyClient()
    result = await client.verify_and_login("123456789", "5001", "000000")
    assert result["status"] == "verified"
    await client.close()
```

**Step 6: Run tests**

Run: `cd /workspace/Test-AI-Matchmaking && python -m pytest tests/test_mlbb_academy.py -v`
Expected: 2 tests PASS

**Step 7: Commit**

```bash
git add -A
git commit -m "feat: add MLBB Academy integration service

Add account linking flow (game ID + server ID + verification code),
player profile endpoint, and match sync. Academy API calls are
stubbed with TODOs — real endpoints to be reverse-engineered."
```

---

## Task 6: React Frontend Setup with Vite + TypeScript + i18n

**Files:**
- Create: `frontend/` — Full React app scaffolded with Vite
- Key files: `package.json`, `vite.config.ts`, `src/App.tsx`, `src/lib/api.ts`, `src/lib/auth.ts`, `src/lib/i18n.ts`
- Pages: `Login.tsx`, `Dashboard.tsx`, `Chat.tsx`
- Locales: `src/locales/en.json`, `src/locales/my.json`

**Step 1: Remove old frontend**

```bash
rm -rf frontend/index.html
```

**Step 2: Scaffold React app with Vite**

```bash
cd /workspace/Test-AI-Matchmaking
npm create vite@latest frontend -- --template react-ts
cd frontend
npm install
npm install react-router-dom@6 react-i18next i18next axios recharts
npm install -D @types/node tailwindcss @tailwindcss/vite
```

**Step 3: Configure Vite**

Write `frontend/vite.config.ts`:
```typescript
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

export default defineConfig({
  plugins: [react(), tailwindcss()],
  server: {
    port: 3000,
    proxy: {
      '/api': 'http://localhost:8000',
    },
  },
})
```

**Step 4: Write `frontend/src/lib/api.ts`**

```typescript
import axios from 'axios';

const api = axios.create({
  baseURL: '/api/v1',
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export default api;
```

**Step 5: Write `frontend/src/lib/auth.ts`**

```typescript
import api from './api';

export async function register(email: string, username: string, password: string, language: string = 'my') {
  const res = await api.post('/auth/register', { email, username, password, language });
  localStorage.setItem('token', res.data.access_token);
  return res.data;
}

export async function login(email: string, password: string) {
  const res = await api.post('/auth/login', { email, password });
  localStorage.setItem('token', res.data.access_token);
  return res.data;
}

export async function getMe() {
  const res = await api.get('/auth/me');
  return res.data;
}

export function logout() {
  localStorage.removeItem('token');
  window.location.href = '/login';
}

export function isAuthenticated(): boolean {
  return !!localStorage.getItem('token');
}
```

**Step 6: Write i18n setup — `frontend/src/lib/i18n.ts`**

```typescript
import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import en from '../locales/en.json';
import my from '../locales/my.json';

i18n.use(initReactI18next).init({
  resources: {
    en: { translation: en },
    my: { translation: my },
  },
  lng: localStorage.getItem('lang') || 'my',
  fallbackLng: 'en',
  interpolation: { escapeValue: false },
});

export default i18n;
```

**Step 7: Write locale files**

`frontend/src/locales/en.json`:
```json
{
  "app_name": "MLBB AI Coach",
  "login": "Login",
  "register": "Register",
  "email": "Email",
  "username": "Username",
  "password": "Password",
  "submit": "Submit",
  "dashboard": "Dashboard",
  "chat": "AI Coach Chat",
  "heroes": "Heroes",
  "profile": "Profile",
  "team": "Team",
  "logout": "Logout",
  "welcome": "Welcome to MLBB AI Coach!",
  "ask_anything": "Ask me anything about Mobile Legends",
  "send": "Send",
  "loading": "Thinking...",
  "no_account": "Don't have an account?",
  "have_account": "Already have an account?",
  "language": "Language",
  "link_account": "Link MLBB Account",
  "game_id": "Game ID",
  "server_id": "Server ID",
  "verification_code": "Verification Code",
  "sync_matches": "Sync Matches"
}
```

`frontend/src/locales/my.json`:
```json
{
  "app_name": "MLBB AI နည်းပြ",
  "login": "ဝင်ရောက်ရန်",
  "register": "စာရင်းသွင်းရန်",
  "email": "အီးမေးလ်",
  "username": "အသုံးပြုသူအမည်",
  "password": "စကားဝှက်",
  "submit": "တင်သွင်းရန်",
  "dashboard": "ဒက်ရှ်ဘုတ်",
  "chat": "AI နည်းပြ ချက်တင်",
  "heroes": "သူရဲကောင်းများ",
  "profile": "ကိုယ်ရေးအချက်အလက်",
  "team": "အသင်း",
  "logout": "ထွက်ရန်",
  "welcome": "MLBB AI နည်းပြ မှ ကြိုဆိုပါသည်!",
  "ask_anything": "Mobile Legends အကြောင်း ဘာမဆို မေးပါ",
  "send": "ပို့ရန်",
  "loading": "စဉ်းစားနေသည်...",
  "no_account": "အကောင့်မရှိသေးဘူးလား?",
  "have_account": "အကောင့်ရှိပြီးသားလား?",
  "language": "ဘာသာစကား",
  "link_account": "MLBB အကောင့်ချိတ်ဆက်ရန်",
  "game_id": "ဂိမ်းအိုင်ဒီ",
  "server_id": "ဆာဗာအိုင်ဒီ",
  "verification_code": "အတည်ပြုကုဒ်",
  "sync_matches": "ပွဲစဉ်များ ချိန်ကိုက်ရန်"
}
```

**Step 8: Write Login page — `frontend/src/pages/Login.tsx`**

```tsx
import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useNavigate } from 'react-router-dom';
import { login, register } from '../lib/auth';

export default function Login() {
  const { t, i18n } = useTranslation();
  const navigate = useNavigate();
  const [isRegister, setIsRegister] = useState(false);
  const [email, setEmail] = useState('');
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    try {
      if (isRegister) {
        await register(email, username, password, i18n.language);
      } else {
        await login(email, password);
      }
      navigate('/');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'An error occurred');
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-indigo-500 to-purple-600 p-4">
      <div className="bg-white rounded-2xl shadow-xl p-8 w-full max-w-md">
        <h1 className="text-2xl font-bold text-center mb-6">{t('app_name')}</h1>

        <div className="flex justify-end mb-4">
          <select
            value={i18n.language}
            onChange={(e) => { i18n.changeLanguage(e.target.value); localStorage.setItem('lang', e.target.value); }}
            className="text-sm border rounded px-2 py-1"
          >
            <option value="my">မြန်မာ</option>
            <option value="en">English</option>
          </select>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <input type="email" placeholder={t('email')} value={email} onChange={e => setEmail(e.target.value)}
            className="w-full border rounded-lg px-4 py-3 focus:outline-none focus:ring-2 focus:ring-indigo-500" required />
          {isRegister && (
            <input type="text" placeholder={t('username')} value={username} onChange={e => setUsername(e.target.value)}
              className="w-full border rounded-lg px-4 py-3 focus:outline-none focus:ring-2 focus:ring-indigo-500" required />
          )}
          <input type="password" placeholder={t('password')} value={password} onChange={e => setPassword(e.target.value)}
            className="w-full border rounded-lg px-4 py-3 focus:outline-none focus:ring-2 focus:ring-indigo-500" required />
          {error && <p className="text-red-500 text-sm">{error}</p>}
          <button type="submit"
            className="w-full bg-gradient-to-r from-indigo-500 to-purple-600 text-white rounded-lg py-3 font-semibold hover:opacity-90">
            {isRegister ? t('register') : t('login')}
          </button>
        </form>

        <p className="text-center mt-4 text-sm text-gray-600 cursor-pointer" onClick={() => setIsRegister(!isRegister)}>
          {isRegister ? t('have_account') : t('no_account')}
        </p>
      </div>
    </div>
  );
}
```

**Step 9: Write Dashboard page — `frontend/src/pages/Dashboard.tsx`**

```tsx
import { useTranslation } from 'react-i18next';
import { Link } from 'react-router-dom';
import { logout } from '../lib/auth';

export default function Dashboard() {
  const { t, i18n } = useTranslation();

  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-gradient-to-r from-indigo-500 to-purple-600 text-white px-6 py-4 flex justify-between items-center">
        <h1 className="text-xl font-bold">{t('app_name')}</h1>
        <div className="flex items-center gap-4">
          <select value={i18n.language} onChange={e => { i18n.changeLanguage(e.target.value); localStorage.setItem('lang', e.target.value); }}
            className="bg-white/20 border border-white/30 rounded px-2 py-1 text-sm">
            <option value="my">မြန်မာ</option>
            <option value="en">English</option>
          </select>
          <button onClick={logout} className="text-sm hover:underline">{t('logout')}</button>
        </div>
      </nav>

      <div className="max-w-4xl mx-auto p-6 grid grid-cols-1 md:grid-cols-2 gap-6 mt-8">
        <Link to="/chat" className="bg-white rounded-xl shadow-md p-6 hover:shadow-lg transition">
          <h2 className="text-lg font-semibold text-indigo-600">🎮 {t('chat')}</h2>
          <p className="text-gray-500 mt-2">{t('ask_anything')}</p>
        </Link>
        <Link to="/profile" className="bg-white rounded-xl shadow-md p-6 hover:shadow-lg transition">
          <h2 className="text-lg font-semibold text-indigo-600">👤 {t('profile')}</h2>
          <p className="text-gray-500 mt-2">{t('link_account')}</p>
        </Link>
      </div>
    </div>
  );
}
```

**Step 10: Write Chat page — `frontend/src/pages/Chat.tsx`**

Port the existing chat UI from the old `index.html` into React:

```tsx
import { useState, useRef, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { Link } from 'react-router-dom';
import api from '../lib/api';

interface Message {
  role: 'user' | 'assistant';
  content: string;
  suggestions?: string[];
}

export default function Chat() {
  const { t } = useTranslation();
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [provider, setProvider] = useState('gemini');
  const [sessionId, setSessionId] = useState<string | null>(null);
  const chatRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    chatRef.current?.scrollTo(0, chatRef.current.scrollHeight);
  }, [messages]);

  const send = async (message?: string) => {
    const text = message || input.trim();
    if (!text) return;
    setInput('');
    setMessages(prev => [...prev, { role: 'user', content: text }]);
    setLoading(true);

    try {
      const res = await api.post('/chat/', {
        message: text,
        session_id: sessionId,
        llm_provider: provider,
      });
      setSessionId(res.data.session_id);
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: res.data.response,
        suggestions: res.data.suggestions,
      }]);
    } catch (err: any) {
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: err.response?.data?.detail || 'Error occurred',
      }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-screen bg-gray-50">
      <nav className="bg-gradient-to-r from-indigo-500 to-purple-600 text-white px-6 py-4 flex justify-between items-center">
        <Link to="/" className="text-xl font-bold">{t('app_name')}</Link>
        <select value={provider} onChange={e => setProvider(e.target.value)}
          className="bg-white/20 border border-white/30 rounded px-3 py-1 text-sm">
          <option value="gemini">Gemini</option>
          <option value="claude">Claude</option>
        </select>
      </nav>

      <div ref={chatRef} className="flex-1 overflow-y-auto p-6 space-y-4">
        {messages.length === 0 && (
          <div className="text-center text-gray-400 mt-20">
            <p className="text-lg">{t('welcome')}</p>
            <p>{t('ask_anything')}</p>
          </div>
        )}
        {messages.map((msg, i) => (
          <div key={i} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div className={`max-w-[70%] rounded-2xl px-5 py-3 ${
              msg.role === 'user'
                ? 'bg-gradient-to-r from-indigo-500 to-purple-600 text-white'
                : 'bg-white border shadow-sm'
            }`}>
              <p className="whitespace-pre-wrap">{msg.content}</p>
              {msg.suggestions && (
                <div className="flex flex-wrap gap-2 mt-3">
                  {msg.suggestions.map((s, j) => (
                    <button key={j} onClick={() => send(s)}
                      className="text-xs border border-indigo-400 text-indigo-600 rounded-full px-3 py-1 hover:bg-indigo-50">
                      {s}
                    </button>
                  ))}
                </div>
              )}
            </div>
          </div>
        ))}
        {loading && (
          <div className="flex justify-start">
            <div className="bg-white border shadow-sm rounded-2xl px-5 py-3 text-gray-400">
              {t('loading')}
            </div>
          </div>
        )}
      </div>

      <div className="border-t bg-white px-6 py-4 flex gap-3">
        <input value={input} onChange={e => setInput(e.target.value)}
          onKeyDown={e => e.key === 'Enter' && send()}
          placeholder={t('ask_anything')}
          className="flex-1 border rounded-full px-5 py-3 focus:outline-none focus:ring-2 focus:ring-indigo-500" />
        <button onClick={() => send()} disabled={loading}
          className="bg-gradient-to-r from-indigo-500 to-purple-600 text-white rounded-full px-8 py-3 font-semibold hover:opacity-90 disabled:opacity-50">
          {t('send')}
        </button>
      </div>
    </div>
  );
}
```

**Step 11: Write `frontend/src/App.tsx`**

```tsx
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { isAuthenticated } from './lib/auth';
import './lib/i18n';
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import Chat from './pages/Chat';

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  return isAuthenticated() ? <>{children}</> : <Navigate to="/login" />;
}

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/" element={<ProtectedRoute><Dashboard /></ProtectedRoute>} />
        <Route path="/chat" element={<ProtectedRoute><Chat /></ProtectedRoute>} />
      </Routes>
    </BrowserRouter>
  );
}
```

**Step 12: Add Tailwind CSS import**

Write `frontend/src/index.css`:
```css
@import "tailwindcss";
```

**Step 13: Verify frontend builds**

Run: `cd /workspace/Test-AI-Matchmaking/frontend && npm run build`
Expected: Build succeeds, output in `dist/`

**Step 14: Commit**

```bash
git add -A
git commit -m "feat: add React frontend with Vite, TypeScript, and Burmese i18n

Login/register flow, dashboard, AI coaching chat page.
Tailwind CSS styling. Burmese + English translations.
Axios API client with JWT auth interceptor."
```

---

## Task 7: Update Documentation and Configuration

**Files:**
- Modify: `README.md` — Update for SaaS product
- Modify: `.env.example` — Add new config vars
- Modify: `requirements.txt` — Add `aiosqlite`
- Modify: `.gitignore` — Add `frontend/node_modules`, `frontend/dist`
- Modify: `docker-compose.yml` — Update for new structure

**Step 1: Update `.gitignore`**

Append:
```
# Frontend
frontend/node_modules/
frontend/dist/
frontend/.vite/
```

**Step 2: Update `.env.example`**

Add under PostgreSQL section:
```
DATABASE_URL=postgresql+asyncpg://mlbb_user:password@localhost:5432/mlbb_coach
```

**Step 3: Update `requirements.txt`**

Add:
```
aiosqlite==0.20.0
```

**Step 4: Update `README.md`**

Rewrite to reflect the SaaS product — MLBB AI Coach for Myanmar market, free solo + paid team tiers, with the new architecture. Reference the design doc at `docs/plans/2026-02-24-mlbb-saas-coach-design.md`.

**Step 5: Commit**

```bash
git add -A
git commit -m "docs: update README, .env.example, and .gitignore for SaaS architecture

Add frontend build artifacts to gitignore, update env template
with DATABASE_URL, add aiosqlite test dependency."
```

---

## Summary of All Tasks

| Task | Description | Files | Tests |
|------|-------------|-------|-------|
| 1 | Project restructure — new directories | 10+ new dirs/files | Import check |
| 2 | PostgreSQL models + Alembic | 8 model files + alembic | `test_db.py` (2 tests) |
| 3 | JWT authentication | security, deps, auth router | `test_auth.py` (4 tests) |
| 4 | Port chat to v1 with auth | v1/chat.py, v1/heroes.py | Import check |
| 5 | MLBB Academy integration | academy client, players router | `test_mlbb_academy.py` (2 tests) |
| 6 | React frontend + i18n | Full React app, 3 pages, 2 locales | `npm run build` |
| 7 | Docs and config updates | README, .env, .gitignore | N/A |

**Total commits: 7**
**Total test files: 4**
**Total tests: 8+**
