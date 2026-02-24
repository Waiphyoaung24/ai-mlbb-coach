import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from app.core.database import Base
from app.models.db import User, UserTier, Team, TeamMember, TeamMemberRole


@pytest_asyncio.fixture
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
