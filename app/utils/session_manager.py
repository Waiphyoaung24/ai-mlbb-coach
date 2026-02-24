from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
import json
import redis
from app.core.config import get_settings


class SessionManager:
    """Manages user sessions and conversation history."""

    def __init__(self):
        self.settings = get_settings()
        self._redis_client = None
        self._use_redis = bool(self.settings.REDIS_HOST)

        # In-memory fallback
        self._memory_store: Dict[str, List[BaseMessage]] = {}

    @property
    def redis_client(self) -> Optional[redis.Redis]:
        """Get or create Redis client."""
        if not self._use_redis:
            return None

        if self._redis_client is None:
            try:
                self._redis_client = redis.Redis(
                    host=self.settings.REDIS_HOST,
                    port=self.settings.REDIS_PORT,
                    db=self.settings.REDIS_DB,
                    password=self.settings.REDIS_PASSWORD,
                    decode_responses=True
                )
                # Test connection
                self._redis_client.ping()
            except Exception as e:
                print(f"Redis connection failed: {e}. Using in-memory storage.")
                self._use_redis = False
                return None

        return self._redis_client

    def get_session(self, session_id: str) -> List[BaseMessage]:
        """
        Get conversation history for a session.

        Args:
            session_id: Session identifier.

        Returns:
            List of conversation messages.
        """
        if self._use_redis and self.redis_client:
            try:
                data = self.redis_client.get(f"session:{session_id}")
                if data:
                    messages_data = json.loads(data)
                    return self._deserialize_messages(messages_data)
            except Exception as e:
                print(f"Redis get failed: {e}")

        # Fallback to memory
        return self._memory_store.get(session_id, [])

    def save_session(
        self,
        session_id: str,
        messages: List[BaseMessage],
        ttl_hours: int = 24
    ):
        """
        Save conversation history for a session.

        Args:
            session_id: Session identifier.
            messages: Conversation messages.
            ttl_hours: Time to live in hours.
        """
        # Limit history size
        max_history = self.settings.MAX_CONVERSATION_HISTORY
        if len(messages) > max_history:
            messages = messages[-max_history:]

        if self._use_redis and self.redis_client:
            try:
                messages_data = self._serialize_messages(messages)
                self.redis_client.setex(
                    f"session:{session_id}",
                    timedelta(hours=ttl_hours),
                    json.dumps(messages_data)
                )
                return
            except Exception as e:
                print(f"Redis save failed: {e}")

        # Fallback to memory
        self._memory_store[session_id] = messages

    def delete_session(self, session_id: str):
        """Delete a session."""
        if self._use_redis and self.redis_client:
            try:
                self.redis_client.delete(f"session:{session_id}")
            except Exception:
                pass

        # Also delete from memory
        self._memory_store.pop(session_id, None)

    def add_message(
        self,
        session_id: str,
        message: BaseMessage
    ):
        """Add a message to session history."""
        messages = self.get_session(session_id)
        messages.append(message)
        self.save_session(session_id, messages)

    def get_user_context(self, session_id: str) -> Dict[str, Any]:
        """
        Extract user context from conversation history.

        Args:
            session_id: Session identifier.

        Returns:
            Dictionary with user preferences and context.
        """
        messages = self.get_session(session_id)

        context = {
            "message_count": len(messages),
            "has_history": len(messages) > 0,
            "last_interaction": None
        }

        # Extract mentioned heroes, roles, etc.
        mentioned_heroes = set()
        mentioned_roles = set()

        for msg in messages:
            if isinstance(msg, HumanMessage):
                content = msg.content.lower()
                # Simple keyword extraction (can be enhanced with NLP)
                if any(hero in content for hero in ["layla", "miya", "moskov", "granger", "bruno"]):
                    for hero in ["layla", "miya", "moskov", "granger", "bruno"]:
                        if hero in content:
                            mentioned_heroes.add(hero.capitalize())

                if "marksman" in content or "mm" in content:
                    mentioned_roles.add("Marksman")

        context["mentioned_heroes"] = list(mentioned_heroes)
        context["mentioned_roles"] = list(mentioned_roles)

        return context

    def _serialize_messages(self, messages: List[BaseMessage]) -> List[Dict]:
        """Serialize messages for storage."""
        serialized = []
        for msg in messages:
            msg_dict = {
                "type": msg.__class__.__name__,
                "content": msg.content
            }
            serialized.append(msg_dict)
        return serialized

    def _deserialize_messages(self, messages_data: List[Dict]) -> List[BaseMessage]:
        """Deserialize messages from storage."""
        messages = []
        for msg_data in messages_data:
            msg_type = msg_data["type"]
            content = msg_data["content"]

            if msg_type == "HumanMessage":
                messages.append(HumanMessage(content=content))
            elif msg_type == "AIMessage":
                messages.append(AIMessage(content=content))

        return messages


# Global instance
_session_manager: Optional[SessionManager] = None


def get_session_manager() -> SessionManager:
    """Get global session manager instance."""
    global _session_manager
    if _session_manager is None:
        _session_manager = SessionManager()
    return _session_manager
