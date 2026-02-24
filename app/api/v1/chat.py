from fastapi import APIRouter, Depends, HTTPException
from typing import Optional
import uuid
import logging

from app.api.deps import get_current_user
from app.models.db.user import User
from app.models.schemas.chat import ChatRequest, ChatResponse, LLMProvider
from app.services.langgraph.coaching_graph import MLBBCoachingGraph, _extract_text
from app.services.llm.provider import LLMFactory

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/chat", tags=["chat"])

# In-memory sessions (migrate to Redis later)
sessions = {}


def _check_provider(llm_provider: Optional[LLMProvider] = None):
    available = LLMFactory.list_available_providers()
    if not available:
        raise HTTPException(status_code=503, detail="No LLM providers configured.")
    if llm_provider and llm_provider not in available:
        raise HTTPException(
            status_code=400,
            detail=f"Provider '{llm_provider.value}' not available. Available: {[p.value for p in available]}",
        )


@router.post("/", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
):
    _check_provider(request.llm_provider)

    try:
        session_id = request.session_id or str(uuid.uuid4())
        if session_id not in sessions:
            sessions[session_id] = []

        graph = MLBBCoachingGraph(llm_provider=request.llm_provider)
        result = graph.process_message(
            user_message=request.message,
            conversation_history=sessions[session_id],
            llm_provider=request.llm_provider,
            language=current_user.language,
        )
        sessions[session_id] = sessions.get(session_id, [])

        return ChatResponse(
            response=result["response"],
            session_id=session_id,
            sources=None,
            suggestions=_suggestions(result["intent"]),
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


def _suggestions(intent: str):
    m = {
        "hero_info": ["What items should I build?", "How do I play this matchup?"],
        "build_recommendation": ["When should I build defensively?", "Best emblem?"],
        "matchup_analysis": ["How do I position in team fights?", "Counter items?"],
        "general_strategy": ["How do I farm efficiently?", "Team fight tips?"],
    }
    return m.get(intent, ["Tell me about a hero", "Recommend a build"])
