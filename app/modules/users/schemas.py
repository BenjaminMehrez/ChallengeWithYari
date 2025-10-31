from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime
from uuid import UUID
from app.modules.pokemon.shemas import Pokemon


# Base Schema
class UserBase(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)


# Schema Create User
class UserCreate(UserBase):
    password: str = Field(..., min_length=8)


# Schema Update User
class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None
    pokemons: Optional[List[Pokemon]] = None


# Schema to Response
class UserResponse(UserBase):
    id: UUID
    is_active: bool
    is_superuser: bool
    pokemons: List[Pokemon] = []
    created_at: datetime
    updated_at: datetime
