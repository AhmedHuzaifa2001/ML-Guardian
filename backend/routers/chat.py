import sys
from pathlib import Path

# Add backend directory to path
backend_dir = str(Path(__file__).resolve().parent.parent)
if backend_dir not in sys.path:
    sys.path.append(backend_dir)

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from pydantic import BaseModel

# Import our dependencies, database, and models
from auth.dependencies import get_current_user
from models.database import get_db
from models.session import ChatSession
from models.user import User

# Import the LangGraph workflow and Risk Passport generator
from agents.workflow import run_workflow
from risk_passport.generator import passport_generator

# Rate limiter setup
from security.rate_limiter import limiter, RATE_LIMIT

router = APIRouter(
    prefix="/api/chat",
    tags=["Chat & Agents"]
)

# Pydantic model for what the user sends us
class ChatRequest(BaseModel):
    message: str

@router.post("/")
@limiter.limit(RATE_LIMIT)
def send_chat_message(
    request: Request, # Required for rate limiter
    chat_request: ChatRequest, 
    current_user: User = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    """
    Main endpoint for chatting with ML-Guardian.
    Passes the user's message through the LangGraph agents and returns an ML Risk Passport.
    Requires JWT Authentication and is Rate Limited.
    """
    
    # 1. Send the message through the LangGraph Agentic Pipeline
    # (This automatically handles prompt injection, PII masking, routing, RAG, and AI generation)
    raw_workflow_result = run_workflow(chat_request.message)
    
    # Check if the security layer blocked it completely
    if raw_workflow_result.get("status") == "blocked":
        raise HTTPException(status_code=400, detail=raw_workflow_result.get("message", "Security Block"))

    # 2. Format the raw output into a beautiful ML Risk Passport
    formatted_passport = passport_generator.generate_passport(
        workflow_result=raw_workflow_result, 
        user_name=current_user.username
    )
    
    # 3. Save the conversation to the PostgreSQL database
    new_chat_session = ChatSession(
        user_id=current_user.id,
        user_query=chat_request.message,
        intent=formatted_passport.get("query_intent", "UNKNOWN"),
        agent_response=formatted_passport
    )
    db.add(new_chat_session)
    db.commit()
    db.refresh(new_chat_session)
    
    # 4. Return the formatted passport to the user/frontend
    return formatted_passport

@router.get("/history")
def get_chat_history(
    current_user: User = Depends(get_current_user), 
    db: Session = Depends(get_db),
    limit: int = 10
):
    """
    Retrieves the logged-in user's past chat history (up to 'limit' items).
    """
    history = db.query(ChatSession)\
                .filter(ChatSession.user_id == current_user.id)\
                .order_by(ChatSession.created_at.desc())\
                .limit(limit)\
                .all()
    
    return {"history": history}
