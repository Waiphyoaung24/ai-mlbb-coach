from typing import List, Optional, Dict, Any
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from app.services.rag.vector_store import get_vector_store_manager
from app.services.llm.provider import LLMFactory
from app.models.schemas import LLMProvider


class MLBBRetriever:
    """RAG retriever for MLBB coaching knowledge."""

    def __init__(self, llm_provider: Optional[LLMProvider] = None):
        self.vector_store_manager = get_vector_store_manager()
        self.llm_provider = llm_provider

    def retrieve_context(
        self,
        query: str,
        k: int = 5,
        namespace: Optional[str] = None,
        filter: Optional[Dict[str, Any]] = None
    ) -> List[Document]:
        """
        Retrieve relevant documents for a query.

        Args:
            query: User query.
            k: Number of documents to retrieve.
            namespace: Optional namespace to search in.
            filter: Optional metadata filter.

        Returns:
            List of relevant documents.
        """
        return self.vector_store_manager.similarity_search(
            query=query,
            k=k,
            namespace=namespace,
            filter=filter
        )

    def retrieve_with_scores(
        self,
        query: str,
        k: int = 5,
        namespace: Optional[str] = None,
        filter: Optional[Dict[str, Any]] = None
    ) -> List[tuple[Document, float]]:
        """Retrieve documents with relevance scores."""
        return self.vector_store_manager.similarity_search_with_score(
            query=query,
            k=k,
            namespace=namespace,
            filter=filter
        )

    def format_documents(self, documents: List[Document]) -> str:
        """Format documents into a context string."""
        formatted_docs = []
        for i, doc in enumerate(documents, 1):
            content = doc.page_content
            metadata = doc.metadata

            # Add metadata context if available
            source_info = []
            if "source" in metadata:
                source_info.append(f"Source: {metadata['source']}")
            if "hero" in metadata:
                source_info.append(f"Hero: {metadata['hero']}")
            if "category" in metadata:
                source_info.append(f"Category: {metadata['category']}")

            header = f"\n--- Document {i} ---"
            if source_info:
                header += f"\n{', '.join(source_info)}"

            formatted_docs.append(f"{header}\n{content}\n")

        return "\n".join(formatted_docs)

    def create_rag_chain(
        self,
        prompt_template: str,
        temperature: float = 0.7
    ):
        """
        Create a RAG chain with retrieval and generation.

        Args:
            prompt_template: Prompt template string with {context} and {question} placeholders.
            temperature: LLM temperature.

        Returns:
            Runnable RAG chain.
        """
        # Get LLM
        llm = LLMFactory.get_model(
            provider=self.llm_provider,
            temperature=temperature
        )

        # Create prompt
        prompt = ChatPromptTemplate.from_template(prompt_template)

        # Define retrieval function
        def retrieve_and_format(question: str) -> str:
            docs = self.retrieve_context(question)
            return self.format_documents(docs)

        # Build chain
        chain = (
            {
                "context": lambda x: retrieve_and_format(x["question"]),
                "question": RunnablePassthrough()
            }
            | prompt
            | llm
            | StrOutputParser()
        )

        return chain

    def answer_question(
        self,
        question: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7
    ) -> str:
        """
        Answer a question using RAG.

        Args:
            question: User question.
            system_prompt: Optional system prompt to guide the response.
            temperature: LLM temperature.

        Returns:
            Generated answer.
        """
        # Retrieve relevant context
        docs = self.retrieve_context(question)
        context = self.format_documents(docs)

        # Build prompt
        default_system_prompt = """You are an expert Mobile Legends Bang Bang (MLBB) coach.
Use the provided context to answer the user's question accurately and helpfully.
If the context doesn't contain enough information, say so and provide general guidance based on your knowledge.

Focus on:
- Practical, actionable advice
- Hero-specific strategies
- Item builds and counters
- Positioning and gameplay tactics
- Meta-relevant information

Context:
{context}

Question: {question}

Answer:"""

        prompt_template = system_prompt or default_system_prompt

        # Create and run chain
        chain = self.create_rag_chain(prompt_template, temperature)

        return chain.invoke({"question": question})


class HeroRetriever(MLBBRetriever):
    """Specialized retriever for hero-related queries."""

    def __init__(self, llm_provider: Optional[LLMProvider] = None):
        super().__init__(llm_provider)
        self.namespace = "heroes"

    def retrieve_hero_info(self, hero_name: str, k: int = 3) -> List[Document]:
        """Retrieve information about a specific hero."""
        return self.retrieve_context(
            query=hero_name,
            k=k,
            namespace=self.namespace,
            filter={"hero": hero_name}
        )

    def retrieve_matchup_info(
        self,
        hero1: str,
        hero2: str,
        k: int = 3
    ) -> List[Document]:
        """Retrieve matchup information between two heroes."""
        query = f"{hero1} vs {hero2} matchup counter strategy"
        return self.retrieve_context(
            query=query,
            k=k,
            namespace=self.namespace
        )


class BuildRetriever(MLBBRetriever):
    """Specialized retriever for build recommendations."""

    def __init__(self, llm_provider: Optional[LLMProvider] = None):
        super().__init__(llm_provider)
        self.namespace = "builds"

    def retrieve_build_info(
        self,
        hero_name: str,
        situation: Optional[str] = None,
        k: int = 3
    ) -> List[Document]:
        """Retrieve build information for a hero."""
        query = f"{hero_name} build"
        if situation:
            query += f" {situation}"

        return self.retrieve_context(
            query=query,
            k=k,
            namespace=self.namespace,
            filter={"hero": hero_name} if hero_name else None
        )


class StrategyRetriever(MLBBRetriever):
    """Specialized retriever for gameplay strategies."""

    def __init__(self, llm_provider: Optional[LLMProvider] = None):
        super().__init__(llm_provider)
        self.namespace = "strategies"

    def retrieve_strategy_info(
        self,
        topic: str,
        role: Optional[str] = None,
        k: int = 5
    ) -> List[Document]:
        """Retrieve strategy information."""
        query = topic
        filter_dict = {}

        if role:
            filter_dict["role"] = role

        return self.retrieve_context(
            query=query,
            k=k,
            namespace=self.namespace,
            filter=filter_dict if filter_dict else None
        )
