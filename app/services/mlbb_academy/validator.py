import httpx
import logging
from typing import Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)

MOOGOLD_VALIDATION_URL = (
    "https://moogold.com/wp-content/plugins/id-validation-new/id-validation-ajax.php"
)

MOOGOLD_HEADERS = {
    "Referer": "https://moogold.com/product/mobile-legends/",
    "Origin": "https://moogold.com",
    "Content-Type": "application/x-www-form-urlencoded",
}

# Fixed form fields required by the moogold endpoint
MOOGOLD_FIXED_FIELDS = {
    "attribute_amount": "Weekly Pass",
    "quantity": "1",
    "add-to-cart": "15145",
    "product_id": "15145",
    "variation_id": "4690783",
}


@dataclass
class ValidationResult:
    valid: bool
    game_id: str
    server_id: str
    username: Optional[str] = None
    country: Optional[str] = None
    error: Optional[str] = None


def _parse_validation_message(message: str) -> dict:
    """Parse the newline-separated key:value message from moogold."""
    result = {}
    for line in message.strip().split("\n"):
        if ":" in line:
            key, value = line.split(":", 1)
            result[key.strip()] = value.strip()
    return result


async def validate_mlbb_account(
    game_id: str, server_id: str
) -> ValidationResult:
    """Validate an MLBB account by Game ID + Zone/Server ID.

    Calls the moogold validation API which proxies to Moonton's servers.
    Returns the in-game nickname and country if valid.
    """
    form_data = {
        **MOOGOLD_FIXED_FIELDS,
        "text-5f6f144f8ffee": game_id,
        "text-1601115253775": server_id,
    }

    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.post(
                MOOGOLD_VALIDATION_URL,
                data=form_data,
                headers=MOOGOLD_HEADERS,
            )
            resp.raise_for_status()
            data = resp.json()

        if data.get("status") != "true":
            return ValidationResult(
                valid=False,
                game_id=game_id,
                server_id=server_id,
                error="Invalid Game ID or Server ID",
            )

        parsed = _parse_validation_message(data.get("message", ""))
        username = parsed.get("In-Game Nickname")
        country = parsed.get("Country")

        if not username:
            return ValidationResult(
                valid=False,
                game_id=game_id,
                server_id=server_id,
                error="Could not retrieve username",
            )

        return ValidationResult(
            valid=True,
            game_id=game_id,
            server_id=server_id,
            username=username,
            country=country,
        )

    except httpx.HTTPStatusError as e:
        logger.error(f"Validation HTTP error: {e}")
        return ValidationResult(
            valid=False,
            game_id=game_id,
            server_id=server_id,
            error=f"Validation service error: {e.response.status_code}",
        )
    except Exception as e:
        logger.error(f"Validation error: {e}")
        return ValidationResult(
            valid=False,
            game_id=game_id,
            server_id=server_id,
            error=str(e),
        )
