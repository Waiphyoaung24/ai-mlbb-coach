from fastapi import APIRouter, HTTPException, Depends
from typing import Optional, List
from datetime import datetime
import uuid
import logging

from app.models.schemas import (
    ChatRequest, ChatResponse, MatchupRequest, MatchupAnalysis,
    BuildRequest, BuildRecommendation, HeroQueryRequest, Hero,
    HealthResponse, LLMProvider
)
from app.services.langgraph.coaching_graph import MLBBCoachingGraph, _extract_text
from app.services.rag.retriever import HeroRetriever, BuildRetriever
from app.services.llm.provider import LLMFactory
from app.core.config import get_settings

logger = logging.getLogger(__name__)

router = APIRouter()

# In-memory session storage (replace with Redis in production)
sessions = {}


def _check_provider_available(llm_provider: Optional[LLMProvider] = None):
    """Validate that the requested LLM provider is available before processing."""
    available = LLMFactory.list_available_providers()
    if not available:
        raise HTTPException(
            status_code=503,
            detail=(
                "No LLM providers are configured. "
                "Please set valid API keys in your .env file: "
                "ANTHROPIC_API_KEY for Claude, GOOGLE_API_KEY for Gemini."
            )
        )
    if llm_provider and llm_provider not in available:
        raise HTTPException(
            status_code=400,
            detail=(
                f"LLM provider '{llm_provider.value}' is not available. "
                f"Available providers: {[p.value for p in available]}. "
                f"Check that the API key for '{llm_provider.value}' is set in .env."
            )
        )


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    settings = get_settings()

    # Check available LLM providers
    available_providers = LLMFactory.list_available_providers()

    services_status = {
        "llm_providers": len(available_providers) > 0,
        "vector_store": settings.PINECONE_API_KEY is not None,
        "api": True
    }

    return HealthResponse(
        status="healthy" if all(services_status.values()) else "degraded",
        version="1.0.0",
        timestamp=datetime.utcnow(),
        services=services_status
    )


@router.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Main coaching chat endpoint.
    Processes user messages through LangGraph workflow.
    """
    # Validate provider before doing any work
    _check_provider_available(request.llm_provider)

    try:
        # Get or create session
        session_id = request.session_id or str(uuid.uuid4())

        if session_id not in sessions:
            sessions[session_id] = []

        conversation_history = sessions[session_id]

        # Initialize coaching graph
        graph = MLBBCoachingGraph(llm_provider=request.llm_provider)

        # Process message
        result = graph.process_message(
            user_message=request.message,
            conversation_history=conversation_history,
            llm_provider=request.llm_provider,
            language=getattr(request, 'language', None),
        )

        # Update session
        sessions[session_id] = conversation_history

        # Generate suggestions based on intent
        suggestions = generate_suggestions(result["intent"])

        return ChatResponse(
            response=result["response"],
            session_id=session_id,
            sources=[
                {"type": k, "content": v[:200] + "..." if v and len(v) > 200 else v}
                for k, v in result["sources"].items()
                if v
            ] if result["sources"] else None,
            suggestions=suggestions
        )

    except HTTPException:
        raise
    except ValueError as e:
        logger.error(f"Configuration error in chat: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Chat error: {error_msg}")
        if "authentication" in error_msg.lower() or "api key" in error_msg.lower():
            raise HTTPException(
                status_code=401,
                detail="Invalid API key. Please check your API key in the .env file."
            )
        raise HTTPException(status_code=500, detail=error_msg)


@router.post("/api/matchup/analyze", response_model=MatchupAnalysis)
async def analyze_matchup(request: MatchupRequest):
    """
    Analyze matchup between two heroes.
    """
    _check_provider_available(request.llm_provider)

    try:
        hero_retriever = HeroRetriever(llm_provider=request.llm_provider)

        # Retrieve matchup information
        matchup_docs = hero_retriever.retrieve_matchup_info(
            hero1=request.your_hero,
            hero2=request.enemy_hero,
            k=5
        )

        # Generate analysis using LLM
        llm = LLMFactory.get_model(
            provider=request.llm_provider,
            temperature=0.5
        )

        context = hero_retriever.format_documents(matchup_docs)

        prompt = f"""Analyze the matchup between {request.your_hero} and {request.enemy_hero}.

Context:
{context}

Provide:
1. Matchup difficulty (Easy/Medium/Hard)
2. 3-5 key points about the matchup
3. 3-5 specific tips for {request.your_hero}
4. Item adjustments to consider
5. Win conditions

Format your response as JSON with these keys: difficulty, key_points, tips, item_adjustments, win_conditions"""

        response = llm.invoke(prompt)

        # Parse response (simplified - in production, use structured output)
        return MatchupAnalysis(
            your_hero=request.your_hero,
            enemy_hero=request.enemy_hero,
            lane=request.lane,
            difficulty="Medium",
            key_points=[
                f"Analysis based on matchup data for {request.your_hero} vs {request.enemy_hero}"
            ],
            tips=[
                "Check the detailed coaching chat for specific tips",
                "Consider your power spikes carefully"
            ],
            item_adjustments=["Adjust based on game situation"],
            win_conditions=[f"Outscale {request.enemy_hero} in late game"]
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Matchup analysis error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api/builds/recommend", response_model=BuildRecommendation)
async def recommend_build(request: BuildRequest):
    """
    Recommend build for a hero.
    """
    _check_provider_available(request.llm_provider)

    try:
        build_retriever = BuildRetriever(llm_provider=request.llm_provider)

        # Retrieve build information
        build_docs = build_retriever.retrieve_build_info(
            hero_name=request.hero_name,
            situation=request.situation,
            k=5
        )

        # Generate build recommendation
        llm = LLMFactory.get_model(
            provider=request.llm_provider,
            temperature=0.5
        )

        context = build_retriever.format_documents(build_docs)

        prompt = f"""Recommend a build for {request.hero_name}.
Situation: {request.situation or 'balanced'}
Enemy composition: {', '.join(request.enemy_composition) if request.enemy_composition else 'unknown'}

Context:
{context}

Provide a complete build recommendation including core items, situational items, boots, emblem, talents, battle spell, and playstyle."""

        response = llm.invoke(prompt)

        # Simplified response (in production, use structured output)
        return BuildRecommendation(
            hero_name=request.hero_name,
            role="Marksman",
            core_items=["Swift Boots", "Scarlet Phantom", "Berserker's Fury"],
            situational_items=["Wind of Nature", "Malefic Roar"],
            boots="Swift Boots",
            emblem="Marksman Emblem",
            emblem_talents=["Agility", "Swift", "Weakness Finder"],
            battle_spell="Flicker",
            playstyle="Farm safely and scale into late game",
            reasoning=_extract_text(response)[:200]
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Build recommendation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/heroes", response_model=List[str])
async def list_heroes(role: Optional[str] = None):
    """
    List available heroes.
    """
    # This would query your database in production
    heroes = [
        "Layla", "Miya", "Moskov", "Granger", "Bruno",
        "Beatrix", "Wanwan", "Karrie", "Claude", "Brody"
    ]

    return heroes


@router.get("/api/providers", response_model=List[str])
async def list_providers():
    """
    List available LLM providers.
    """
    providers = LLMFactory.list_available_providers()
    return [p.value for p in providers]


def generate_suggestions(intent: str) -> List[str]:
    """Generate follow-up suggestions based on intent."""
    suggestions_map = {
        "hero_info": [
            "What items should I build?",
            "How do I play this matchup?",
            "What are the best emblems?"
        ],
        "build_recommendation": [
            "When should I build defensively?",
            "What about against tanks?",
            "Best emblem for this build?"
        ],
        "matchup_analysis": [
            "How do I position in team fights?",
            "What's the power spike timing?",
            "Counter itemization advice?"
        ],
        "general_strategy": [
            "How do I farm efficiently?",
            "Team fight positioning tips?",
            "How to play from behind?"
        ]
    }

    return suggestions_map.get(intent, [
        "Tell me about a hero",
        "Recommend a build",
        "Help with a matchup"
    ])
