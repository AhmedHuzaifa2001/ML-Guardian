from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr

from models.database import get_db
from models.user import User
from auth.password import get_password_hash, verify_password
from auth.jwt_handler import create_access_token

router = APIRouter(prefix="/api/auth", tags=["Authentication"])

# --- Pydantic Schemas for Request/Response validation ---
class UserCreate(BaseModel):
    email: EmailStr
    username: str
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str


# --- Endpoints ---

@router.post("/register", response_model=dict)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    # Check if user already exists
    db_user = db.query(User).filter((User.email == user.email) | (User.username == user.username)).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email or Username already registered")

    # Hash the password
    hashed_pwd = get_password_hash(user.password)

    # Create new database user
    new_user = User(
        email=user.email,
        username=user.username,
        hashed_password=hashed_pwd
    )
    
    # Save to database
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {"message": "User registered successfully", "user_id": new_user.id}


@router.post("/login", response_model=Token)
def login_user(user: UserLogin, db: Session = Depends(get_db)):
    # Find user by email
    db_user = db.query(User).filter(User.email == user.email).first()
    
    # Check if user exists and password matches
    if not db_user or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Generate JWT token
    access_token = create_access_token(data={"sub": str(db_user.id), "role": db_user.role})

    return {"access_token": access_token, "token_type": "bearer"}
