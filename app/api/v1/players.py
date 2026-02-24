from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
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
