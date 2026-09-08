import jwt
from datetime import datetime, timedelta, timezone
from config import settings

def create_access_token(data: dict) -> str:
    """Create a new JWT access token."""
    to_encode = data.copy()
    
    # Calculate expiration time
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    
    # Generate the JWT token string
    encoded_jwt = jwt.encode(
        to_encode, 
        settings.JWT_SECRET_KEY, 
        algorithm=settings.JWT_ALGORITHM
    )
    
    return encoded_jwt

def decode_access_token(token: str) -> dict:
    """Decode and verify a JWT access token."""
    try:
        decoded_token = jwt.decode(
            token, 
            settings.JWT_SECRET_KEY, 
            algorithms=[settings.JWT_ALGORITHM]
        )
        return decoded_token
    except jwt.ExpiredSignatureError:
        return None  # Token has expired
    except jwt.PyJWTError:
        return None  # Token is invalid
