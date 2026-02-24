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
