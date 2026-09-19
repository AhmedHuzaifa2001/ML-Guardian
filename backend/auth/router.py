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


from fastapi.security import OAuth2PasswordRequestForm

@router.post("/login", response_model=Token)
def login_user(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    # Find user by email or username (Swagger uses the 'username' field for whatever the user types)
    db_user = db.query(User).filter(
        (User.email == form_data.username) | (User.username == form_data.username)
    ).first()
    
    # Check if user exists and password matches
    if not db_user or not verify_password(form_data.password, db_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username/email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Generate JWT token with the username as the subject (required by dependencies.py)
    access_token = create_access_token(data={"sub": db_user.username, "role": db_user.role})

    return {"access_token": access_token, "token_type": "bearer"}
