## Member 2's security role (preventing data/password leakage).

import bcrypt

def get_password_hash(password: str) -> str:
    """Hash a plaintext password using bcrypt."""
    # Generate a salt and hash the password
    pwd_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt() ## a unique, random string of characters called a "salt"
    hashed_password = bcrypt.hashpw(password=pwd_bytes, salt=salt)
    
    # Return the hashed password as a string
    return hashed_password.decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Check if a plaintext password matches the hashed password."""
    password_byte_enc = plain_password.encode('utf-8')
    hashed_password_byte_enc = hashed_password.encode('utf-8')
    
    return bcrypt.checkpw(password=password_byte_enc, hashed_password=hashed_password_byte_enc)


## by hashing passwords, you ensure that even if an 
# attacker gains access to your PostgreSQL database, 
# they cannot read the actual plaintext passwords.