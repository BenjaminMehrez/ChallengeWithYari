from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from uuid import UUID

from app.core.database import get_db
from app.core.security import verify_token, security
from app.modules.users.repository import UserRepository
from app.modules.users.models import User


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)) -> User:
  # Get token
  token = credentials.credentials

  # Verify and decode token
  payload = verify_token(token)
  user_id_str: str = payload.get("sub")

  if user_id_str is None:
    raise HTTPException(
      status_code=status.HTTP_401_UNAUTHORIZED,
      detail="Invalid authentication credentials",
      headers={"WWW-Authenticate": "Bearer"}
    )

  # Parse user ID
  try:
    user_id = UUID(user_id_str)
  except ValueError:
    raise HTTPException(
      status_code=status.HTTP_401_UNAUTHORIZED,
      detail="Invalid user ID format",
      headers={"WWW-Authenticate": "Bearer"}
    )
  
  # Get user from database
  user_repository = UserRepository(db)
  user = user_repository.get_by_id(user_id)

  if user is None:
    raise HTTPException(
      status_code=status.HTTP_401_UNAUTHORIZED,
      detail="User not found",
      headers={"WWW-Authenticate": "Bearer"}
    )

  return user


def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
  if not current_user.is_active:
    raise HTTPException(
      status_code=status.HTTP_403_FORBIDDEN,
      detail="Inactive user account"
    )
  return current_user


def require_superuser(current_user: User = Depends(get_current_user)) -> User:
  if not current_user.is_superuser:
    raise HTTPException(
      status_code=status.HTTP_403_FORBIDDEN,
      detail="Not enough permissions. Superuser access required."
    )
  return current_user