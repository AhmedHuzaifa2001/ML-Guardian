import sys
from pathlib import Path

# Add backend directory to path so we can run this file directly
backend_dir = str(Path(__file__).resolve().parent.parent)
if backend_dir not in sys.path:
    sys.path.append(backend_dir)

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from models.database import Base

class ChatSession(Base):
    __tablename__ = "chat_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    # Store the user's original prompt
    user_query = Column(String, nullable=False)
    
    # Store the intent classified by the Orchestrator
    intent = Column(String, nullable=False)
    
    # Store the final agentic response (which might include ML recommendations, risk audits, etc.)
    # We use JSON so we can easily store the structured data
    agent_response = Column(JSON, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Establish a relationship back to the User model
    # (Note: we will need to update the User model to include a back_populates="chats" if we want bi-directional querying)
    owner = relationship("User")
