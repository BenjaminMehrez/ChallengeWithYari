import httpx
from typing import Optional, Dict
from fastapi import HTTPException, status
from app.core.config import Settings
from app.modules.pokemon.shemas import Pokemon

settings = Settings()


class PokeAPIService:

    BASE_URL = settings.API_POKEMON
    TIMEOUT = 10.0

    def __init__(self):
        self.limits = httpx.Limits(
            max_keepalive_connections=5,
            max_connections=10
        )

    async def _make_request(self, endpoint: str, params: Optional[Dict] = None) -> Dict:
        async with httpx.AsyncClient(
            timeout=self.TIMEOUT,
            limits=self.limits
        ) as client:
            try:
                response = await client.get(
                    f"{self.BASE_URL}/{endpoint}",
                    params=params or {}
                )
                response.raise_for_status()
                return response.json()
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 404:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"Resource not found: {endpoint}"
                    )

                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Resource not found: {endpoint}"
                )

            except httpx.TimeoutException:
                raise HTTPException(
                    status_code=status.HTTP_504_GATEWAY_TIMEOUT,
                    detail=f"PokeAPI request timed out"
                )

            except httpx.RequestError as e:
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail=f"Could not connect to PokeAPI: {str(e)}"
                )

    async def get_pokemon(self, pokemon_id: int) -> Pokemon:
        if pokemon_id < 1 or pokemon_id > 1025:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Pokemon ID must be between 1 and 1025"
            )

        result = await self._make_request(f"pokemon/{pokemon_id}")

        pokemon = {
            "id": result["id"],
            "name": result['name']
        }

        return pokemon

    async def get_pokemon_by_name(self, name: str) -> Pokemon:
        result = await self._make_request(f"pokemon/{name.lower()}")

        pokemon = {
            "id": result["id"],
            "name": result['name']
        }

        return pokemon
