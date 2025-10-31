from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.modules.auth.schema import LoginRequest, Token
from app.core.database import get_db
from .service import AuthService
from .dependencies import get_current_user
from app.modules.users.models import User
from app.modules.users.schemas import UserResponse

router = APIRouter(
  prefix="/api/v1/auth",
  tags=["authentication"]
)

@router.post("/login", response_model=Token)
def login(credentials: LoginRequest, db: Session = Depends(get_db)):
  auth_service = AuthService(db)
  
  user = auth_service.authenticate_user(
    credentials.email,
    credentials.password
  )

  if not user:
    raise HTTPException(
      status_code=status.HTTP_401_UNAUTHORIZED,
      detail="Incorrect email or password",
      headers={"WWW-Authenticate": "Bearer"},
    )

  access_token = auth_service.create_access_token_for_user(user)
  
  return {
    "access_token": access_token,
    "token_type": "bearer"
  }

@router.get("/me", response_model=UserResponse)
def get_current_user_info(current_user: User = Depends(get_current_user)):
  return current_user