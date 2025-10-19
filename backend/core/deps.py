from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from .db import get_db
from .security import verify_token
from models.users import User
security = HTTPBearer()

def get_current_user(credentials: HTTPAuthorizationCredentials=Depends(security), db: Session=Depends(get_db)) -> User:
    token = credentials.credentials
    payload = verify_token(token)
    if payload is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid authentication credentials', headers={'WWW-Authenticate': 'Bearer'})
    email: str = payload.get('sub')
    if email is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid authentication credentials', headers={'WWW-Authenticate': 'Bearer'})
    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='User not found', headers={'WWW-Authenticate': 'Bearer'})
    return user

def get_current_active_user(current_user: User=Depends(get_current_user)) -> User:
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail='Inactive user')
    return current_user
