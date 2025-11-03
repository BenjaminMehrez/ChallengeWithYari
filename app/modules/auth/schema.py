from pydantic import BaseModel, EmailStr
from typing import Optional
from uuid import UUID

# Schema to Login
class LoginRequest(BaseModel):
  email: EmailStr
  password: str

# Schema to Token
class Token(BaseModel):
  access_token: str
  token_type: str

class TokenData(BaseModel):
  user_id: Optional[UUID] = None

  def get_uuid(self) -> UUID | None:
      if self.user_id:
        return UUID(self.user_id)
      return None