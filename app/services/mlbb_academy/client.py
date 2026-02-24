"""MLBB Academy client — facade for validator and meta data services.

The old stubbed methods (request_verification, verify_and_login, etc.)
have been replaced with real API integrations:
  - validator.py: Player ID validation via moogold → Moonton
  - meta_client.py: Hero meta data via Moonton GMS Academy API
"""

from app.services.mlbb_academy.validator import validate_mlbb_account, ValidationResult
from app.services.mlbb_academy.meta_client import MLBBMetaClient, get_meta_client

__all__ = [
    "validate_mlbb_account",
    "ValidationResult",
    "MLBBMetaClient",
    "get_meta_client",
]
