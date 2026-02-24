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
