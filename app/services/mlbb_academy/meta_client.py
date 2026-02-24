import httpx
import logging
import time
from typing import Optional, Dict, List, Any
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)

GMS_BASE_URL = "https://api.gms.moontontech.com"

# Source IDs for different Moonton GMS endpoints
SOURCES = {
    "hero_rank_1d": "/api/gms/source/2669606/2756567",
    "hero_rank_3d": "/api/gms/source/2669606/2756568",
    "hero_rank_7d": "/api/gms/source/2669606/2756569",
    "hero_rank_15d": "/api/gms/source/2669606/2756565",
    "hero_rank_30d": "/api/gms/source/2669606/2756570",
    "hero_position": "/api/gms/source/2669606/2756564",
    "hero_skill_combo": "/api/gms/source/2669606/2674711",
    "hero_rate_7d": "/api/gms/source/2669606/2674709",
    "hero_rate_15d": "/api/gms/source/2669606/2687909",
    "hero_rate_30d": "/api/gms/source/2669606/2690860",
}

RANK_MAP = {
    "all": "101",
    "epic": "5",
    "legend": "6",
    "mythic": "7",
    "honor": "8",
    "glory": "9",
}

DAYS_SOURCE_MAP = {
    1: "hero_rank_1d",
    3: "hero_rank_3d",
    7: "hero_rank_7d",
    15: "hero_rank_15d",
    30: "hero_rank_30d",
}

# Hero ID → name mapping (127 heroes as of 2026-02)
HERO_ID_MAP = {
    127: "Lukas", 126: "Suyou", 125: "Zhuxin", 124: "Chip", 123: "Cici",
    122: "Nolan", 121: "Ixia", 120: "Arlott", 119: "Novaria", 118: "Joy",
    117: "Fredrinn", 116: "Julian", 115: "Xavier", 114: "Melissa", 113: "Yin",
    112: "Floryn", 111: "Edith", 110: "Valentina", 109: "Aamon", 108: "Aulus",
    107: "Natan", 106: "Phoveus", 105: "Beatrix", 104: "Gloo", 103: "Paquito",
    102: "Mathilda", 101: "Yve", 100: "Brody", 99: "Barats", 98: "Khaleed",
    97: "Benedetta", 96: "Luo Yi", 95: "Yu Zhong", 94: "Popol and Kupa",
    93: "Atlas", 92: "Carmilla", 91: "Cecilion", 90: "Silvanna", 89: "Wanwan",
    88: "Masha", 87: "Baxia", 86: "Lylia", 85: "Dyrroth", 84: "Ling",
    83: "X.Borg", 82: "Terizla", 81: "Esmeralda", 80: "Guinevere",
    79: "Granger", 78: "Khufra", 77: "Badang", 76: "Faramis", 75: "Kadita",
    74: "Minsitthar", 73: "Harith", 72: "Thamuz", 71: "Kimmy", 70: "Belerick",
    69: "Hanzo", 68: "Lunox", 67: "Leomord", 66: "Vale", 65: "Claude",
    64: "Aldous", 63: "Selena", 62: "Kaja", 61: "Chang'e", 60: "Hanabi",
    59: "Uranus", 58: "Martis", 57: "Valir", 56: "Gusion", 55: "Angela",
    54: "Jawhead", 53: "Lesley", 52: "Pharsa", 51: "Helcurt", 50: "Zhask",
    49: "Hylos", 48: "Diggie", 47: "Lancelot", 46: "Odette", 45: "Argus",
    44: "Grock", 43: "Irithel", 42: "Harley", 41: "Gatotkaca", 40: "Karrie",
    39: "Roger", 38: "Vexana", 37: "Lapu-Lapu", 36: "Aurora", 35: "Hilda",
    34: "Estes", 33: "Cyclops", 32: "Johnson", 31: "Moskov",
    30: "Yi Sun-shin", 29: "Ruby", 28: "Alpha", 27: "Sun", 26: "Chou",
    25: "Kagura", 24: "Natalia", 23: "Gord", 22: "Freya", 21: "Hayabusa",
    20: "Lolita", 19: "Minotaur", 18: "Layla", 17: "Fanny", 16: "Zilong",
    15: "Eudora", 14: "Rafaela", 13: "Clint", 12: "Bruno", 11: "Bane",
    10: "Franco", 9: "Akai", 8: "Karina", 7: "Alucard", 6: "Tigreal",
    5: "Nana", 4: "Alice", 3: "Saber", 2: "Balmond", 1: "Miya",
}

# Reverse map: name (lowercase) → hero_id
HERO_NAME_MAP = {name.lower(): hid for hid, name in HERO_ID_MAP.items()}


@dataclass
class CacheEntry:
    data: Any
    expires_at: float


class MLBBMetaClient:
    """Client for Moonton GMS Academy API — hero meta data."""

    def __init__(self):
        self._cache: Dict[str, CacheEntry] = {}

    def _get_cached(self, key: str) -> Optional[Any]:
        entry = self._cache.get(key)
        if entry and entry.expires_at > time.time():
            return entry.data
        return None

    def _set_cached(self, key: str, data: Any, ttl_seconds: int):
        self._cache[key] = CacheEntry(data=data, expires_at=time.time() + ttl_seconds)

    async def _post(self, source_key: str, payload: dict) -> Optional[dict]:
        path = SOURCES.get(source_key)
        if not path:
            logger.error(f"Unknown source key: {source_key}")
            return None

        url = f"{GMS_BASE_URL}{path}"
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                resp = await client.post(
                    url,
                    json=payload,
                    headers={"Content-Type": "application/json"},
                )
                resp.raise_for_status()
                data = resp.json()

            if data.get("code") != 0:
                logger.warning(f"GMS API error: {data.get('message')}")
                return None
            return data.get("data", {})

        except Exception as e:
            logger.error(f"GMS API call failed ({source_key}): {e}")
            return None

    @staticmethod
    def hero_name_to_id(hero_name: str) -> Optional[int]:
        return HERO_NAME_MAP.get(hero_name.lower())

    @staticmethod
    def hero_id_to_name(hero_id: int) -> Optional[str]:
        return HERO_ID_MAP.get(hero_id)

    async def get_hero_rankings(
        self,
        rank: str = "all",
        days: int = 7,
        sort_by: str = "win_rate",
        limit: int = 20,
    ) -> Optional[List[dict]]:
        """Get hero rankings by win/pick/ban rate for a given rank tier."""
        cache_key = f"rankings:{rank}:{days}:{sort_by}:{limit}"
        cached = self._get_cached(cache_key)
        if cached is not None:
            return cached

        sort_field_map = {
            "pick_rate": "main_hero_appearance_rate",
            "ban_rate": "main_hero_ban_rate",
            "win_rate": "main_hero_win_rate",
        }
        source_key = DAYS_SOURCE_MAP.get(days, "hero_rank_7d")
        rank_value = RANK_MAP.get(rank, "101")

        payload = {
            "pageSize": limit,
            "filters": [
                {"field": "bigrank", "operator": "eq", "value": rank_value},
                {"field": "match_type", "operator": "eq", "value": "0"},
            ],
            "sorts": [
                {
                    "data": {
                        "field": sort_field_map.get(sort_by, "main_hero_win_rate"),
                        "order": "desc",
                    },
                    "type": "sequence",
                }
            ],
            "pageIndex": 1,
            "fields": [
                "main_hero",
                "main_hero_appearance_rate",
                "main_hero_ban_rate",
                "main_hero_win_rate",
                "main_heroid",
            ],
        }

        data = await self._post(source_key, payload)
        if not data:
            return None

        records = data.get("records", [])
        results = []
        for rec in records:
            d = rec.get("data", {})
            hero_info = d.get("main_hero", {}).get("data", {})
            results.append({
                "hero_id": d.get("main_heroid"),
                "name": hero_info.get("name", HERO_ID_MAP.get(d.get("main_heroid"), "Unknown")),
                "win_rate": round(d.get("main_hero_win_rate", 0) * 100, 2),
                "pick_rate": round(d.get("main_hero_appearance_rate", 0) * 100, 2),
                "ban_rate": round(d.get("main_hero_ban_rate", 0) * 100, 2),
                "icon": hero_info.get("head"),
            })

        self._set_cached(cache_key, results, ttl_seconds=3600)
        return results

    async def get_hero_counters(
        self, hero_id: int, rank: str = "mythic"
    ) -> Optional[List[dict]]:
        """Get heroes that counter the given hero (match_type=0)."""
        cache_key = f"counters:{hero_id}:{rank}"
        cached = self._get_cached(cache_key)
        if cached is not None:
            return cached

        rank_value = RANK_MAP.get(rank, "7")
        payload = {
            "pageSize": 20,
            "filters": [
                {"field": "match_type", "operator": "eq", "value": "0"},
                {"field": "main_heroid", "operator": "eq", "value": hero_id},
                {"field": "bigrank", "operator": "eq", "value": rank_value},
            ],
            "sorts": [],
            "pageIndex": 1,
        }

        data = await self._post("hero_rank_7d", payload)
        if not data:
            return None

        records = data.get("records", [])
        results = []
        for rec in records:
            d = rec.get("data", {})
            for sub in d.get("sub_hero", []):
                results.append({
                    "hero_id": sub.get("heroid"),
                    "name": HERO_ID_MAP.get(sub.get("heroid"), "Unknown"),
                    "win_rate_against": round(sub.get("hero_win_rate", 0) * 100, 2),
                    "increase_win_rate": round(sub.get("increase_win_rate", 0) * 100, 2),
                })

        self._set_cached(cache_key, results, ttl_seconds=3600)
        return results

    async def get_hero_synergies(
        self, hero_id: int, rank: str = "mythic"
    ) -> Optional[List[dict]]:
        """Get best teammate heroes for the given hero (match_type=1)."""
        cache_key = f"synergies:{hero_id}:{rank}"
        cached = self._get_cached(cache_key)
        if cached is not None:
            return cached

        rank_value = RANK_MAP.get(rank, "7")
        payload = {
            "pageSize": 20,
            "filters": [
                {"field": "match_type", "operator": "eq", "value": "1"},
                {"field": "main_heroid", "operator": "eq", "value": hero_id},
                {"field": "bigrank", "operator": "eq", "value": rank_value},
            ],
            "sorts": [],
            "pageIndex": 1,
        }

        data = await self._post("hero_rank_7d", payload)
        if not data:
            return None

        records = data.get("records", [])
        results = []
        for rec in records:
            d = rec.get("data", {})
            for sub in d.get("sub_hero", []):
                results.append({
                    "hero_id": sub.get("heroid"),
                    "name": HERO_ID_MAP.get(sub.get("heroid"), "Unknown"),
                    "teammate_win_rate": round(sub.get("hero_win_rate", 0) * 100, 2),
                    "increase_win_rate": round(sub.get("increase_win_rate", 0) * 100, 2),
                })

        self._set_cached(cache_key, results, ttl_seconds=3600)
        return results

    async def get_hero_detail(self, hero_id: int) -> Optional[dict]:
        """Get detailed hero info (skills, stats, role, lane)."""
        cache_key = f"detail:{hero_id}"
        cached = self._get_cached(cache_key)
        if cached is not None:
            return cached

        payload = {
            "pageSize": 1,
            "filters": [
                {"field": "hero_id", "operator": "eq", "value": hero_id},
            ],
            "sorts": [],
            "pageIndex": 1,
            "object": [],
        }

        data = await self._post("hero_position", payload)
        if not data:
            return None

        records = data.get("records", [])
        if not records:
            return None

        rec = records[0].get("data", {})
        hero_data = rec.get("hero", {}) if isinstance(rec.get("hero"), dict) else {}
        inner = hero_data.get("data", {}) if isinstance(hero_data, dict) else {}

        role_map = {1: "Tank", 2: "Fighter", 3: "Assassin", 4: "Mage", 5: "Marksman", 6: "Support"}
        lane_map = {1: "EXP Lane", 2: "Mid Lane", 3: "Roam", 4: "Jungle", 5: "Gold Lane"}

        roles = [role_map.get(r) for r in inner.get("sortid", []) if role_map.get(r)]
        lanes = [lane_map.get(l) for l in inner.get("roadsort", []) if lane_map.get(l)]

        skills = []
        for skill_group in inner.get("heroskilllist", []):
            for skill in skill_group.get("skilllist", []):
                skills.append({
                    "name": skill.get("skillname"),
                    "description": skill.get("skilldesc", "").replace('<font color="fba51f">', "").replace('<font color="fb1f1f">', "").replace('<font color="a6aafb">', "").replace("</font>", ""),
                    "cooldown": skill.get("skillcd&cost"),
                })

        result = {
            "hero_id": hero_id,
            "name": inner.get("name", HERO_ID_MAP.get(hero_id, "Unknown")),
            "roles": roles,
            "lanes": lanes,
            "skills": skills,
            "difficulty": inner.get("difficulty"),
            "ability_scores": inner.get("abilityshow", []),
        }

        self._set_cached(cache_key, result, ttl_seconds=21600)
        return result

    def format_meta_context(
        self,
        hero_name: str,
        rankings: Optional[List[dict]] = None,
        counters: Optional[List[dict]] = None,
        synergies: Optional[List[dict]] = None,
    ) -> str:
        """Format meta data as text context for the LLM prompt."""
        parts = [f"\n=== LIVE META DATA FOR {hero_name.upper()} ==="]

        if rankings:
            hero_rank = next(
                (r for r in rankings if r["name"].lower() == hero_name.lower()), None
            )
            if hero_rank:
                parts.append(
                    f"Current Stats (all ranks, 7 days): "
                    f"Win Rate: {hero_rank['win_rate']}%, "
                    f"Pick Rate: {hero_rank['pick_rate']}%, "
                    f"Ban Rate: {hero_rank['ban_rate']}%"
                )

        if counters:
            top_counters = counters[:5]
            counter_lines = [
                f"  - {c['name']}: {c['win_rate_against']}% win rate against"
                for c in top_counters
            ]
            parts.append("Top Counters (Mythic rank):\n" + "\n".join(counter_lines))

        if synergies:
            top_synergies = synergies[:5]
            synergy_lines = [
                f"  - {s['name']}: {s['teammate_win_rate']}% win rate together (+{s['increase_win_rate']}%)"
                for s in top_synergies
            ]
            parts.append("Best Teammates (Mythic rank):\n" + "\n".join(synergy_lines))

        parts.append("=== END META DATA ===\n")
        return "\n".join(parts)


# Singleton
_meta_client: Optional[MLBBMetaClient] = None


def get_meta_client() -> MLBBMetaClient:
    global _meta_client
    if _meta_client is None:
        _meta_client = MLBBMetaClient()
    return _meta_client
