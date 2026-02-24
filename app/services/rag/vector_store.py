from typing import List, Optional, Dict, Any
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_pinecone import PineconeVectorStore
from langchain_core.documents import Document
from pinecone import Pinecone, ServerlessSpec
from app.core.config import get_settings
import time


class VectorStoreManager:
    """Manages vector store operations for MLBB knowledge base."""

    def __init__(self):
        self.settings = get_settings()
        self._embeddings = None
        self._vector_store = None
        self._pinecone_client = None

    @property
    def embeddings(self) -> HuggingFaceEmbeddings:
        """Get or create embeddings model."""
        if self._embeddings is None:
            self._embeddings = HuggingFaceEmbeddings(
                model_name=self.settings.EMBEDDING_MODEL,
                model_kwargs={'device': 'cpu'},
                encode_kwargs={'normalize_embeddings': True}
            )
        return self._embeddings

    @property
    def pinecone_client(self) -> Pinecone:
        """Get or create Pinecone client."""
        if self._pinecone_client is None:
            self._pinecone_client = Pinecone(api_key=self.settings.PINECONE_API_KEY)
        return self._pinecone_client

    def initialize_index(self, delete_if_exists: bool = False):
        """
        Initialize Pinecone index.

        Args:
            delete_if_exists: If True, delete existing index before creating.
        """
        pc = self.pinecone_client
        index_name = self.settings.PINECONE_INDEX_NAME

        # Check if index exists
        existing_indexes = [index.name for index in pc.list_indexes()]

        if index_name in existing_indexes:
            if delete_if_exists:
                print(f"Deleting existing index: {index_name}")
                pc.delete_index(index_name)
            else:
                print(f"Index {index_name} already exists")
                return

        # Create new index
        print(f"Creating new index: {index_name}")
        pc.create_index(
            name=index_name,
            dimension=self.settings.EMBEDDING_DIMENSION,
            metric="cosine",
            spec=ServerlessSpec(
                cloud="aws",
                region=self.settings.PINECONE_ENVIRONMENT or "us-east-1"
            )
        )

        # Wait for index to be ready
        while not pc.describe_index(index_name).status['ready']:
            time.sleep(1)

        print(f"Index {index_name} is ready")

    @property
    def vector_store(self) -> PineconeVectorStore:
        """Get or create vector store instance."""
        if self._vector_store is None:
            self._vector_store = PineconeVectorStore(
                index_name=self.settings.PINECONE_INDEX_NAME,
                embedding=self.embeddings,
                pinecone_api_key=self.settings.PINECONE_API_KEY
            )
        return self._vector_store

    def add_documents(
        self,
        documents: List[Document],
        namespace: Optional[str] = None
    ) -> List[str]:
        """
        Add documents to vector store.

        Args:
            documents: List of documents to add.
            namespace: Optional namespace for organizing documents.

        Returns:
            List of document IDs.
        """
        return self.vector_store.add_documents(
            documents=documents,
            namespace=namespace
        )

    def similarity_search(
        self,
        query: str,
        k: int = None,
        namespace: Optional[str] = None,
        filter: Optional[Dict[str, Any]] = None
    ) -> List[Document]:
        """
        Search for similar documents.

        Args:
            query: Search query.
            k: Number of results to return.
            namespace: Optional namespace to search in.
            filter: Optional metadata filter.

        Returns:
            List of similar documents.
        """
        k = k or self.settings.RAG_TOP_K

        return self.vector_store.similarity_search(
            query=query,
            k=k,
            namespace=namespace,
            filter=filter
        )

    def similarity_search_with_score(
        self,
        query: str,
        k: int = None,
        namespace: Optional[str] = None,
        filter: Optional[Dict[str, Any]] = None
    ) -> List[tuple[Document, float]]:
        """
        Search for similar documents with relevance scores.

        Args:
            query: Search query.
            k: Number of results to return.
            namespace: Optional namespace to search in.
            filter: Optional metadata filter.

        Returns:
            List of (document, score) tuples.
        """
        k = k or self.settings.RAG_TOP_K

        results = self.vector_store.similarity_search_with_score(
            query=query,
            k=k,
            namespace=namespace,
            filter=filter
        )

        # Filter by score threshold
        threshold = self.settings.RAG_SCORE_THRESHOLD
        return [(doc, score) for doc, score in results if score >= threshold]

    def delete_namespace(self, namespace: str):
        """Delete all documents in a namespace."""
        index = self.pinecone_client.Index(self.settings.PINECONE_INDEX_NAME)
        index.delete(delete_all=True, namespace=namespace)


# Global instance
_vector_store_manager: Optional[VectorStoreManager] = None


def get_vector_store_manager() -> VectorStoreManager:
    """Get global vector store manager instance."""
    global _vector_store_manager
    if _vector_store_manager is None:
        _vector_store_manager = VectorStoreManager()
    return _vector_store_manager
