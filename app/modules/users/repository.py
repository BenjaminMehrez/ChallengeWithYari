from sqlalchemy.orm import Session
from typing import List, Optional
from .models import User
from uuid import UUID


class UserRepository:
  """ CRUD Operetion with DataBase  """
  def __init__(self, db: Session):
    self.db = db


  def get_all(self, skip: int = 0, limit: int = 100) -> List[User]:
    return self.db.query(User).offset(skip).limit(limit).all()

  def get_by_id(self, user_id: UUID) -> Optional[User]:
    return self.db.query(User).filter(User.id == user_id).first()

  def get_by_email(self, email: str) -> Optional[User]:
    return self.db.query(User).filter(User.email == email).first()

  def get_by_username(self, username: str) -> Optional[User]:
    return self.db.query(User).filter(User.username == username).first()

  def get_active_users(self, skip: int = 0, limit: int = 100) -> Optional[User]:
    return self.db.query(User).filter(User.is_active == True).offset(skip).limit(limit).all()

  def get_superuser(self) -> List[User]:
    return self.db.query(User).filter(User.is_superuser == True).all()

  def create(self, user: User) -> User:
    self.db.add(user)
    self.db.commit()
    self.db.refresh(user)
    return user
  
  def update(self, user: User) -> User:
    self.db.commit()
    self.db.refresh(user)
    return user

  def delete(self, user: User) -> bool:
    self.db.delete(user)
    self.db.commit()
    return True

  def exists_by_email(self, email: str) -> bool:
    return self.db.query(User).filter(User.email == email).first() is not None

  def exists_by_username(self, username: str) -> bool:
    return self.db.query(User).filter(User.username == username).first() is not None
  
  def count_all(self) -> int:
    return self.db.query(User).count()

  def count_active(self) -> int:
    return self.db.query(User).filter(User.is_active == True).count()

  def search_by_name(self, search_term: str, skip: int = 0, limit: int = 100) -> List[User]:
    search = f"%{search_term}%"
    return self.db.query(User).filter(User.username.ilike(search)).offset(skip).limit(limit).all()