from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config import settings
from models.database import engine, Base
from models import user, session  # Import models so Base.metadata.create_all knows about them

# Create database tables if they don't exist yet
Base.metadata.create_all(bind=engine)

# Import slowapi tools
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from security.rate_limiter import limiter, rate_limit_exceeded_handler

app = FastAPI(
    title="ML-Guardian",
    version="1.0.0",
    description="Secure Multi-Agent AI System API"
)

# Wire up the rate limiter to the FastAPI app
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)

# Set up CORS (Cross-Origin Resource Sharing)
# This allows the React frontend to communicate with this backend API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from auth.router import router as auth_router
from routers.chat import router as chat_router

# Include the routers
app.include_router(auth_router)
app.include_router(chat_router)

@app.get("/")
def read_root():
    return {"message": f"Welcome to Agentic ML API"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}