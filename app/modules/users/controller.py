from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from .schemas import Pokemon, UserCreate, UserUpdate, UserResponse
from .service import UserService
from ..auth.dependencies import get_current_user
from ...core.config import get_settings
from .models import User

settings = get_settings()
router = APIRouter(
    prefix="/api/v1/users",
    tags=["users"]
)



### ------- User


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    user_service = UserService(db)
    return user_service.create_user(user)


@router.get("/", response_model=List[UserResponse])
def get_users(
    skip: int = 0,
    limit: int = 100,
    active_only: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    user_service = UserService(db)
    if active_only:
        return user_service.get_active_users(skip=skip, limit=limit)
    return user_service.get_all_users(skip=skip, limit=limit)


@router.get("/{user_id}", response_model=UserResponse)
def get_user(
    user_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    user_service = UserService(db)
    return user_service.get_user_by_id(user_id)


@router.get("/statistics")
def get_statistics(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    user_service = UserService(db)
    return user_service.get_user_statistics()


@router.get("/search/", response_model=List[UserResponse])
def search_users(
    q: str = Query(..., min_length=1, description="Search term"),
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user)
):
    user_service = UserService(db)
    return user_service.search_users(q, skip=skip, limit=limit)


@router.put("/{user_id}", response_model=UserResponse)
def update_user(
    user_id: UUID,
    user_data: UserUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    if current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )

    user_service = UserService(db)
    return user_service.update_user(user_id, user_data)


@router.patch("/{user_id}/deactivate", response_model=UserResponse)
def deactivate_user(
    user_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only superusers can deactivate"
        )

    user_service = UserService(db)
    return user_service.deactivate_user(user_id)


@router.patch("/{user_id}/activate", response_model=UserResponse)
def activate_user(
    user_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only superusers can deactivate"
        )

    user_service = UserService(db)
    return user_service.activate_user(user_id)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.id != user_id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )

    user_service = UserService(db)
    user_service.delete_user(user_id)
    return None



### -------- Poke API

@router.get("/{user_id}/pokemons", response_model=List[Pokemon])
def get_user_pokemons(user_id: UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )

    user_service = UserService(db)
    return user_service.get_user_pokemons(user_id)


@router.post("/{user_id}/pokemons/{pokemon_id}", response_model=UserResponse)
async def add_pokemon_to_user(user_id: UUID, pokemon_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only add Pokémon to your own collection"
        )
    user_service = UserService(db)
    return await user_service.add_pokemon_to_user(user_id, pokemon_id)
    

@router.put("/{user_id}/pokemons", response_model=UserResponse)
def update_user_pokemons(user_id: UUID, pokemons: List[Pokemon], db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):

    if current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only add Pokémon to your own collection"
        )

    user_service = UserService(db)
    return user_service.update_user_pokemons(user_id, pokemons)


@router.delete("/{user_id}/pokemons/{pokemon_id}", response_model=UserResponse)
def remove_pokemon_from_user(user_id: UUID, pokemon_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only remove Pokémon to your own collection"
        )
    user_service = UserService(db)
    return user_service.remove_pokemon_from_user(user_id, pokemon_id)