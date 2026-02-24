import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from app.core.database import Base, get_db
from app.main import app


@pytest_asyncio.fixture
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


@pytest_asyncio.fixture
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
