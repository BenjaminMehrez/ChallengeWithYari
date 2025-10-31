from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from typing import Optional
from datetime import timedelta

from app.modules.users.repository import UserRepository
from app.modules.users.models import User
from app.core.security import verify_password, create_access_token, get_settings

settings = get_settings()

class AuthService:
  """
  Business logic layer for authentication.
  Handles login, token generation, and credential verification.
  """
  def __init__(self, db: Session):
    self.db = db
    self.user_repository = UserRepository(db)

  def authenticate_user(self, email: str, password: str) -> Optional[User]:
    """
    Authenticate user by email and password.
    Returns User if credentials are valid, None otherwise.
    """
    user = self.user_repository.get_by_email(email)

    if not user:
      return None

    if not user.is_active:
      raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="User account is inactive"
      )

    if not verify_password(password, user.hashed_password):
      return None

    return user

  def create_access_token_for_user(self, user: User) -> str:
    """
    Generate JWT access token for authenticated user.
    """
    access_token = create_access_token(
      data={"sub": str(user.id)},
      expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    return access_token