from typing import TypedDict, Annotated, Sequence, Optional, Literal
from langgraph.graph import StateGraph, END
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate
import operator
import logging
from app.services.llm.provider import LLMFactory
from app.services.rag.retriever import HeroRetriever, BuildRetriever, StrategyRetriever
from app.models.schemas import LLMProvider

logger = logging.getLogger(__name__)


def _extract_text(response) -> str:
    """Safely extract text content from an LLM response."""
    content = response.content
    if isinstance(content, list):
        # Gemini returns content as a list of parts
        parts = []
        for part in content:
            if isinstance(part, str):
                parts.append(part)
            elif isinstance(part, dict) and "text" in part:
                parts.append(part["text"])
        return " ".join(parts)
    return str(content)


class CoachingState(TypedDict):
    """State for the coaching conversation graph."""
    messages: Annotated[Sequence[BaseMessage], operator.add]
    user_query: str
    intent: Optional[str]  # hero_info, build_recommendation, matchup_analysis, general_strategy
    hero_context: Optional[str]
    build_context: Optional[str]
    strategy_context: Optional[str]
    llm_provider: Optional[LLMProvider]
    language: Optional[str]
    response: Optional[str]


class MLBBCoachingGraph:
    """LangGraph workflow for MLBB coaching conversations."""

    def __init__(self, llm_provider: Optional[LLMProvider] = None):
        self.llm_provider = llm_provider
        self.hero_retriever = HeroRetriever(llm_provider)
        self.build_retriever = BuildRetriever(llm_provider)
        self.strategy_retriever = StrategyRetriever(llm_provider)
        self.graph = self._build_graph()

    def _classify_intent(self, state: CoachingState) -> CoachingState:
        """Classify the user's intent from their query."""
        user_query = state["user_query"]

        # Use LLM to classify intent
        llm = LLMFactory.get_model(
            provider=state.get("llm_provider") or self.llm_provider,
            temperature=0.1
        )

        classification_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an intent classifier for an MLBB coaching system.
Classify the user's query into ONE of these categories:

1. hero_info - Questions about specific heroes, their abilities, roles, or general info
2. build_recommendation - Questions about items, builds, emblems, or equipment
3. matchup_analysis - Questions about counters, how to play against specific heroes
4. general_strategy - Questions about gameplay, positioning, team fights, meta, tactics
5. general_chat - Greetings, thanks, or non-MLBB related queries

Respond with ONLY the category name, nothing else."""),
            ("user", "{query}")
        ])

        chain = classification_prompt | llm
        intent = _extract_text(chain.invoke({"query": user_query})).strip().lower()

        # Validate intent
        valid_intents = ["hero_info", "build_recommendation", "matchup_analysis", "general_strategy", "general_chat"]
        if intent not in valid_intents:
            intent = "general_strategy"

        state["intent"] = intent
        return state

    def _retrieve_hero_context(self, state: CoachingState) -> CoachingState:
        """Retrieve hero-related context."""
        if state["intent"] in ["hero_info", "matchup_analysis"]:
            docs = self.hero_retriever.retrieve_context(state["user_query"], k=3)
            state["hero_context"] = self.hero_retriever.format_documents(docs)
        return state

    def _retrieve_build_context(self, state: CoachingState) -> CoachingState:
        """Retrieve build-related context."""
        if state["intent"] == "build_recommendation":
            docs = self.build_retriever.retrieve_context(state["user_query"], k=3)
            state["build_context"] = self.build_retriever.format_documents(docs)
        return state

    def _retrieve_strategy_context(self, state: CoachingState) -> CoachingState:
        """Retrieve strategy-related context."""
        if state["intent"] in ["general_strategy", "matchup_analysis"]:
            docs = self.strategy_retriever.retrieve_context(state["user_query"], k=5)
            state["strategy_context"] = self.strategy_retriever.format_documents(docs)
        return state

    def _generate_response(self, state: CoachingState) -> CoachingState:
        """Generate the coaching response using retrieved context."""
        llm = LLMFactory.get_model(
            provider=state.get("llm_provider") or self.llm_provider,
            temperature=0.7
        )

        # Build context from retrieved information
        context_parts = []
        if state.get("hero_context"):
            context_parts.append(f"Hero Information:\n{state['hero_context']}")
        if state.get("build_context"):
            context_parts.append(f"Build Information:\n{state['build_context']}")
        if state.get("strategy_context"):
            context_parts.append(f"Strategy Information:\n{state['strategy_context']}")

        context = "\n\n".join(context_parts) if context_parts else "No specific context available."

        # Create system prompt based on intent
        intent_prompts = {
            "hero_info": """You are an expert MLBB coach specializing in hero knowledge.
Provide detailed, accurate information about heroes, their abilities, roles, and playstyles.
Be specific and reference game mechanics when relevant.""",

            "build_recommendation": """You are an expert MLBB coach specializing in item builds.
Recommend optimal item builds, emblems, and battle spells.
Explain the reasoning behind each recommendation and when to adapt builds.""",

            "matchup_analysis": """You are an expert MLBB coach specializing in matchup analysis.
Provide detailed counter strategies, positioning tips, and win conditions.
Be specific about power spikes, itemization adjustments, and gameplay tactics.""",

            "general_strategy": """You are an expert MLBB coach providing strategic guidance.
Give actionable advice on gameplay, positioning, objectives, and team coordination.
Focus on practical tips that players can immediately apply.""",

            "general_chat": """You are a friendly MLBB coach assistant.
Respond naturally to greetings and general conversation while staying in character."""
        }

        system_prompt = intent_prompts.get(state["intent"], intent_prompts["general_strategy"])

        # Language instruction based on user preference
        language = state.get("language") or "en"
        if language == "my":
            language_instruction = "\n- IMPORTANT: You MUST respond entirely in Burmese (Myanmar language). Use Burmese script for all text. Hero names, item names, and game terms can remain in English."
        else:
            language_instruction = ""

        # Build the prompt
        prompt = ChatPromptTemplate.from_messages([
            ("system", f"""{system_prompt}

Use the following context to inform your response:

{context}

Important guidelines:
- Be concise but thorough
- Use bullet points for lists
- Mention specific hero names, items, and game mechanics
- If context is insufficient, use your general MLBB knowledge
- For Marksman (MM) role, be especially detailed
- Always be encouraging and constructive{language_instruction}"""),
            ("user", "{query}")
        ])

        chain = prompt | llm
        response = chain.invoke({"query": state["user_query"]})

        response_text = _extract_text(response)
        state["response"] = response_text
        state["messages"].append(AIMessage(content=response_text))

        return state

    def _should_retrieve(self, state: CoachingState) -> Literal["retrieve", "respond"]:
        """Decide whether to retrieve context or respond directly."""
        intent = state.get("intent")

        # For general chat, skip retrieval
        if intent == "general_chat":
            return "respond"

        return "retrieve"

    def _build_graph(self) -> StateGraph:
        """Build the coaching conversation graph."""
        workflow = StateGraph(CoachingState)

        # Add nodes
        workflow.add_node("classify_intent", self._classify_intent)
        workflow.add_node("retrieve_hero", self._retrieve_hero_context)
        workflow.add_node("retrieve_build", self._retrieve_build_context)
        workflow.add_node("retrieve_strategy", self._retrieve_strategy_context)
        workflow.add_node("generate_response", self._generate_response)

        # Define the flow
        workflow.set_entry_point("classify_intent")

        # After classification, retrieve all relevant contexts in parallel
        workflow.add_edge("classify_intent", "retrieve_hero")
        workflow.add_edge("retrieve_hero", "retrieve_build")
        workflow.add_edge("retrieve_build", "retrieve_strategy")
        workflow.add_edge("retrieve_strategy", "generate_response")

        # End after generation
        workflow.add_edge("generate_response", END)

        return workflow.compile()

    def process_message(
        self,
        user_message: str,
        conversation_history: Optional[list[BaseMessage]] = None,
        llm_provider: Optional[LLMProvider] = None,
        language: Optional[str] = None,
    ) -> dict:
        """
        Process a user message through the coaching graph.

        Args:
            user_message: The user's message.
            conversation_history: Previous conversation messages.
            llm_provider: Optional LLM provider to use.
            language: User's preferred language code (e.g. "my" for Burmese).

        Returns:
            Dictionary with response and metadata.
        """
        initial_state = {
            "messages": conversation_history or [],
            "user_query": user_message,
            "intent": None,
            "hero_context": None,
            "build_context": None,
            "strategy_context": None,
            "llm_provider": llm_provider or self.llm_provider,
            "language": language,
            "response": None
        }

        # Add user message
        initial_state["messages"].append(HumanMessage(content=user_message))

        # Run the graph
        result = self.graph.invoke(initial_state)

        return {
            "response": result["response"],
            "intent": result["intent"],
            "sources": {
                "hero_context": result.get("hero_context"),
                "build_context": result.get("build_context"),
                "strategy_context": result.get("strategy_context")
            }
        }
