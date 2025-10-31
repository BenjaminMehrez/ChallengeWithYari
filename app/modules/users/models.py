from sqlalchemy import Column, String, Boolean, DateTime, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.core.database import Base
import uuid


class User(Base):
  __tablename__ = "users"


  id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
  email = Column(String, unique=True, index=True, nullable=False)
  username = Column(String, unique=True, index=True, nullable=False)
  hashed_password = Column(String, nullable=False)

  pokemons = Column(JSON, default=list, nullable=False)

  is_active = Column(Boolean, default=False)
  is_superuser = Column(Boolean, default=False)
  created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
  updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

  def __repr__(self):
    return f"<User(email='{self.email}', full_name='{self.username}')>"