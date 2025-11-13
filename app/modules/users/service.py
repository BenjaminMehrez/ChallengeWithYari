from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from typing import List, Optional
from .models import User
from .schemas import Pokemon, UserCreate, UserUpdate
from .repository import UserRepository
from app.core.security import get_password_hash
from uuid import UUID
from app.modules.pokemon.service import PokeAPIService


class UserService:
    """
    Business logic layer for users.
    Coordinates operations between the controller and the repository.
    """

    def __init__(self, db: Session):
        self.db = db
        self.repository = UserRepository(db)
        self.pokeapi_service = PokeAPIService()

    
    ### ------- Pokemon API

    async def add_pokemon_to_user(self, user_id: UUID, pokemon_id: int) -> User:
        user = self.repository.get_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with id {user_id} not found"
            )

        try:
            pokemon_data = await self.pokeapi_service.get_pokemon(pokemon_id)
        except HTTPException:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Pokémon with id {pokemon_id} not found in PokeAPI"
            )


        if any(p["id"] == pokemon_id for p in user.pokemons):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Pokemon {pokemon_data['name']} already in collection"
            )

        user.pokemons.append(pokemon_data)
        
        ### Esto es porque SQLAlchemy no detecta automaticamente los cambios JSON/ARRAY
        from sqlalchemy.orm.attributes import flag_modified
        flag_modified(user, "pokemons")

        return self.repository.update(user)

    def remove_pokemon_from_user(self, user_id: UUID, pokemon_id: int) -> User:
        user = self.repository.get_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with id {user_id} not found"
            )

        original_length = len(user.pokemons)
        user.pokemons = [p for p in user.pokemons if p["id"] != pokemon_id]
        
        if len(user.pokemons) == original_length:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Pokemon with id {pokemon_id} not found in collection"
            )

        from sqlalchemy.orm.attributes import flag_modified
        flag_modified(user, "pokemons")

        return self.repository.update(user)

    def get_user_pokemons(self, user_id: UUID) -> List[Pokemon]:
        user = self.repository.get_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with id {user_id} not found"
            )
        return user.pokemons

    def update_user_pokemons(self, user_id: UUID, pokemons: List[Pokemon]) -> User:
        user = self.repository.get_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with id {user_id} not found"
            )
        pokemon_ids = [p.id for p in pokemons]
        if len(pokemon_ids) != len(set(pokemon_ids)):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Duplicate Pokemon in list"
            )

        user.pokemons = [p.model_dump() for p in pokemons]

        from sqlalchemy.orm.attributes import flag_modified
        flag_modified(user, "pokemons")

        return self.repository.update(user)

    ### --- User

    def get_all_users(self, skip: int = 0, limit: int = 100) -> List[User]:
        return self.repository.get_all(skip=skip, limit=limit)

    def get_active_users(self, skip: int = 0, limit: int = 100) -> List[User]:
        return self.repository.get_active_users(skip=skip, limit=limit)

    def get_user_by_id(self, user_id: UUID) -> Optional[User]:
        user = self.repository.get_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with id {user_id} not found"
            )
        return user

    def get_user_by_email(self, email: str) -> Optional[User]:
        user = self.repository.get_by_email(email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with email: {email} not found"
            )
        return user

    def get_user_username(self, username: str) -> Optional[User]:
        user = self.repository.get_by_username(username)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with username: {username} not found"
            )
        return user

    def search_users(self, search_term: str, skip: int = 0, limit: int = 100) -> Optional[User]:
        return self.repository.search_by_name(search_term, skip=skip, limit=limit)

    def create_user(self, user_data: UserCreate) -> User:

        # Verify email already exist
        if self.repository.exists_by_email(user_data.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )

        # Verify username already exist
        if self.repository.exists_by_username(user_data.username):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken"
            )

        # Verify requery password
        if len(user_data.password) < 8:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password must be at least 8 characters long"
            )

        hashed_password = get_password_hash(user_data.password)
        db_user = User(
            email=user_data.email,
            username=user_data.username,
            hashed_password=hashed_password,
            is_active=True,
            is_superuser=False,
        )

        # Save on Database
        return self.repository.create(db_user)

    def update_user(self, user_id: UUID, user_data: UserUpdate) -> User:
        db_user = self.repository.get_by_id(user_id)
        if not db_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        # Verify email unique
        if user_data.email and user_data.email != db_user.email:
            if self.repository.exists_by_email(user_data.email):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already in use"
                )
            db_user.email = user_data.email

        # Verify username unique
        if user_data.username and user_data.username != db_user.username:
            if self.repository.exists_by_username(user_data.username):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Username already in use"
                )
            db_user.username = user_data.username

        if user_data.password:
            if len(user_data.password) < 8:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Password must be at least 8 characters long"
                )
            db_user.hashed_password = get_password_hash(user_data.password)

        if user_data.is_active is not None:
            db_user.is_active = user_data.is_active

        # Save Changes
        return self.repository.update(db_user)

    def delete_user(self, user_id: UUID) -> bool:
        db_user = self.repository.get_by_id(user_id)
        if not db_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        # Dont permit delete superuser
        if db_user.is_superuser:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot delete superuser accounts"
            )

        return self.repository.delete(db_user)

    def deactivate_user(self, user_id: UUID) -> User:
        db_user = self.repository.get_by_id(user_id)
        if not db_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        db_user.is_active = False
        return self.repository.update(db_user)

    def activate_user(self, user_id: UUID) -> User:
        db_user = self.repository.get_by_id(user_id)
        if not db_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        db_user.is_active = True
        return self.repository.update(db_user)

    def get_user_statistics(self) -> dict:
        return {
            "total_users": self.repository.count_all(),
            "active_users": self.repository.count_active(),
            "inactive_users": self.repository.count_all() - self.repository.count_active()
        }
