import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import json
from pathlib import Path
from langchain_core.documents import Document
from app.services.rag.vector_store import get_vector_store_manager
from app.core.config import get_settings


def load_json_file(file_path: Path) -> list:
    """Load data from JSON file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def create_hero_documents(heroes_data: list) -> list[Document]:
    """Create documents from hero data."""
    documents = []

    for hero in heroes_data:
        # Main hero document
        content = f"""
Hero: {hero['name']}
Role: {hero['role']}
Difficulty: {hero['difficulty']}
Lanes: {', '.join(hero['lanes'])}
Specialty: {', '.join(hero['specialty'])}

Description:
{hero['description']}

Strengths:
{chr(10).join(f'- {s}' for s in hero['strengths'])}

Weaknesses:
{chr(10).join(f'- {w}' for w in hero['weaknesses'])}

Counters (Good Against):
{', '.join(hero['counters']) if hero['counters'] else 'General effectiveness'}

Countered By (Weak Against):
{', '.join(hero['countered_by']) if hero['countered_by'] else 'Standard threats'}

Gameplay Tips:
{chr(10).join(f'- {tip}' for tip in hero.get('gameplay_tips', []))}

Recommended Build:
Core Items: {', '.join(hero.get('build_core', []))}
Emblem: {hero.get('emblem', 'N/A')}
Battle Spell: {hero.get('battle_spell', 'N/A')}
"""

        doc = Document(
            page_content=content.strip(),
            metadata={
                "source": "hero_data",
                "hero": hero['name'],
                "role": hero['role'],
                "difficulty": hero['difficulty'],
                "type": "hero_guide"
            }
        )
        documents.append(doc)

        # Create specific documents for matchups
        if hero['countered_by']:
            for counter in hero['countered_by']:
                matchup_content = f"""
Matchup: {hero['name']} vs {counter}
Difficulty: Unfavorable for {hero['name']}

{hero['name']} is countered by {counter}.

{hero['name']} weaknesses that {counter} exploits:
{chr(10).join(f'- {w}' for w in hero['weaknesses'][:3])}

Key tips when playing {hero['name']} against {counter}:
- Play extremely safe and stay near your tower
- Ward to spot {counter} early
- Ask for ganks from teammates
- Build defensive items early
- Avoid 1v1 situations
- Farm safely and wait for team fights
"""
                matchup_doc = Document(
                    page_content=matchup_content.strip(),
                    metadata={
                        "source": "matchup_data",
                        "hero": hero['name'],
                        "enemy": counter,
                        "type": "matchup_guide",
                        "difficulty": "hard"
                    }
                )
                documents.append(matchup_doc)

    return documents


def create_item_documents(items_data: list) -> list[Document]:
    """Create documents from item data."""
    documents = []

    for item in items_data:
        content = f"""
Item: {item['name']}
Category: {item['category']}
Cost: {item['cost']} gold

Stats:
{chr(10).join(f'- {k}: {v}' for k, v in item['stats'].items())}

{f"Passive: {item['passive']}" if item.get('passive') else ""}
{f"Active: {item['active']}" if item.get('active') else ""}

Good For:
{chr(10).join(f'- {hero}' for hero in item.get('good_for', []))}

Description: {item.get('description', '')}
"""

        doc = Document(
            page_content=content.strip(),
            metadata={
                "source": "item_data",
                "item": item['name'],
                "category": item['category'],
                "cost": item['cost'],
                "type": "item_guide"
            }
        )
        documents.append(doc)

    return documents


def create_strategy_documents(strategies_data: list) -> list[Document]:
    """Create documents from strategy data."""
    documents = []

    for strategy in strategies_data:
        content = f"""
Strategy Guide: {strategy['title']}
Category: {strategy['category']}
Role: {strategy['role']}

{strategy['content']}
"""

        doc = Document(
            page_content=content.strip(),
            metadata={
                "source": "strategy_data",
                "title": strategy['title'],
                "category": strategy['category'],
                "role": strategy['role'],
                "type": "strategy_guide"
            }
        )
        documents.append(doc)

    return documents


def ingest_all_data():
    """Ingest all MLBB data into vector store."""
    print("Starting data ingestion...")

    # Get vector store manager
    vsm = get_vector_store_manager()

    # Initialize Pinecone index
    print("\nInitializing Pinecone index...")
    vsm.initialize_index(delete_if_exists=False)

    # Define data paths
    data_dir = Path(__file__).parent.parent / "app" / "data"

    # Load and ingest heroes
    print("\nIngesting hero data...")
    heroes_file = data_dir / "heroes" / "marksman_heroes.json"
    if heroes_file.exists():
        heroes_data = load_json_file(heroes_file)
        hero_docs = create_hero_documents(heroes_data)
        vsm.add_documents(hero_docs, namespace="heroes")
        print(f"✓ Ingested {len(hero_docs)} hero documents")

    # Load and ingest items
    print("\nIngesting item data...")
    items_file = data_dir / "items" / "marksman_items.json"
    if items_file.exists():
        items_data = load_json_file(items_file)
        item_docs = create_item_documents(items_data)
        vsm.add_documents(item_docs, namespace="builds")
        print(f"✓ Ingested {len(item_docs)} item documents")

    # Load and ingest strategies
    print("\nIngesting strategy data...")
    strategies_file = data_dir / "strategies" / "marksman_strategies.json"
    if strategies_file.exists():
        strategies_data = load_json_file(strategies_file)
        strategy_docs = create_strategy_documents(strategies_data)
        vsm.add_documents(strategy_docs, namespace="strategies")
        print(f"✓ Ingested {len(strategy_docs)} strategy documents")

    print("\n✅ Data ingestion complete!")
    print(f"\nTotal documents ingested:")
    print(f"- Heroes namespace: {len(hero_docs) if 'hero_docs' in locals() else 0}")
    print(f"- Builds namespace: {len(item_docs) if 'item_docs' in locals() else 0}")
    print(f"- Strategies namespace: {len(strategy_docs) if 'strategy_docs' in locals() else 0}")


if __name__ == "__main__":
    # Check if API keys are set
    settings = get_settings()

    if not settings.PINECONE_API_KEY:
        print("❌ Error: PINECONE_API_KEY not set in environment variables")
        print("Please set your Pinecone API key in .env file")
        sys.exit(1)

    ingest_all_data()
