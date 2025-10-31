from fastapi import APIRouter, Depends
from app.modules.pokemon.shemas import Pokemon
from .service import PokeAPIService


router = APIRouter(
    prefix="/api/v1/pokemon",
    tags=["pokemon"]
)


def get_pokemon_service() -> PokeAPIService:
    return PokeAPIService()


@router.get("/{pokemon_id}", response_model=Pokemon)
async def get_pokemon(pokemon_id: int, service: PokeAPIService = Depends(get_pokemon_service)) -> Pokemon:
    return await service.get_pokemon(pokemon_id)


@router.get("/name/{name}", response_model=Pokemon)
async def get_pokemon_by_name(name: str, service: PokeAPIService = Depends(get_pokemon_service)) -> Pokemon:
    return await service.get_pokemon_by_name(name)
