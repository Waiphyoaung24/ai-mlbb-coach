from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.db.user import User
from app.models.schemas.player import (
    ValidateAccountRequest,
    ValidateAccountResponse,
    ConfirmLinkRequest,
    PlayerProfile,
)
from app.services.mlbb_academy.validator import validate_mlbb_account

router = APIRouter(prefix="/players", tags=["players"])


@router.post("/validate-account", response_model=ValidateAccountResponse)
async def validate_account(
    request: ValidateAccountRequest,
    current_user: User = Depends(get_current_user),
):
    """Step 1: Validate MLBB Game ID + Zone ID and return the in-game username."""
    result = await validate_mlbb_account(request.game_id, request.server_id)

    return ValidateAccountResponse(
        valid=result.valid,
        game_id=result.game_id,
        server_id=result.server_id,
        username=result.username,
        country=result.country,
        error=result.error,
    )


@router.post("/link-account")
async def link_account(
    request: ConfirmLinkRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Step 2: Confirm and link the validated MLBB account."""
    current_user.mlbb_game_id = request.game_id
    current_user.mlbb_server_id = request.server_id
    current_user.mlbb_username = request.username
    await db.commit()

    return {
        "status": "account_linked",
        "game_id": request.game_id,
        "server_id": request.server_id,
        "username": request.username,
        "message": "MLBB account linked successfully!",
    }


@router.get("/me/profile", response_model=PlayerProfile)
async def get_profile(
    current_user: User = Depends(get_current_user),
):
    if not current_user.mlbb_game_id:
        raise HTTPException(status_code=404, detail="No MLBB account linked")

    return PlayerProfile(
        game_id=current_user.mlbb_game_id,
        server_id=current_user.mlbb_server_id,
        username=current_user.mlbb_username,
    )
