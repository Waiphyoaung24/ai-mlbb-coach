import httpx
import logging
from typing import Optional, Dict

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
            "username": None,
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
